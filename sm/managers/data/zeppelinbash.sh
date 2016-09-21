# now, zeppelin should be installed
echo "now, installing zeppelin" >> /home/ubuntu/deployment.log
mkdir /usr/lib/zeppelin
chown ubuntu:ubuntu /usr/lib/zeppelin/
cd /usr/lib/zeppelin/
su ubuntu -c "wget http://mirror.switch.ch/mirror/apache/dist/zeppelin/zeppelin-0.6.1/zeppelin-0.6.1-bin-all.tgz"
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
echo "zeppelin ready" >> /home/ubuntu/deployment.log
# zeppelin is installed and running


#echo "downloading test file for zeppelin" >> /home/ubuntu/deployment.log
cd /home/ubuntu
apt-get install -y unzip
su ubuntu -c "wget http://archive.ics.uci.edu/ml/machine-learning-databases/00222/bank.zip"
su ubuntu -c "unzip /home/ubuntu/bank.zip"
su ubuntu -c "/usr/lib/hadoop/hadoop/bin/hdfs dfs -copyFromLocal /home/ubuntu/bank-full.csv /"
