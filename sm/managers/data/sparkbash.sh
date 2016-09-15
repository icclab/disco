# install Apache Spark on master node
echo "downloading Apache Spark to master node" >> /home/ubuntu/deployment.log
su ubuntu -c "sudo mkdir /home/ubuntu/spark"
cd /home/ubuntu/spark
chown ubuntu:ubuntu /home/ubuntu/spark
su ubuntu -c "wget http://d3kbcqa49mib13.cloudfront.net/spark-2.0.0-bin-hadoop2.7.tgz"
#su ubuntu -c "tar -xzf /home/ubuntu/spark/spark-2.0.0-bin-hadoop2.7.tgz"
su ubuntu -c "parallel-ssh -t 2000 -h /home/ubuntu/hosts.lst \"sudo sh -c \\\"echo \\\\\\\"SPARK_HOME=\\\\\\\\\\\\\\\"/usr/lib/spark/spark\\\\\\\\\\\\\\\"\\\\nJAVA_HOME=\\\\\\\\\\\\\\\"/usr/lib/java/jdk\\\\\\\\\\\\\\\"\\\\\\\" >> \\\/etc\\\/environment\\\"\""
su ubuntu -c "parallel-ssh -t 2000 -h ~/hosts.lst \"sudo mkdir /usr/lib/spark\""
su ubuntu -c "parallel-ssh -t 2000 -h ~/hosts.lst \"sudo chown ubuntu:ubuntu /usr/lib/spark/\""
su ubuntu -c "parallel-scp -h ~/hosts.lst ~/spark/spark-2.0.0-bin-hadoop2.7.tgz /usr/lib/spark"
su ubuntu -c "parallel-ssh -t 2000 -h /home/ubuntu/hosts.lst \"tar -xzf /usr/lib/spark/spark-2.0.0-bin-hadoop2.7.tgz\""
#su ubuntu -c "parallel-ssh -t 2000 -h ~/hosts.lst \"mv spark-2.0.0-bin-hadoop2.7 /usr/lib/spark/\""
su ubuntu -c "parallel-ssh -t 2000 -h ~/hosts.lst \"mv spark-2.0.0-bin-hadoop2.7 /usr/lib/spark\""
su ubuntu -c "parallel-ssh -t 2000 -h ~/hosts.lst \"ln -s /usr/lib/spark/spark-2.0.0-bin-hadoop2.7/ /usr/lib/spark/spark\""
cat - > /usr/lib/spark/spark/conf/slaves << 'EOF'
$masternodeasslave$$slavesfile$
EOF
su ubuntu -c "/usr/lib/spark/spark/sbin/start-master.sh"
su ubuntu -c "/usr/lib/spark/spark/sbin/start-slaves.sh"
echo "Spark installed and started" >> /home/ubuntu/deployment.log
# at this point, Spark cluster is installed and running