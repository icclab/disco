#!/bin/bash
{
SECONDS=0
apt-get update
apt-get -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade
apt-get install -y python git python-pip python-dev
cd ~
git clone https://github.com/icclab/hurtle_cc_sdk.git
cd ~/hurtle_cc_sdk
pip install --upgrade requests
python setup.py install
cd ~
git clone https://github.com/icclab/hurtle_sm.git
cd ~/hurtle_sm
python setup.py install
cd ~
git clone https://github.com/Pentadactylus/testso.git
python ~/testso/bundle/wsgi/application
} 2> ~/error.log | tee ~/debug.log
