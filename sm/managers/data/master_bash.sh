#!/bin/bash

# NOTE about this bash file: this file will be used to setup the distributed
# computing cluster on OpenStack. This includes copying the actual application
# frameworks from an external cinder volume to each master/slave and writing
# the configuration files to each of them. The parameters within dollar signs
# (e.g. /home/ubuntu) will be filled by the service orchestrator (so.py) with
# either given values from the user, default settings either from file
# defaultSettings.cfg / assumptions within the serice orchestrator or with
# pre-defined configuration files within the /data directory of the SO bundle.

{
SECONDS=0
# disable IPv6 as Hadoop won't run on a system with it activated
echo "disabling IPv6" >> /home/ubuntu/deployment.log
echo -e "\nnet.ipv6.conf.all.disable_ipv6 = 1\nnet.ipv6.conf.default.disable_ipv6 = 1\nnet.ipv6.conf.lo.disable_ipv6 = 1" >> /etc/sysctl.conf
sysctl -p

# setup master's SSH configuration
su ubuntu -c 'echo -e "$master.id_rsa$" > /home/ubuntu/.ssh/id_rsa'
su ubuntu -c 'echo -e "$master.id_rsa.pub$" > /home/ubuntu/.ssh/id_rsa.pub'
$insert_master_pub_key$
su ubuntu -c 'echo -e "Host *\n   StrictHostKeyChecking no\n   UserKnownHostsFile=/dev/null" > /home/ubuntu/.ssh/config'
chmod 0600 /home/ubuntu/.ssh/*

# copying Hadoop & Java on the master and install them (including setting the
# environment variables)
cd /root

mkdir /home/ubuntu/archives

echo "setting up files for deployment on slaves..." >> /home/ubuntu/deployment.log

cat - >> /root/bashrc.suffix <<'EOF'
export JAVA_HOME=/usr/lib/java/jdk
export PATH=$PATH:$JAVA_HOME/bin
export HADOOP_HOME=/usr/lib/hadoop/hadoop
export PATH=$PATH:$HADOOP_HOME/bin
EOF

# configure Hadoop
# first of all, let's create the config files for the slaves
mkdir /home/ubuntu/hadoopconf
mv /root/bashrc.suffix /home/ubuntu/hadoopconf

# creating /etc/hosts file's replacement - don't forget: slaves need to have
# the same name as configured with Heat Template!!!
echo -e "127.0.0.1\tlocalhost\n`/sbin/ifconfig eth0 | grep 'inet addr' | cut -d: -f2 | awk '{print $1}'`  $masternode$" > /root/hosts.replacement
cat - >> /root/hosts.replacement <<'EOF'
$hostsfilecontent$
EOF
mv -f /root/hosts.replacement /home/ubuntu/hadoopconf


# create yarn-site.xml:
cat - > /home/ubuntu/hadoopconf/yarn-site.xml << 'EOF'
$yarn-site.xml$
EOF

# create core-site.xml:
cat - > /home/ubuntu/hadoopconf/core-site.xml << 'EOF'
$core-site.xml$
EOF

# create mapred-site.xml:
cat - >> /home/ubuntu/hadoopconf/mapred-site.xml << 'EOF'
$mapred-site.xml$
EOF

# create hdfs-site.xml: (here, replication factor has to be entered!!!)
cat - >> /home/ubuntu/hadoopconf/hdfs-site.xml << 'EOF'
$hdfs-site.xml$
EOF

# create hadoop-env.sh:
cat - >> /home/ubuntu/hadoopconf/hadoop-env.sh << 'EOF'
$hadoop-env.sh$
EOF

# copy pssh/pscp to /usr/bin/pssh on master
# originally from Git repo https://github.com/jcmcken/parallel-ssh
# cp -r /mnt/pssh/pssh /usr/bin/
apt-get install -y pssh
cat - > /home/ubuntu/hosts.lst << 'EOF'
127.0.0.1
$for_loop_slaves$
EOF

mkdir /home/ubuntu/downloaded
cd /home/ubuntu/downloaded
wget http://mirror.switch.ch/mirror/apache/dist/hadoop/common/hadoop-2.7.1/hadoop-2.7.1.tar.gz
wget --no-cookies --no-check-certificate --header "Cookie: oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jdk/8u74-b02/jdk-8u74-linux-x64.tar.gz" -O jdk-8-linux-x64.tar.gz

function transferFirstUnpackLater {
	# copying hadoop & jdk to slaves in a compact form and unpacking them on
	# the slaves
	echo "copying hadoop and jdk to slaves" >> /home/ubuntu/deployment.log
	su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/downloaded/{hadoop-2.7.1.tar.gz,jdk-8-linux-x64.tar.gz} /home/ubuntu"
	echo "unpacking hadoop" >> /home/ubuntu/deployment.log
	su ubuntu -c "parallel-ssh -t 2000 -h /home/ubuntu/hosts.lst \"tar -xzf /home/ubuntu/hadoop-2.7.1.tar.gz\""
	echo "unpacking jdk" >> /home/ubuntu/deployment.log
	su ubuntu -c "parallel-ssh -t 2000 -h /home/ubuntu/hosts.lst \"tar -xzf /home/ubuntu/jdk-8-linux-x64.tar.gz\""
	echo "setting up both" >> /home/ubuntu/deployment.log
	# done with copying/unpacking hadoop/jdk
}

# here, the script has to decide which function to call:
# transferFirstUnpackLater or transferUnpackedFiles
echo "transferring hadoop & jdk to the masters/slaves and unpacking them" >> /home/ubuntu/deployment.log
transferFirstUnpackLater

echo "setting up hadoop & jdk" >> /home/ubuntu/deployment.log
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mkdir /usr/lib/hadoop\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mv /home/ubuntu/hadoop-2.7.1 /usr/lib/hadoop\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo ln -s /usr/lib/hadoop/hadoop-2.7.1 /usr/lib/hadoop/hadoop\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mv /usr/lib/hadoop/hadoop-2.7.1/etc/hadoop/ /etc/\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mkdir -p /usr/lib/java\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mv /home/ubuntu/jdk1.8.0_74/ /usr/lib/java/\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo ln -s /usr/lib/java/jdk1.8.0_74/ /usr/lib/java/jdk\""
su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/hadoopconf/bashrc.suffix /home/ubuntu"
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo sh -c \\\"cat /home/ubuntu/bashrc.suffix >> /etc/bash.bashrc\\\"\""

# now, let's copy the files to the slaves
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mkdir -p /app/hadoop/tmp\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo chown ubuntu:ubuntu /app/hadoop/tmp\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo chmod 750 /app/hadoop/tmp\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo chown -R ubuntu:ubuntu /etc/hadoop\""

# the file has to be copied into the user directory as ubuntu doesn't have
# permissions to write into /etc/hadoop
echo "copying config files from master to slave..." >> /home/ubuntu/deployment.log
su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/hadoopconf/core-site.xml /home/ubuntu"
# move file to its final location (/etc/hadoop)
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mv -f /home/ubuntu/core-site.xml /etc/hadoop\""

su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/hadoopconf/{{mapred,hdfs,yarn}-site.xml,hadoop-env.sh} /etc/hadoop"

su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/hadoopconf/hosts.replacement /home/ubuntu"
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mv -f /home/ubuntu/hosts.replacement /etc/hosts\""

su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"ln -s /etc/hadoop /usr/lib/hadoop/hadoop-2.7.1/etc/hadoop\""


# set master and slave nodes
echo $masternode$ > /etc/hadoop/masters
cat - > /etc/hadoop/slaves << 'EOF'
$masternodeasslave$$slavesfile$
EOF
source /etc/hadoop/hadoop-env.sh
su ubuntu -c "/usr/lib/hadoop/hadoop/bin/hdfs namenode -format"
su ubuntu -c "/usr/lib/hadoop/hadoop/sbin/start-dfs.sh"
su ubuntu -c "/usr/lib/hadoop/hadoop/sbin/start-yarn.sh"
echo "hadoop cluster ready" >> /home/ubuntu/deployment.log
duration=$SECONDS
echo "deployment took me $duration seconds"

# in the following line, the whole regular output will be redirected to the
# file debug.log in the user's home directory and the error output to the file
# error.log within the same directory
} 2> /home/ubuntu/error.log | tee /home/ubuntu/debug.log
