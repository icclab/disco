# now, let's get to jupyter
deploymentLog "installing jupyter"
apt-get install -y build-essential python3-dev python3-pip
pip3 install jupyter

# create mapred-site.xml:
su ubuntu -c "mkdir /home/ubuntu/.jupyter"
cat - >> /home/ubuntu/.jupyter/jupyter_notebook_config.py << 'EOF'
$jupyter_notebook_config.py$
EOF
chown ubuntu:ubuntu /home/ubuntu/.jupyter/jupyter_notebook_config.py
su ubuntu -c "jupyter-notebook &"
deploymentLog "jupyter ready"
# jupyter is installed and running

