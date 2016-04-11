# Copyright 2014-2015 Zuercher Hochschule fuer Angewandte Wissenschaften
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from sm.managers.generic import Task
import uuid
from sm.log import LOG
from sm.config import CONFIG
from keystoneclient.v2_0 import client as keystoneclient
from heatclient import client as heatclient
import time
import json
from os import environ
import copy
import os
import ConfigParser

__author__ = 'balazs'

HEAT_VERSION = '1'

# some global variables have to be saved so that different class instances can
# access them
so_instances = {}

class SOInstanceManager():
    @staticmethod
    def addSO(newSO, key):
        global so_instances
        so_instances[key] = copy.deepcopy(newSO)

    @staticmethod
    def getSO(key):
        global so_instances
        if key in so_instances:
            return so_instances[key]
        else:
            return None

    @staticmethod
    def deleteSO(key):
        global so_instances
        if key in so_instances:
            del so_instances[key]

# ClientProvider returns the appropriate client after fetching the needed service catalog
class ClientProvider():
    @staticmethod
    def getOrchestrator( attributes ):

        # getParam will return the parameter given
        # several layer are queried for the parameters in this order:
        #   - given over curl request
        #   - given as environment variables
        #   - given within the service_manager section of the sm.cfg file
        def getParam( paramName ):
            if paramName in attributes:
                return attributes[paramName]
            elif environ.get(paramName) is not None:
                return environ.get(paramName)
            elif CONFIG.get('service_manager',paramName,'') is not None:
                return CONFIG.get('service_manager',paramName,'')
            else:
                LOG.debug(paramName+"not given")
                raise

        # first, a connection to keystone has to be established in order to load the service catalog for the orchestration endpoint (heat)
        # the design_uri has to be given in the sm.cfg file so that no other OpenStack deployment can be used
        kc = keystoneclient.Client(auth_url=CONFIG.get('service_manager','design_uri',''),
                                   username=getParam('OS_USERNAME'),
                                   password=getParam('OS_PASSWORD'),
                                   tenant_name=getParam('OS_TENANT_NAME')
                                   )

        # get the orchestration part of the service catalog
        orch = kc.service_catalog.get_endpoints(service_type='orchestration',
                                                region_name=getParam('OS_REGION_NAME'),
                                                endpoint_type='publicURL'
                                                )

        # create a heat client with acquired public endpoint
        # if the correct region had been given, there is supposed to be but one entry for the orchestrator URLs
        hc = heatclient.Client(HEAT_VERSION, endpoint=orch['orchestration'][0]['publicURL'],token=kc.auth_token)
        return hc

class SOContainer():
    def __init__(self, *args): #ip, frameworks, template, stackname):
        # if isinstance(wargs, dict):
        self.data = copy.deepcopy(args)
        print(args)

    def getData(self):
        return self.data

    def addEntry(self, *args):
        if 'value' in args and 'key' in args:
            self.data[args['key']] = copy.deepcopy(args['value'])

    def getEntry(self, key):
        if 'key' in self.data:
            return self.data[key]

class Init(Task):

    def __init__(self, entity, extras):
        Task.__init__(self, entity, extras, state='initialise')

    def run(self):
        LOG.debug("running init")
        self.start_time = time.time()
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'init',
                    'phase_event': 'start',
                    'response_time': 0,
                    }
        LOG.debug(json.dumps(infoDict))
        self.entity.attributes['mcn.service.state'] = 'initialise'

        # Do init work here
        self.entity.extras = {}
        self.entity.extras['loc'] = 'foobar'
        self.entity.extras['tenant_name'] = self.extras['tenant_name']

        elapsed_time = time.time() - self.start_time
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'init',
                    'phase_event': 'done',
                    'response_time': elapsed_time,
                    }
        LOG.debug(json.dumps(infoDict))
        return self.entity, self.extras

class Activate(Task):
    def __init__(self, entity, extras):
        Task.__init__(self, entity, extras, state='activate')

    def run(self):
        LOG.debug("running activate")
        self.start_time = time.time()
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'activate',
                    'phase_event': 'start',
                    'response_time': 0,
                    }
        LOG.debug(json.dumps(infoDict))
        self.entity.attributes['mcn.service.state'] = 'activate'

        # Do activate work here

        elapsed_time = time.time() - self.start_time
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'activate',
                    'phase_event': 'done',
                    'response_time': elapsed_time,
                    }
        LOG.debug(json.dumps(infoDict))
        return self.entity, self.extras

