# DISCO

## Introduction

DISCO stands for DIStributed COmputing. It provides the user with the ability to deploy a distributed computing cluster in as short a time as imaginable. Not only will it setup the whole virtual computing cluster but it will also install the desired distributed computing frameworks on it. Then, it will guide you through the entire lifecycle of the cluster until its disposal, which is also maintained by DISCO. You will be amazed by how much work DISCO is taking care of - and how intuitively it handles your requests.

## Running DISCO

In the following section, I will explain how to configure and use the Service Manager (SM; part of the Hurtle framework), the core part of DISCO.

### Overview over the system

DISCO is an orchestration system to create distributed computing clusters. How this is done you ask? The answer is over Heat templates. These templates will determine the lifecycle of computing clusters, probably installed on OpenStack.

In the original Hurtle release, you needed an OpenShift (or similar) system setup in order to execute a Service Orchestrator (SO). With DISCO, you don't need the SO anymore - everything will be automatically deployed as a distributed computing cluster.

Provisioning a cluster is done in two steps:

1. deploying DISCO on a dedicated machine which can be done on the same OpenStack system as the cluster is to be hosted on or on a different one - it can even be deployed on a dedicated physical computer or on localhost (for testing)
2. issuing the creation request to DISCO

For the detailed configuration and example commands, please refer to the following section.

### Configuration (Setting up DISCO)

The most basic need is an OpenStack installation with access to the necessary resources for the clusters. Also, you need to expose the OpenStack endpoints to DISCO. These are actually just the regular endpoints so no complication in this part. You can find them on Horizon (OpenStack's web interface) -> Compute -> Access & Security -> API Access. 

1. The dependencies need to be installed first which include some python tools.
    
    ```
    sudo apt-get install -y git python-pip python-dev python-flask libffi-dev
    ```

2. Now, the SDK can be installed.

    ```
    git clone https://github.com/icclab/hurtle_cc_sdk.git
    cd hurtle_cc_sdk
    sudo python setup.py install
    ```
    
3. At this point, DISCO can be installed.

    ```
    git clone -b hadoop_sm https://github.com/Pentadactylus/sm_openstack
    cd sm_openstack
    sudo python setup.py install
    ```
    
4. Before you can start DISCO, you need to make a couple of changes in the sm.cfg configuration file within the etc subdirectory of DISCO. These values are:
    - manifest: the path to the file service_manifest.json which is in the sm/managers/data subfolder of DISCO but could be at any other location.
    - design_uri: Keystone's public endpoint in OpenStack.
    - service_params: the path of the service_params.json file; located within the etc subfolder of DISCO.

5. As soon as these changes are made, you can start DISCO with the command

    ```
    service_manager -c /path/to/sm.cfg
    ```
    
    At this point, DISCO is running and you can issue the HTTP commands to create a cluster.
    
### Creating a cluster

In order to have a distributed computing cluster setup, you will need to issue a couple of HTTP commands. So let's have a look at those. Additionally, you will need a SSH public key registered within OpenStack which you can login with later on the cluster's master.

1. You can list all the available services of a specific DISCO SM with the command

    ```
    curl -v -X GET http://xxx.xxx.xxx.xxx:8888/-/ -H 'Accept: text/occi' -H "X-User-Name: $OS_USERNAME" -H "X-Password: $OS_PASSWORD" -H "X-Tenant-Name: $OS_TENANT_NAME"
    ```
    
    The three variables $OS_USERNAME, $OS_PASSWORD and $OS_TENANT_NAME are the same that you can download within the openrc.sh file from OpenStack.
    
    This will list all the registered services with the possible parametrs. For DISCO, this is the service haas.
    
2. With the following command, a cluster can be created:

   ```
   curl -v -X POST http://xxx.xxx.xxx.xxx:8888/haas/ -H 'Category: haas; scheme="http://schemas.cloudcomplab.ch/occi/sm#"; class="kind";' -H "X-User-Name: $OS_USERNAME" -H "X-Tenant-Name: $OS_TENANT_NAME" -H "X-Password: $OS_PASSWORD" -H "X-Region-Name: $OS_REGION_NAME" -H 'content-type: text/occi' -H 'X-OCCI-Attribute: icclab.haas.rootfolder="/path/to/sm/managers/data",icclab.haas.master.sshkeyname="<your SSH public key name>"'
   ```

   Two additional headers are included in this command: one for the region where the cluster should be deployed and another for the parameters for the cluster setup. The command above contains the minimum of the required parameters which will setup a cluster.
   
   You can see two parameters which are absolutely necessary for each cluster:
   - icclab.haas.rootfolder specifies the path to the data folder for the heat template fragments. Again, in the standard version, it can be found under sm/managers/data in the DISCO repository.
   - icclab.haas.master.sshkeyname tells DISCO which (already registered) SSH keyname should be inserted within the new cluster's master node.
   
   A successful deployment will be acknowledged with an 'OK' and a UUID which identifies the created cluster within DISCO. It is within the location field of the response. Remember this because it is the address which you will send the following requests to.

3. Though if you haven't taken note of the UUID, you can still retrieve it with the command

   ```
   curl -v -X GET http://xxx.xxx.xxx.xxx:8888/haas/ -H 'Accept: text/occi' -H "X-User-Name: $OS_USERNAME" -H "X-Tenant-Name: $OS_TENANT_NAME" -H "X-Password: $OS_PASSWORD"
   ```
   
   This will list all clusters which have been deployed for the given username on the given DISCO instance.
   
4. If you want to know the IP of your newly created cluster, issue the following HTTP command:

   ```
   curl -v -X GET http://xxx.xxx.xxx.xxx:8888/haas/UUID -H 'Accept: text/occi' -H "X-Tenant-Name: $OS_TENANT_NAME" -H "X-User-Name: $OS_USERNAME" -H "X-Password: $OS_PASSWORD" -H "X-Region-Name: $OS_REGION_NAME"
   ```

   Note: if the cluster hasn't been fully created by OpenStack yet, this command will return an error. Just try it again after a short time.
   
   Note 2: Don't forget to replace the UUID field with the actual ID returned by DISCO in the command before.
   
   As soon as the cluster creation has been finished on OpenStack's side, this command will return the IP address of the cluster's master node. It is in the 'externalIP' field.
   
5. As soon as you have the IP of the master node, you can login over SSH:

   ```
   ssh ubuntu@external.ip.of.master
   ```
   
   Because the deployment on OpenStack is just a part of the cluster provisioning, your cluster most likely isn't ready yet for big data processing. But as soon as you have logged in, you can check the deployment status:
   
   ```
   tail -f /home/ubuntu/deployment.log
   ```
   
   As soon as the deployment has finished, it will tell so within the deployment.log file.

6. If you would like to delete the cluster again, the following command will help you

    ```
    curl -v -X DELETE http://xxx.xxx.xxx.xxx:8888/haas/UUID -H 'Category: haas; scheme="http://schemas.cloudcomplab.ch/occi/sm#"; class="kind";' -H 'content-type: text/occi' -H "X-User-Name: $OS_USERNAME" -H "X-Password: $OS_PASSWORD" -H "X-Tenant-Name: $OS_TENANT_NAME" -H 'X-Region-Name: $OS_REGION_NAME"
    ```

7. After this last step, you can check with the command at a previous step that the cluster is not registered within DISCO anymore and the resources are freed. You can also double check that information on OpenStack Horizon. (Orchestration -> Stacks)
