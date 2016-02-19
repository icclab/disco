# Service Manager

## Introduction

The Service Manager is the entry point for Service Orchestrators in Hurtle. The basic version can currently only deploy Service Orchestrators on an OpenShift installation. If you don't have such an installation available, you will have to search some other option. This Readme will show you two options that are available: you can either use the following SM which will allow you to deploy a SO on OpenStack or you can follow the following notes and program your own SM.

## SO on OpenStack

### notes

The current version of the SM is not optimised at all. This means that it's not sparing any resources, i.e. each SO needs to run on its own OpenStack VM and needs to have its own IP. With some effort, a dedicated VM could be provisioned that hosts all SO-s, but currently, I'm working on a solution for Docker which would be more resource-friendly. Nevertheless, the OpenStack solution was a quick way to have a SO deployed automatically on a system without OpenShift. For this, the currently, it's impossible to do anything but deploying and deleting SO-s. The basic structure for the other operations is provided, though not implemented yet.

In the following section, I will explain how to configure and use the SM.

### overview over the system

Hurtle is an orchestration system to provision SO-s which themselves will create heat orchestration templates. These templates will determine the lifecycle of computing clusters, probably installed on OpenStack.

In the original Hurtle release, you needed an OpenShift (or similar) system setup in order to execute a SO. With this SM, you can also deploy a SO on OpenStack. In order to achieve this, a VM is created on OpenStack where the SO will be installed in. But let's look at it step by step.

Before you can use the SM, you have to create a special volume on OpenStack which meets some basic properties. The testing system was a Debian derivate (Ubuntu Server 14.04), but any other Linux distribution should work as well. Its software was updated beforehand and some packages were installed. There had to be two available floating IPs as well; one of them was attached to the SO's VM, the other to the distributed computing cluster created by the SO. Technically, the second IP wasn't necessary but if you can't connect to your cluster, what use is it anyway, right?

With these prerequisites, you can instantiate a SO. (the procedure in detail is covered in the next section; this part is just an overview) If you would like to do this, you have to deploy a SO. This is basically done with some CRUD commands over HTTP. But note that currently, only the C and D are implemented.

So, let's start with instantiation: as soon as you fire up a SO, a VM is provisioned on OpenStack (with the given floating IP) and the Git repository of the SO is cloned into the VM. As soon as this is done, it is started and the SM sends the deploying command to it. The SO then will decide what to do in this stage.

As soon as the SO isn't needed anymore, the delete command can be issued to the SM which first will forward it to the SO and immediately afterwards will destroy the VM. (and release the floating IP)

For the detailed configuration and example commands, please refer to the following section.

### configuration

In order to get the SM working, you have to make some preparations to your OpenStack installation. This means that for each deployed SO, you need to have 2 available floating IPs and a volume with the basic tools installed already.

1. First, you have to create a volume with the necessary software installed already. This software is basically in the apt packages python git python-pip and python-dev. If you do it on a different package management system, you need to ensure that you can execute python, you have the dev files for python and you can clone git repositories. Plus you have to install code from two Git repositories as well for the SO.

I ran the following bash command for setting up the VM:

```
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
} 2> ~/error.log | tee ~/debug.log
```
2. As soon as this is done, you have to create a snapshot of the volume and save it as a volume on OpenStack. This volume will be the basis of your SO's VM.

3. You also need to upload your SO to a publicly available Git repository as the VM needs to be able to clone it.

4. Some more things you have to setup within OpenStack in order to launch a VM. These are:
   * creating a network and a subnet and insert their IDs into the HOT template within the openstack_so_manager.py file
   * you have to adjust the image name within the same template to the name you gave the volume before
   * adjust the SSH public key name (you need an SSH public key within OpenStack)
   * also update the flavor so that it's big enough for the created volume but still as small as possible (only the SO will be executed on this VM)

5. Now, you're ready to power up the SM. But before you do that, please take a look at the user_data part within the Heat template that will be deployed by the SM: maybe you have to make changes to the path, the Git repository's address, and so on. The following command will create a SO for you (don't worry, I will explain the details immediately)

```
curl -v -X POST http://127.0.0.1:8888/haas/ -H 'Category: haas; scheme="http://schemas.cloudcomplab.ch/occi/sm#"; class="kind";' -H 'content-type: text/occi' -H 'X-Auth-Token: 137f5775f01245588c936dd05b7c2893' -H 'X-Tenant-Name: mesz' -H 'X-OCCI-Attribute: icclab.haas.debug.donotdeploy="False",icclab.haas.master.createvolumeforattachment="False",icclab.haas.sm.sofloatingipid="c03eb859-99f7-49f7-9316-dffd5af8c299",icclab.haas.sm.sofloatingip="160.85.4.205",icclab.haas.rootfolder="/root/testso/bundle/data",icclab.haas.master.sshkeyname="MNMBA2"'
```

   1. You have to update the IP and the service type which is to be created. (here, it's haas) You specified this in the *service_manifest.json* file of the SO.
   2. the X-Auth-Token and X-Tenant-Name headers are the credentials you want to use to deploy the computing cluster from out of the SO.
   3. with the X-OCCI-Attribute header, you send the required configuration settings to the SO and the SM. They will be forwarded to the SO automatically. Here, you will have to update the settings icclab.haas.sm.sofloatingipid and icclab.haas.sm.sofloatingip which are used by the SM: the first one refers to the ID of the floating IP which has to be connected to the SO's VM, the second is the coupled IP address.

6. Lean back and wait, until deployment has finished. Currently, there's no possibility of checking the deployment status over the SM, but you can have a look at the stack status within OpenStack's Horizon.

7. You can list the created SO instanceswith the following command

```
curl -v -X GET http://127.0.0.1:8888/haas/ -H 'Accept: text/occi' -H 'X-Auth-Token: 137f5775f01245588c936dd05b7c2893' -H 'X-Tenant-Name: mesz'
```

    1. Here, you already know all the parameters that you have to append insert.

8. If you would like to delete the SO again, the following command will help you

```
curl -v -X DELETE http://127.0.0.1:8888/haas/3850dc24-557b-44c0-b5e1-1fef0b6775f9 -H 'Category: haas; scheme="http://schemas.cloudcomplab.ch/occi/sm#"; class="kind";' -H 'content-type: text/occi' -H 'X-Auth-Token: 137f5775f01245588c936dd05b7c2893' -H 'X-Tenant-Name: mesz' -H 'X-OCCI-Attribute: icclab.haas.sm.sofloatingip="160.85.4.205"'
```

    1. This one is a little more complicated, so let's look at it in more detail: the IP address is still the same, but everything after the service type is generated by the SM. You can get that address over the command at point 7.
    2. Tenant name and token are the same as before, but you have to provide the IP address of the SO's VM as data retention within the SM is based on the SO's IP.

9. After this last step, you can check with the command at point 7 that the SO has been deleted and the resources freed. You can also double check that information on OpenStack Horizon. (Orchestration -> Stacks)

## How to write your own SM

nothing yet...