class Deploy(Task):
    """
    The Deploy class is about deploying the SO on the system where it has to
    run in the end. In this case, it's on OpenStack. That means that a VM has
    to be created on OpenStack and the SO has to be setup within it.
    """
    def __init__(self, entity, extras):

        Task.__init__(self, entity, extras, state='deploy')

        self.extras = extras

    def run(self):
        # TODO: bad practise
        global so_instances

        LOG.debug("running deploy")
        self.start_time = time.time()
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'deploy',
                    'phase_event': 'start',
                    'response_time': 0,
                    }
        LOG.debug(json.dumps(infoDict))
        self.entity.attributes['mcn.service.state'] = 'deploy'

        # retrieve the Heat template which will setup the cluster according to the specifications within the given http attributes
        heatTemplate = self.__get_heat_template(attributes=self.entity.attributes)

        # If heatTemplate is empty, nothing should be deployed. This can happen if the according debug setting is set to not deploying.
        if heatTemplate != "":

            # deploy the Heat orchestration template on OpenStack:
            heatClient=ClientProvider.getOrchestrator(self.entity.attributes)

            randomstring = str(uuid.uuid1())

            # set the required attributes (stack name and Heat template) to what is needed
            curStackName = 'disco_'+randomstring
            body = {
                'stack_name': curStackName,
                'template': heatTemplate
            }
            LOG.debug('the stack\'s name is '+body['stack_name'])

            # here is where the actual SO deployment happens
            tmp = heatClient.stacks.create(**body)

            # the return value will be saved locally so it can be retrieved for future operations
            SOInstanceManager.addSO(SOContainer(tmp),self.entity.identifier)
            LOG.debug("new stack's ID: "+tmp['stack']['id'])

        return self.entity, self.extras

    def __get_heat_template(self, attributes):
        randomstring = "-"+str(uuid.uuid1())

        # this function will return the first of following values in the order
        # of occurrence:
        #   - given by the user during instantiation
        #   - set as a default value in the config file
        #   - an empty string
        def getAttr(attrName):
            if(attrName in attributes):
                return attributes[attrName]
            else:
                try:
                    retVal = config.get('cluster',attrName)
                    return retVal
                except:
                    return ""

        # the rootFolder is needed in order to load the config files
        self.rootFolder = getAttr('icclab.haas.rootfolder')
        if self.rootFolder=="":
            # if no rootFolder has been provided, take the path it's located
            # within the Docker image
            self.rootFolder = "data/"

        # setup parser for config file
        config = ConfigParser.RawConfigParser()
        config.read(os.path.join(self.rootFolder,'defaultSettings.cfg'))

        LOG.info("deploying stack...")

        # the needed variables for the Heat Orchestration Template will be set
        # on the following lines; the function getAttr() is returning the
        # appropriate value. As an empty value cannot be used for int/float
        # conversion, they have to be set within a try-except block.
        slaveCount = 1
        try:
            slaveCount = int(getAttr('icclab.haas.slave.number'))
        except:
            pass
        masterImage = getAttr('icclab.haas.master.image')
        slaveImage = getAttr('icclab.haas.slave.image')
        masterFlavor = getAttr('icclab.haas.master.flavor')
        slaveFlavor = getAttr('icclab.haas.slave.flavor')
        slaveOnMaster = getAttr('icclab.haas.master.slaveonmaster').lower() in ['true', '1']
        SSHPublicKeyName = getAttr('icclab.haas.master.sshkeyname')
        SSHMasterPublicKey = getAttr('icclab.haas.master.publickey')
        withFloatingIP = getAttr('icclab.haas.master.withfloatingip').lower() in ['true','1']
        master_name = getAttr('icclab.haas.master.name')+randomstring
        slave_name = getAttr('icclab.haas.slave.name')+randomstring+"-"
        subnet_cidr = getAttr('icclab.haas.network.subnet.cidr')
        subnet_gw_ip = getAttr('icclab.haas.network.gw.ip')
        subnet_allocation_pool_start = getAttr('icclab.haas.network.subnet.allocpool.start')
        subnet_allocation_pool_end = getAttr('icclab.haas.network.subnet.allocpool.end')
        subnet_dns_servers = getAttr('icclab.haas.network.dnsservers')
        image_id = getAttr('icclab.haas.master.imageid')
        floatingIpId = getAttr('icclab.haas.master.attachfloatingipwithid')

        externalNetwork = getAttr('icclab.haas.network.external')

        noDeployment = getAttr('icclab.haas.debug.donotdeploy').lower() in ['true','1']
        saveToLocalPath = getAttr('icclab.haas.debug.savetemplatetolocalpath')

        diskId = 'virtio-'+image_id[0:20]

        # masterSSHKeyEntry = ''

        def getFileContent(fileName):
            f = open(os.path.join(self.rootFolder, fileName))
            retVal = f.read()
            f.close()
            return retVal

        # read all the necessary files for creating the Heat template
        clusterTemplate = getFileContent("cluster.yaml");
        slaveTemplate = getFileContent("slave.yaml")
        masterBash = getFileContent("master_bash.sh")
        master_id_rsa = getFileContent("master.id_rsa").replace("\n","\\n")
        master_id_rsa_pub = getFileContent("master.id_rsa.pub").replace("\n","")
        yarn_site_xml = getFileContent("yarn-site.xml")
        core_site_xml = getFileContent("core-site.xml")
        mapred_site_xml = getFileContent("mapred-site.xml")
        hdfs_site_xml = getFileContent("hdfs-site.xml")
        hadoop_env_sh = getFileContent("hadoop-env.sh")

        slaves = ""
        hostFileContent = ""
        forLoopSlaves = ""
        paramsSlave = ""
        slavesFile = ""
        hostsListFile = ""


        slaveTemplate = slaveTemplate.replace("$master.id_rsa.pub$",master_id_rsa_pub)
        for i in xrange(1,slaveCount+1):
            slaves += slaveTemplate.replace("$slavenumber$",str(i))
            hostFileContent += "$slave"+str(i)+"address$\t"+slave_name+str(i)+"\n"
            forLoopSlaves += " $slave"+str(i)+"address$"
            paramsSlave += "            $slave"+str(i)+"address$: { get_attr: [hadoop_slave_"+str(i)+", first_address] }\n"
            slavesFile += slave_name+str(i)+"\n"
            hostsListFile += "$slave"+str(i)+"address$\n"

        # In the following section, the master's public SSH key will be setup.
        # This is done the following way: if no key name was provided for an
        # existing public SSH key, the same key will be used as was used for
        # the slaves as well. If a key name was provided but no public SSH key,
        # it's assumed that an existing public key is already registered in
        # keystone which should be used. If a key name and a public SSH key are
        # provided, a new public key entry will be created in keystone with the
        # give public key and the given name.
        masterSSHKeyResource = ""
        insertMasterPublicKey = ""
        if SSHPublicKeyName=="":
            masterSSHKeyEntry = "{ get_resource: sshpublickey }"
        else:
            insertMasterPublicKey = "su ubuntu -c \"cat /home/ubuntu/.ssh/id_rsa.pub >> /home/ubuntu/.ssh/authorized_keys\"\n"
            if SSHMasterPublicKey=="":
                masterSSHKeyEntry = SSHPublicKeyName
            else:
                masterSSHKeyResource = "  users_public_key:\n" \
                                       "    type: OS::Nova::KeyPair\n" \
                                       "    properties:\n" \
                                       "      name: " + SSHPublicKeyName + "\n" \
                                       "      public_key: " + SSHMasterPublicKey + "\n\n"
                masterSSHKeyEntry = "{ get_resource: users_public_key }"

        # if master has to act as a slave as well, set variable accordingly
        masterasslave = ""
        if slaveOnMaster==True:
            masterasslave = master_name+"\n"

        # setup bash script for master (write replace{r,e}s into dictionary and
        # replace them one by one
        replaceDict = { "$master.id_rsa$": master_id_rsa,
                        "$master.id_rsa.pub$": master_id_rsa_pub,
                        "$yarn-site.xml$": yarn_site_xml,
                        "$core-site.xml$": core_site_xml,
                        "$mapred-site.xml$": mapred_site_xml,
                        "$hdfs-site.xml$": hdfs_site_xml,
                        "$hadoop-env.sh$": hadoop_env_sh,
                        "$masternodeasslave$": masterasslave,
                        "$slavesfile$": slavesFile,
                        "$hostsfilecontent$": hostFileContent,
                        "$forloopslaves$": forLoopSlaves,
                        "$for_loop_slaves$": hostsListFile,
                        "$insert_master_pub_key$": insertMasterPublicKey,
                        "$disk_id$": diskId
                        }
        for key, value in replaceDict.iteritems():
            masterBash = masterBash.replace(key, value)

        # add some spaces in front of each line because the bash script has to
        # be indented within the Heat template
        masterBashLines = masterBash.splitlines(True)
        masterbash = ""
        for line in masterBashLines:
            masterbash += ' '*14+line

        # does the user want to have a floating IP created?
        floatingIpResource = ""
        floatingIpAssoc = ""
        externalIpOutput = ""

        # if a floating IP is to be setup for the master, the variables have to be set accordingly
        if True == withFloatingIP:
            ipid = floatingIpId
            floatingIpAssoc = "  floating_ip_assoc:\n" \
                              "    type: OS::Neutron::FloatingIPAssociation\n" \
                              "    properties:\n" \
                              "      floatingip_id: "
            if floatingIpId=="":
                floatingIpResource = "  hadoop_ip:\n" \
                                     "    type: OS::Neutron::FloatingIP\n" \
                                     "    properties:\n" \
                                     "      floating_network: \""+externalNetwork+"\"\n\n"
                floatingIpAssoc += "{ get_resource: hadoop_ip }"
                externalIpOutput = "  external_ip:\n" \
                                   "    description: The IP address of the deployed master node\n" \
                                   "    value: { get_attr: [ hadoop_ip, floating_ip_address ] }\n\n"
            else:
                floatingIpAssoc = floatingIpAssoc+floatingIpId
            floatingIpAssoc += "\n      port_id: { get_resource: hadoop_port }\n\n"

        # the cluster's heat template will have to be configured
        replaceDict = {"$master_bash.sh$": masterbash,
                       "$paramsslave$": paramsSlave,
                       "$slaves$": slaves,
                       "$master_image$": masterImage,
                       "$slave_image$": slaveImage,
                       "$masternode$": master_name,
                       "$slavenode$": slave_name,
                       "$master_flavor$": masterFlavor,
                       "$slave_flavor$": slaveFlavor,
                       "$master_ssh_key_entry$": masterSSHKeyEntry,
                       "$users_ssh_public_key$": masterSSHKeyResource,
                       "$floating_ip_resource$": floatingIpResource,
                       "$floating_ip_assoc$": floatingIpAssoc,
                       "$external_ip_output$": externalIpOutput,
                       "$subnet_cidr$": subnet_cidr,
                       "$subnet_gw_ip$": subnet_gw_ip,
                       "$subnet_allocation_pool_start$":
                           subnet_allocation_pool_start,
                       "$subnet_allocation_pool_end$":
                           subnet_allocation_pool_end,
                       "$subnet_dns_servers$": subnet_dns_servers,
                       "$ssh_cluster_pub_key$": "ssh_pub_key_"+randomstring,
                       "$hadoop_security_group$": "security_group_"+randomstring,
                        "$network_name$": "network_"+randomstring,
                       "$external_network$": externalNetwork

                    }

        for key, value in replaceDict.iteritems():
            clusterTemplate = clusterTemplate.replace(key, value)

        # for debugging purposes, the template can be saved locally
        if saveToLocalPath is not "":
            try:
                f = open( saveToLocalPath,"w")
                f.write(clusterTemplate)
                f.close()
            except:
                LOG.info("Couldn't write to location "+saveToLocalPath)

        # debug output should be implemented as a parameter
        #   LOG.debug(clusterTemplate)
        # self.deployTemplate = clusterTemplate

        # deploy the created template
        if not noDeployment:
            return clusterTemplate
            # self.hadoop_master = self.deployer.deploy(self.deployTemplate,
            #                                           self.token,
            #                                           name=clusterName+"_"+str(uuid.uuid1()))
            # LOG.info('Hadoop stack ID: ' + self.hadoop_master)

