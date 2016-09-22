# now, let's get to jupyter
echo "installing jupyter" >> /home/ubuntu/deployment.log
apt-get install -y build-essential python3-dev python3-pip
pip3 install jupyter

# create mapred-site.xml:
su ubuntu -c "mkdir /home/ubuntu/.jupyter"
cat - >> /home/ubuntu/.jupyter/jupyter_notebook_config.py << 'EOF'
$jupyter_notebook_config.py$
EOF
chown ubuntu:ubuntu /home/ubuntu/.jupyter/jupyter_notebook_config.py
su ubuntu -c "jupyter-notebook &"
echo "jupyter ready" >> /home/ubuntu/deployment.log
# jupyter is installed and running

