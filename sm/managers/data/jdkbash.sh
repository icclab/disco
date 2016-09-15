cd /home/ubuntu/downloaded

setState

wget --no-cookies --no-check-certificate --header "Cookie: oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jdk/8u74-b02/jdk-8u74-linux-x64.tar.gz" -O jdk-8-linux-x64.tar.gz

deploymentLog "copying JDK to slaves"

su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/downloaded/jdk-8-linux-x64.tar.gz /home/ubuntu"

deploymentLog "unpacking jdk"

su ubuntu -c "parallel-ssh -t 2000 -h /home/ubuntu/hosts.lst \"tar -xzf /home/ubuntu/jdk-8-linux-x64.tar.gz\""

deploymentLog "setting up JDK"

su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mkdir -p /usr/lib/java\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo mv /home/ubuntu/jdk1.8.0_74/ /usr/lib/java/\""
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \"sudo ln -s /usr/lib/java/jdk1.8.0_74/ /usr/lib/java/jdk\""