class Provision(Task):
    def __init__(self, entity, extras):
        Task.__init__(self, entity, extras, state='provision')

    def run(self):
        LOG.debug("running provisioning")
        self.start_time = time.time()
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'provision',
                    'phase_event': 'start',
                    'response_time': 0,
                    }
        LOG.debug(json.dumps(infoDict))
        self.entity.attributes['mcn.service.state'] = 'provision'

        # Do provision work here

        elapsed_time = time.time() - self.start_time
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'provision',
                    'phase_event': 'done',
                    'response_time': elapsed_time,
                    }
        LOG.debug(json.dumps(infoDict))
        return self.entity, self.extras

class Retrieve(Task):
# the retrieve task will return the external IP of the created master VM as header value externalIP

    def __init__(self, entity, extras):
        Task.__init__(self, entity, extras, 'retrieve')

    def run(self):
        LOG.debug("running retrieve")
        self.start_time = time.time()
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'retrieve',
                    'phase_event': 'start',
                    'response_time': 0,
                    }
        LOG.debug(json.dumps(infoDict))
        self.entity.attributes['mcn.service.state'] = 'retrieve'

        # the stack's identifier needs to be read from the locally saved data
        soid = self.entity.identifier
        tempSO = SOInstanceManager.getSO(soid)
        stackID = tempSO.data[0]['stack']['id']

        # a heat client needs to be acquired which will provide the connection to OpenStack
        heatClient = ClientProvider.getOrchestrator(self.entity.attributes)

        # the current stack contains the data about the output values
        curstack = heatClient.stacks.get(stackID)

        # if no external IP has been assigned (because a possible error happened)
        externalIP = "none"

        # later, all outputs will be iterated and the external_ip one chosen for status value
        for element in curstack.outputs:
            if element['output_key']=='external_ip' and element['output_value'] is not None:
                LOG.debug("external IP: "+element['output_value'])
                externalIP = element['output_value']
                break

        # the value will be saved among the attributes which will be returned to the user
        self.entity.attributes['externalIP'] = copy.deepcopy(externalIP)

        elapsed_time = time.time() - self.start_time
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'retrieve',
                    'phase_event': 'done',
                    'response_time': elapsed_time,
                    }
        LOG.debug(json.dumps(infoDict))
        return self.entity, self.extras

