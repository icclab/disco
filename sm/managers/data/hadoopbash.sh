# state 3
setState

# create yarn-site.xml:
cat - > /home/ubuntu/hadoopconf/yarn-site.xml << 'EOF'
$yarn-site.xml$
EOF
sed -i 's/\$masteraddress\$/'`/sbin/ifconfig eth0 | grep 'inet addr' | cut -d: -f2 | awk '{print $1}'`'/g' /home/ubuntu/hadoopconf/yarn-site.xml

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

cd /home/ubuntu/downloaded
#wget http://mirror.switch.ch/mirror/apache/dist/hadoop/common/hadoop-2.7.1/hadoop-2.7.1.tar.gz
wget http://reposerver/hadoop/hadoop-2.7.1.tar.gz

# copying hadoop to slaves in a compact form and unpacking it on
# the slaves
deploymentLog "copying hadoop to slaves"
su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/downloaded/hadoop-2.7.1.tar.gz /home/ubuntu"
deploymentLog "unpacking hadoop"

setState
su ubuntu -c "parallel-ssh -t 2000 -h /home/ubuntu/hosts.lst \"tar -xzf /home/ubuntu/hadoop-2.7.1.tar.gz\""


setState

deploymentLog "setting up hadoop"
# copy the SSH files to all slaves
su ubuntu -c "parallel-scp -h ~/hosts.lst ~/.ssh/{config,id_rsa,id_rsa.pub} ~/.ssh"
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mkdir /usr/lib/hadoop\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mv /home/ubuntu/hadoop-2.7.1 /usr/lib/hadoop\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo ln -s /usr/lib/hadoop/hadoop-2.7.1 /usr/lib/hadoop/hadoop\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mv /usr/lib/hadoop/hadoop-2.7.1/etc/hadoop/ /etc/\""
su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/hadoopconf/bashrc.suffix /home/ubuntu"
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo sh -c \\\"cat /home/ubuntu/bashrc.suffix >> /etc/bash.bashrc\\\"\""

# now, let's copy the files to the slaves
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mkdir -p /app/hadoop/tmp\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo chown ubuntu:ubuntu /app/hadoop/tmp\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo chmod 750 /app/hadoop/tmp\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo chown -R ubuntu:ubuntu /etc/hadoop\""

# the file has to be copied into the user directory as ubuntu doesn't have
# permissions to write into /etc/hadoop
deploymentLog "copying config files from master to slave..."
su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/hadoopconf/core-site.xml /home/ubuntu"
# move file to its final location (/etc/hadoop)
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mv -f /home/ubuntu/core-site.xml /etc/hadoop\""

su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/hadoopconf/{{mapred,hdfs,yarn}-site.xml,hadoop-env.sh} /etc/hadoop"

#su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/hadoopconf/hosts.replacement /home/ubuntu"
#su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mv -f /home/ubuntu/hosts.replacement /etc/hosts\""

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

#cd /home/ubuntu
#git clone https://github.com/Pentadactylus/yarn_jars.git
#echo "CLASSPATH=/home/ubuntu/yarn_jars/hadoop-client-1.2.1.jar:/home/ubuntu/yarn_jars/commons-cli-1.2.jar:/home/ubuntu/yarn_jars/hadoop-core-1.2.1.jar" >> /etc/bash.bashrc

deploymentLog "hadoop cluster ready"


