# installing prerequisites for Zeppelin
deploymentLog "installing some requisites for Zeppelin"
apt-get install -y python3-tk python3-numpy python3-matplotlib xserver-xorg
rm /usr/bin/python
# ln -s /usr/bin/python3 /usr/bin/python
X &
echo "DISPLAY=:0.0" >> /etc/environment
#

# now, zeppelin should be installed
deploymentLog "now, installing zeppelin"
mkdir /usr/lib/zeppelin
chown ubuntu:ubuntu /usr/lib/zeppelin/
cd /usr/lib/zeppelin/
#su ubuntu -c "wget http://mirror.switch.ch/mirror/apache/dist/zeppelin/zeppelin-0.6.1/zeppelin-0.6.1-bin-all.tgz"
su ubuntu -c "wget http://reposerver/zeppelin/zeppelin-0.6.1-bin-all.tgz"
su ubuntu -c "tar -xvzf /usr/lib/zeppelin/zeppelin-0.6.1-bin-all.tgz"
su ubuntu -c "mkdir -p /usr/lib/zeppelin/zeppelin-0.6.1-bin-all/{logs,run}"
su ubuntu -c "ln -s /usr/lib/zeppelin/zeppelin-0.6.1-bin-all /usr/lib/zeppelin/zeppelin"
# port has to be changed to 8070 as 8080 is Spark's standard Web UI port
su ubuntu -c "cat /usr/lib/zeppelin/zeppelin/conf/zeppelin-site.xml.template | sed \"s/8080/8070/\" > /usr/lib/zeppelin/zeppelin/conf/zeppelin-site.xml"
cat - > /usr/lib/zeppelin/zeppelin/conf/zeppelin-env.sh << 'EOF'
$zeppelin_env_sh$
EOF
chown ubuntu:ubuntu /usr/lib/zeppelin/zeppelin/conf/zeppelin-env.sh
su ubuntu -c "source /etc/environment && source /etc/bash.bashrc && /usr/lib/zeppelin/zeppelin/bin/zeppelin-daemon.sh start"
deploymentLog "zeppelin ready"
# zeppelin is installed and running


deploymentLog "downloading test file for zeppelin"
cd /home/ubuntu
apt-get install -y unzip
su ubuntu -c "wget http://archive.ics.uci.edu/ml/machine-learning-databases/00222/bank.zip"
su ubuntu -c "unzip /home/ubuntu/bank.zip"
su ubuntu -c "/usr/lib/hadoop/hadoop/bin/hdfs dfs -copyFromLocal /home/ubuntu/bank-full.csv /"
