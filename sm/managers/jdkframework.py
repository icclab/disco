from framework import Framework

class JDKFramework(Framework):
    def __init__(self, deployClass, attributes):
        super(JDKFramework,self).__init__(deployClass, attributes)

    def get_bash(self):
        return '# state 2\n\
setState\n\
\n\
deploymentLog "downloading JDK"\n\
wget --no-cookies --no-check-certificate --header "Cookie: oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jdk/8u74-b02/jdk-8u74-linux-x64.tar.gz" -O jdk-8-linux-x64.tar.gz\n\
\n\
deploymentLog "copying JDK to slaves" >> /home/ubuntu/deployment.log\n\
su ubuntu -c "parallel-scp -h /home/ubuntu/hosts.lst /home/ubuntu/downloaded/jdk-8-linux-x64.tar.gz /home/ubuntu"\n\
\n\
deploymentLog "unpacking jdk"\n\
su ubuntu -c "parallel-ssh -t 2000 -h /home/ubuntu/hosts.lst \\"tar -xzf /home/ubuntu/jdk-8-linux-x64.tar.gz\\""\n\
\n\
deploymentLog "setting up JDK"\n\
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \\"sudo mkdir -p /usr/lib/java\\""\n\
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \\"sudo mv /home/ubuntu/jdk1.8.0_74/ /usr/lib/java/\\""\n\
su ubuntu -c "parallel-ssh -h /home/ubuntu/hosts.lst \\"sudo ln -s /usr/lib/java/jdk1.8.0_74/ /usr/lib/java/jdk\\""\n\
'
    def get_name(self):
        return "jdk"

    def get_dependencies(self):
        return {"environment": {"parallel_scp":None,"parallel_ssh":None,"hosts_lst":None,"setstate":None,"deployment_log":None}}

