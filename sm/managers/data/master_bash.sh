#!/bin/bash

# NOTE about this bash file: this file will be used to setup the distributed
# computing cluster on OpenStack. This includes copying the actual application
# frameworks from an external cinder volume to each master/slave and writing
# the configuration files to each of them. The parameters within dollar signs
# (e.g. $homedir$) will be filled by the service orchestrator (so.py) with
# either given values from the user, default settings either from file
# defaultSettings.cfg / assumptions within the serice orchestrator or with
# pre-defined configuration files within the /data directory of the SO bundle.

{
SECONDS=0
# disable IPv6 as Hadoop won't run on a system with it activated
echo "disabling IPv6" >> $homedir$/deployment.log
echo -e "\nnet.ipv6.conf.all.disable_ipv6 = 1\nnet.ipv6.conf.default.disable_ipv6 = 1\nnet.ipv6.conf.lo.disable_ipv6 = 1" >> /etc/sysctl.conf
sysctl -p

# setup master's SSH configuration
su $username$ -c 'echo -e "$master.id_rsa$" > $homedir$/.ssh/id_rsa'
su $username$ -c 'echo -e "$master.id_rsa.pub$" > $homedir$/.ssh/id_rsa.pub'
$insert_master_pub_key$
su $username$ -c 'echo -e "Host *\n   StrictHostKeyChecking no\n   UserKnownHostsFile=/dev/null" > $homedir$/.ssh/config'
chmod 0600 $homedir$/.ssh/*

# copying Hadoop & Java on the master and install them (including setting the
# environment variables)
cd /root
# disk has to be mounted by ID as the virtual disk device in the /dev folder
# can be different with every restart
mount -o ro /dev/disk/by-id/$disk_id$ /mnt/

mkdir $homedir$/archives

echo "setting up files for deployment on slaves..." >> $homedir$/deployment.log

cat - >> /root/bashrc.suffix <<'EOF'
export JAVA_HOME=/usr/lib/java/jdk
export PATH=$PATH:$JAVA_HOME/bin
export HADOOP_HOME=/usr/lib/hadoop/hadoop
export PATH=$PATH:$HADOOP_HOME/bin
EOF

# configure Hadoop
# first of all, let's create the config files for the slaves
mkdir $homedir$/hadoopconf
mv /root/bashrc.suffix $homedir$/hadoopconf

# creating /etc/hosts file's replacement - don't forget: slaves need to have
# the same name as configured with Heat Template!!!
echo -e "127.0.0.1\tlocalhost\n`/sbin/ifconfig eth0 | grep 'inet addr' | cut -d: -f2 | awk '{print $1}'`  $masternode$" > /root/hosts.replacement
cat - >> /root/hosts.replacement <<'EOF'
$hostsfilecontent$
EOF
mv -f /root/hosts.replacement $homedir$/hadoopconf


# create yarn-site.xml:
cat - > $homedir$/hadoopconf/yarn-site.xml << 'EOF'
$yarn-site.xml$
EOF

# create core-site.xml:
cat - > $homedir$/hadoopconf/core-site.xml << 'EOF'
$core-site.xml$
EOF

# create mapred-site.xml:
cat - >> $homedir$/hadoopconf/mapred-site.xml << 'EOF'
$mapred-site.xml$
EOF

# create hdfs-site.xml: (here, replication factor has to be entered!!!)
cat - >> $homedir$/hadoopconf/hdfs-site.xml << 'EOF'
$hdfs-site.xml$
EOF

# create hadoop-env.sh:
cat - >> $homedir$/hadoopconf/hadoop-env.sh << 'EOF'
$hadoop-env.sh$
EOF

# copy pssh/pscp to /usr/bin/pssh on master
# originally from Git repo https://github.com/jcmcken/parallel-ssh
cp -r /mnt/pssh/pssh /usr/bin/
cat - > $homedir$/hosts.lst << 'EOF'
127.0.0.1
$for_loop_slaves$
EOF


function transferFirstUnpackLater {
	# copying hadoop & jdk to slaves in a compact form and unpacking them on
	# the slaves
	echo "copying hadoop and jdk to slaves" >> $homedir$/deployment.log
	su $username$ -c "/usr/bin/pssh/bin/pscp -h $homedir$/hosts.lst /mnt/{hadoop/hadoop-2.7.1.tar.gz,java/jdk-8u60-linux-x64.tar.gz} $homedir$"
	echo "unpacking hadoop" >> $homedir$/deployment.log
	su $username$ -c "/usr/bin/pssh/bin/pssh -t 2000 -h $homedir$/hosts.lst \"tar -xzf $homedir$/hadoop-2.7.1.tar.gz\""
	echo "unpacking jdk" >> $homedir$/deployment.log
	su $username$ -c "/usr/bin/pssh/bin/pssh -t 2000 -h $homedir$/hosts.lst \"tar -xzf $homedir$/jdk-8u60-linux-x64.tar.gz\""
	echo "setting up both" >> $homedir$/deployment.log
	# done with copying/unpacking hadoop/jdk
}

function transferUnpackedFiles {
	# in this scenario, hadoop/jdk will be transferred to the slaves in an
	# unpacked form
	echo "copying hadoop and jdk to slaves" >> $homedir$/deployment.log
	su $username$ -c "/usr/bin/pssh/bin/pscp -r -h $homedir$/hosts.lst /mnt/{hadoop/hadoop-2.7.1,java/jdk1.8.0_60} $homedir$"
	# done with transfer
}

# here, the script has to decide which function to call:
# transferFirstUnpackLater or transferUnpackedFiles
echo "transferring hadoop & jdk to the masters/slaves and unpacking them" >> $homedir$/deployment.log
$transfer_method$

# the mounted volume isn't needed anymore - for security's sake, it will be
# unmounted
umount /mnt 

echo "setting up hadoop & jdk" >> $homedir$/deployment.log
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo mkdir /usr/lib/hadoop\""
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo mv $homedir$/hadoop-2.7.1 /usr/lib/hadoop\""
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo ln -s /usr/lib/hadoop/hadoop-2.7.1 /usr/lib/hadoop/hadoop\""
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo mv /usr/lib/hadoop/hadoop-2.7.1/etc/hadoop/ /etc/\""
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo mkdir -p /usr/lib/java\""
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo mv $homedir$/jdk1.8.0_60/ /usr/lib/java/\""
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo ln -s /usr/lib/java/jdk1.8.0_60/ /usr/lib/java/jdk\""
su $username$ -c "/usr/bin/pssh/bin/pscp -h $homedir$/hosts.lst $homedir$/hadoopconf/bashrc.suffix $homedir$"
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo sh -c \\\"cat $homedir$/bashrc.suffix >> /etc/bash.bashrc\\\"\""

# now, let's copy the files to the slaves
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo mkdir -p /app/hadoop/tmp\""
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo chown $username$:$usergroup$ /app/hadoop/tmp\""
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo chmod 750 /app/hadoop/tmp\""
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo chown -R $username$:$usergroup$ /etc/hadoop\""

# the file has to be copied into the user directory as $username$ doesn't have
# permissions to write into /etc/hadoop
echo "copying config files from master to slave..." >> $homedir$/deployment.log
su $username$ -c "/usr/bin/pssh/bin/pscp -h $homedir$/hosts.lst $homedir$/hadoopconf/core-site.xml $homedir$"
# move file to its final location (/etc/hadoop)
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo mv -f $homedir$/core-site.xml /etc/hadoop\""

su $username$ -c "/usr/bin/pssh/bin/pscp -h $homedir$/hosts.lst $homedir$/hadoopconf/{{mapred,hdfs,yarn}-site.xml,hadoop-env.sh} /etc/hadoop"

su $username$ -c "/usr/bin/pssh/bin/pscp -h $homedir$/hosts.lst $homedir$/hadoopconf/hosts.replacement $homedir$"
su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"sudo mv -f $homedir$/hosts.replacement /etc/hosts\""

su $username$ -c "/usr/bin/pssh/bin/pssh -h $homedir$/hosts.lst \"ln -s /etc/hadoop /usr/lib/hadoop/hadoop-2.7.1/etc/hadoop\""


# set master and slave nodes
echo $masternode$ > /etc/hadoop/masters
cat - > /etc/hadoop/slaves << 'EOF'
$masternodeasslave$$slavesfile$
EOF
source /etc/hadoop/hadoop-env.sh
su $username$ -c "/usr/lib/hadoop/hadoop/bin/hdfs namenode -format"
su $username$ -c "/usr/lib/hadoop/hadoop/sbin/start-dfs.sh"
su $username$ -c "/usr/lib/hadoop/hadoop/sbin/start-yarn.sh"
echo "hadoop cluster ready" >> $homedir$/deployment.log
duration=$SECONDS
echo "deployment took me $duration seconds"

# in the following line, the whole regular output will be redirected to the
# file debug.log in the user's home directory and the error output to the file
# error.log within the same directory
} 2> $homedir$/error.log | tee $homedir$/debug.log