# can only be executed when provisioning is complete
class Update(Task):
    def __init__(self, entity, extras, updated_entity):
        Task.__init__(self, entity, extras, state='update')
        self.new = updated_entity

    def run(self):
        LOG.debug("running update")
        self.start_time = time.time()
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'update',
                    'phase_event': 'start',
                    'response_time': 0,
                    }
        LOG.debug(json.dumps(infoDict))
        self.entity.attributes['mcn.service.state'] = 'update'

        # Do update work here

        elapsed_time = time.time() - self.start_time
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'update',
                    'phase_event': 'done',
                    'response_time': elapsed_time,
                    }
        LOG.debug(json.dumps(infoDict))
        return self.entity, self.extras


class Destroy(Task):
    def __init__(self, entity, extras):
        Task.__init__(self, entity, extras, state='destroy')
        self.entity = entity
        self.extras = extras

    def run(self):
        LOG.debug("running destroy")
        self.start_time = time.time()
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'destroy',
                    'phase_event': 'start',
                    'response_time': 0,
                    }
        LOG.debug(json.dumps(infoDict))
        self.entity.attributes['mcn.service.state'] = 'destroy'

        # Do destroy work here

        # the stack's ID has to be fetched in order for the stack to be deleted by the heatClient's request
        heatClient = ClientProvider.getOrchestrator(self.entity.attributes)
        soid = self.entity.identifier
        tempSO = SOInstanceManager.getSO(soid)
        body = {
            'stack_id': tempSO.data[0]['stack']['id']
        }

        heatClient.stacks.delete(**body)

        # the SO can be deleted again as the stack has been deleted too by this moment
        SOInstanceManager.deleteSO(soid)

        elapsed_time = time.time() - self.start_time
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'destroy',
                    'phase_event': 'done',
                    'response_time': elapsed_time,
                    }
        LOG.debug(json.dumps(infoDict))
        return self.entity, self.extras
