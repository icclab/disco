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

state=0

function setState() {
    echo $state > /home/ubuntu/status.log
    let "state += 1"
}

function deploymentLog() {
    echo $1 >> /home/ubuntu/deployment.log
}
# state 1
setState

# solve problem with not correctly configured locale...
echo -e "LC_ALL=en_US.UTF-8\nLANG=en_US.UTF-8" >> /etc/environment

# serve deployment.log
sh -c "while true; do nc -l -p 8084 < /home/ubuntu/deployment.log; done" > /dev/null 2>&1 &

# monitoring from the outside that setup has started
echo "0" > /home/ubuntu/progress.log
sh -c "while true; do nc -l -p 6088 < /home/ubuntu/progress.log; done" > /dev/null 2>&1 &


# disable IPv6 as Hadoop won't run on a system with it activated
deploymentLog "disabling IPv6"
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

deploymentLog "setting up files for deployment on slaves..."

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

86.119.37.182   reposerver
EOF
mv -f /root/hosts.replacement /home/ubuntu/hadoopconf


# copy pssh/pscp to /usr/bin/pssh on master
# originally from Git repo https://github.com/jcmcken/parallel-ssh
# cp -r /mnt/pssh/pssh /usr/bin/
apt-get update
apt-get install -y pssh # git
cat - > /home/ubuntu/hosts.lst << 'EOF'
127.0.0.1
$for_loop_slaves$
EOF


su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/hadoopconf/hosts.replacement /home/ubuntu"
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mv -f /home/ubuntu/hosts.replacement /etc/hosts\""



mkdir /home/ubuntu/downloaded
cd /home/ubuntu/downloaded

$shellframeworkbash$



















# install ZooKeeper (needed for Storm)
cd /home/ubuntu/downloaded
wget http://mirror.switch.ch/mirror/apache/dist/zookeeper/zookeeper-3.4.9/zookeeper-3.4.9.tar.gz
su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/downloaded/zookeeper-3.4.9.tar.gz /home/ubuntu"
deploymentLog "unpacking hadoop"

su ubuntu -c "parallel-ssh -t 2000 -h /home/ubuntu/hosts.lst \"tar -xzf /home/ubuntu/zookeeper-3.4.9.tar.gz\""
# at this point, the config file has to be set and distributed to each machine
cat - > /home/ubuntu/downloaded/conf/zoo.cfg << 'EOF'
$zoo_cfg$
EOF
su ubuntu -c "parallel-ssh -t 2000 -h /home/ubuntu/hosts.lst \"sudo mkdir /usr/lib/zookeeper && sudo chown ubuntu:ubuntu /usr/lib/zookeeper\""
su ubuntu -c "parallel-ssh -t 2000 -h /home/ubuntu/hosts.lst \"mv /home/ubuntu/zookeeper-3.4.9 /usr/lib/zookeeper\""





# example zookeeper.../conf/zoo.cfg file; for each machine the same (file 'myid' within dataDir directory specifies the individual server number):
#tickTime=2000
#dataDir=/var/lib/zookeeper
#clientPort=2181
#initLimit=5
#syncLimit=2
#server.1=masternode-e45d1fc5-758e-11e6-a3e0-34363b7e7806:2888:3888
#server.2=slavenode-e45d1fc5-758e-11e6-a3e0-34363b7e7806-1:2888:3888





# install Storm
mkdir /usr/lib/storm

# in the end: starting storm: bin/storm nimbus && bin/storm supervisor && bin/storm ui <- nimbus & ui just on master node




duration=$SECONDS
# save it into deployment.log...
deploymentLog "deployment took me $duration seconds"
# ...and into debug.log
echo "deployment took me $duration seconds"

deploymentLog `date`

# state 8
setState

# everything has been setup
echo "1" > /home/ubuntu/progress.log

# in the following line, the whole regular output will be redirected to the
# file debug.log in the user's home directory and the error output to the file
# error.log within the same directory
} 2> /home/ubuntu/error.log | tee /home/ubuntu/debug.log
