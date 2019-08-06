#!/usr/bin/env bash
yum install epel-release -y
yum install python36 python36-setuptools python36-pip -y
ln -s /usr/bin/python3 /usr/bin/python36
mkdir /usr/local/cloudstack_netbox_sync
cp *.py /usr/local/cloudstack_netbox_sync
cp requirements.txt
cp example/settings.ini /usr/local/cloudstack_netbox_sync/settings.ini.example
cd /usr/local/cloudstack_netbox_sync
python3.6 -m venv venv
. venv/bin/activate && pip install -r requirements.txt && pip install --editable .
ln -s /ust/local/cloudstack_netbox_sync/venv/bin/ /usr/local/bin/cloudstack_netbox_sync
