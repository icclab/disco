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
from novaclient import client as novaclient
import urllib2
from urllib2 import Request
from status import Status
import time
import json
import copy
import os
import ConfigParser

from frameworkfactory import FrameworkFactory

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
    def getOrchestrator( extras ):

        # first, a connection to keystone has to be established in order to load the service catalog for the orchestration endpoint (heat)
        # the design_uri has to be given in the sm.cfg file so that no other OpenStack deployment can be used
        kc = keystoneclient.Client(auth_url=CONFIG.get('service_manager','design_uri',''),
                                   username=extras['username'],
                                   password=extras['password'],
                                   tenant_name=extras['tenant_name']
                                   )

        # get the orchestration part of the service catalog
        orch = kc.service_catalog.get_endpoints(service_type='orchestration',
                                                region_name=extras['region'],
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

    def dep_resolve(self, framework, resolved, unresolved):
        unresolved.append(framework)
        for fw, deps in framework.get_dependencies().iteritems():
            if not self.list_contains_fw(resolved, fw):
                if self.list_contains_fw(unresolved, fw):
                    raise Exception('Circular reference detected: %s -&gt; %s' % (framework, fw))
                self.dep_resolve(FrameworkFactory.get_framework(fw,self,deps), resolved, unresolved)
            elif len(deps) is not 0:
                # here, the new requirements have to be inserted into existing framework instance
                # if no new attributes are to be inserted, no call necessary as the framework will be installed anyway
                self.add_attributes_to_fw(deps, fw, resolved)
        resolved.append(framework)
        unresolved.remove(framework)

    def list_contains_fw(self, fwList, fwName):
        for fw in iter(fwList):
            if fw.get_name()==fwName:
                return True
        return False

    def add_attributes_to_fw(self, attrs, fwname, list):
        for fw in iter(list):
            if fw.get_name()==fwname:
                fw.add_required_attributes(attrs)
        pass

    def get_dep(self, fw, neededList):
        dependencyKeys = fw.get_dependencies().keys()

        for newFwName in iter(dependencyKeys):
            if not self.list_contains_fw(neededList, newFwName):
                newFw = FrameworkFactory.get_framework(newFwName,None,None)
                neededList.append(newFw)
                self.get_dep(newFw, neededList)

    # inserts variable values into framework to be used
    def insert_variables_into_fw(self, fw, fwList):
        # iterate over each framework which current framework depends on
        for fwname, fwattrs in fw.get_dependencies().items():
            for framework in fwList:
                # this framework's values are needed
                if framework.get_name()==fwname:
                    # the framework's entry will be updated with every value the respective framework provides
                    #TODO: should only be done with the required values
                    # fw.get_dependencies().pop(framework.get_name())
                    curDict = fw.get_dependencies()
                    curDict.update(framework.get_variables())
            pass

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

        # set attributes member variable
        self.attributes = self.entity.attributes

        # the rootFolder is needed in order to load the config files
        self.rootFolder = CONFIG.get('disco','root_folder')
        if self.rootFolder=="":
            # if no rootFolder has been provided, take the path it's located
            # within the Docker image
            self.rootFolder = "data/"

        # setup parser for config file
        self.config = ConfigParser.RawConfigParser()
        self.config.read(os.path.join(self.rootFolder,'defaultSettings.cfg'))

        # retrieve the Heat template which will setup the cluster according to the specifications within the given http attributes
        heatTemplate = self.__get_heat_template(attributes=self.entity.attributes)

        # If heatTemplate is empty, nothing should be deployed. This can happen if the according debug setting is set to not deploying.
        if heatTemplate != "":

            # deploy the Heat orchestration template on OpenStack:
            heatClient=ClientProvider.getOrchestrator(self.extras)

            randomstring = str(uuid.uuid1())

            # set the required attributes (stack name and Heat template) to what is needed
            curStackName = 'disco_'+randomstring
            body = {
                'stack_name': curStackName,
                'template': heatTemplate
            }
            LOG.debug('the stack\'s name is '+body['stack_name'])

            deploymentCount = 1
            try:
                deploymentCount = int(self.getAttr('icclab.haas.cluster.deploymentcount'))
            except:
                pass

            for i in range(0, deploymentCount):
                print i
            # here is where the actual SO deployment happens
            #TODO
            tmp = heatClient.stacks.create(**body)

            # the return value will be saved locally so it can be retrieved for future operations
            SOInstanceManager.addSO(SOContainer(tmp),self.entity.identifier)
            LOG.debug("new stack's ID: "+tmp['stack']['id'])

        return self.entity, self.extras


    # this function will return the first of following values in the order
    # of occurrence:
    #   - given by the user during instantiation
    #   - set as a default value in the config file
    #   - an empty string
    def getAttr(self, attrName):
        if(attrName in self.attributes):
            return self.attributes[attrName]
        else:
            try:
                retVal = self.config.get('cluster',attrName)
                return retVal
            except:
                return ""

    def get_master_name(self):
        return self.master_name

    def getFileContent(self,fileName):
        f = open(os.path.join(self.rootFolder, fileName))
        retVal = f.read()
        f.close()
        return retVal

    def __get_heat_template(self, attributes):
        randomstring = "-"+str(uuid.uuid1())


        LOG.info("deploying stack...")

        # the needed variables for the Heat Orchestration Template will be set
        # on the following lines; the function getAttr() is returning the
        # appropriate value. As an empty value cannot be used for int/float
        # conversion, they have to be set within a try-except block.
        slaveCount = 1
        try:
            slaveCount = int(self.getAttr('icclab.haas.slave.number'))
        except:
            pass
        masterImage = self.getAttr('icclab.haas.master.image')
        slaveImage = self.getAttr('icclab.haas.slave.image')
        masterFlavor = self.getAttr('icclab.haas.master.flavor')
        slaveFlavor = self.getAttr('icclab.haas.slave.flavor')
        slaveOnMaster = True #getAttr('icclab.haas.master.slaveonmaster').lower() in ['true', '1']
        SSHPublicKeyName = self.getAttr('icclab.haas.master.sshkeyname')
        SSHMasterPublicKey = self.getAttr('icclab.haas.master.publickey')
        withFloatingIP = self.getAttr('icclab.haas.master.withfloatingip').lower() in ['true','1']
        self.master_name = self.getAttr('icclab.haas.master.name')+randomstring
        slave_name = self.getAttr('icclab.haas.slave.name')+randomstring+"-"
        subnet_cidr = self.getAttr('icclab.haas.network.subnet.cidr')
        subnet_gw_ip = self.getAttr('icclab.haas.network.gw.ip')
        subnet_allocation_pool_start = self.getAttr('icclab.haas.network.subnet.allocpool.start')
        subnet_allocation_pool_end = self.getAttr('icclab.haas.network.subnet.allocpool.end')
        subnet_dns_servers = self.getAttr('icclab.haas.network.dnsservers')
        image_id = self.getAttr('icclab.haas.master.imageid')
        floatingIpId = self.getAttr('icclab.haas.master.attachfloatingipwithid')

        externalNetwork = self.getAttr('icclab.haas.network.external')

        noDeployment = self.getAttr('icclab.haas.debug.donotdeploy').lower() in ['true','1']
        saveToLocalPath = self.getAttr('icclab.haas.debug.savetemplatetolocalpath')

        diskId = 'virtio-'+image_id[0:20]

        # masterSSHKeyEntry = ''
        # self.frameworkList = []
        # newFW = FrameworkFactory.get_framework("jdk",self,None)
        # self.frameworkList.append(newFW)
        # jdkframeworkbash = newFW.get_bash()

        resolved = []
        shellFW = FrameworkFactory.get_framework("shell",self,None)
        shellFW.set_dependencies({"jdk":{"java_home":None},"hadoop":{},"spark":{}})
        self.dep_resolve(shellFW, resolved, [])

        shellframeworkbash = ''
        for framework in iter(resolved):
            self.insert_variables_into_fw(framework, resolved)
            shellframeworkbash += framework.get_bash()



        # read all the necessary files for creating the Heat template
        clusterTemplate = self.getFileContent("cluster.yaml");
        slaveTemplate = self.getFileContent("slave.yaml")
        masterBash = self.getFileContent("master_bash.sh")
        master_id_rsa = self.getFileContent("master.id_rsa").replace("\n","\\n")
        master_id_rsa_pub = self.getFileContent("master.id_rsa.pub").replace("\n","")
        jupyter_notebook_config_py = self.getFileContent("jupyter_notebook_config.py")
        zeppelin_env_sh = self.getFileContent("zeppelin-env.sh")
        # interpreter_json = getFileContent("interpreter.json")

        slaves = ""
        hostFileContent = ""
        forLoopSlaves = ""
        paramsSlave = ""
        slavesFile = ""
        hostsListFile = ""
        zooCfgFile = "tickTime=2000\ndataDir=/var/lib/zookeeper\nclientPort=2181\ninitLimit=5\nsyncLimit=2\n"

        addToZoo = 0
        if slaveOnMaster:
            addToZoo = 1
            zooCfgFile += "server.1"+self.master_name+":2888:3888\n"

        slaveTemplate = slaveTemplate.replace("$master.id_rsa.pub$",master_id_rsa_pub)
        for i in xrange(1,slaveCount+1):
            slaves += slaveTemplate.replace("$slavenumber$",str(i))
            hostFileContent += "$slave"+str(i)+"address$\t"+slave_name+str(i)+"\n"
            forLoopSlaves += " $slave"+str(i)+"address$"
            paramsSlave += "            $slave"+str(i)+"address$: { get_attr: [hadoop_slave_"+str(i)+", first_address] }\n"
            slavesFile += slave_name+str(i)+"\n"
            hostsListFile += "$slave"+str(i)+"address$\n"
            zooCfgFile += "server."+str(i+addToZoo)+"$slave"+str(i)+":2888:3888\n"

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
            masterasslave = self.master_name+"\n"

        # setup bash script for master (write replace{r,e}s into dictionary and
        # replace them one by one
        #TODO: bugfix: as dictionary is not ordered, created a list with dict-s - should be handled differently
        replaceDict = [ {"$shellframeworkbash$": shellframeworkbash},
                        {"$master.id_rsa$": master_id_rsa},
                        {"$master.id_rsa.pub$": master_id_rsa_pub},
                        {"$masternodeasslave$": masterasslave},
                        {"$slavesfile$": slavesFile},
                        {"$hostsfilecontent$": hostFileContent},
                        {"$forloopslaves$": forLoopSlaves},
                        {"$for_loop_slaves$": hostsListFile},
                        {"$insert_master_pub_key$": insertMasterPublicKey},
                        {"$disk_id$": diskId},
                        {"$jupyter_notebook_config.py$": jupyter_notebook_config_py},
                        {"$zeppelin_env_sh$": zeppelin_env_sh},
                        # "$interpreter_json$": interpreter_json,
                        ]
        for item in replaceDict:
            masterBash = masterBash.replace(item.keys()[0], item.values()[0])

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


        memVals = self.__get_hadoop_memory_values(slaveFlavor)


        # the cluster's heat template will have to be configured
        replaceDict = {"$master_bash.sh$": masterbash,
                       "$paramsslave$": paramsSlave,
                       "$slaves$": slaves,
                       "$master_image$": masterImage,
                       "$slave_image$": slaveImage,
                       "$masternode$": self.master_name,
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

        # do basic configuration
        for key, value in replaceDict.iteritems():
            clusterTemplate = clusterTemplate.replace(key, value)

        # insert memory values
        for key, value in memVals.iteritems():
            clusterTemplate = clusterTemplate.replace(key, str(value))

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

    def __get_hadoop_memory_values(self, flavorID):
        nc = novaclient.Client("2",
                               self.extras['username'],
                               self.extras['password'],
                               self.extras['tenant_name'],
                               CONFIG.get('service_manager','design_uri',''),
                               region_name=self.extras['region']
                               )
        curFlavor = None
        try:
            curFlavor = nc.flavors.find(id=flavorID)
        except:
            print "didn't find flavor with ID "+flavorID

        # curFlavor.ram [MB], curFlavor.disk [GB]

        # class test (object):
        #     def __init__(self):
        #         self.ram = 8192
        #         self.vcpus = 8
        #         self.disk = 20
        # curFlavor = test()

        # determine the reserved memory for system
        # [RAM in MB, reserved system memory in MB]
        sysMem = 0
        resMemRecommendation = [[4*1024,1*1024],[8*1024,2*1024],[16*1024,2*1024],[24*1024,4*1024],[48*1024,6*1024],[64*1024,8*1024],[72*1024,8*1024],[96*1024,12*1024],[128*1024,24*1024],[256*1024,32*1024],[512*1024,64*1024]]
        for curMem in resMemRecommendation:
            if curMem[0]<=curFlavor.ram:
                sysMem = curMem[1]
            else:
                break

        # determine the minimum container memory size
        # [RAM in MB, Container memory in MB]
        minContSizeRecommendation = [[0,256],[4*1024,512],[8*1024,1024],[24*1024,2048]]
        for curSize in minContSizeRecommendation:
            if (curFlavor.ram-sysMem)>curSize[0]:
                minContSize = curSize[1]
            else:
                break

        # #containers on each slave node
        containerCount = min(
            (curFlavor.ram-sysMem)/minContSize,
            2*curFlavor.vcpus,
            1.8*curFlavor.disk
        )

        containerMemory = max(minContSize, (curFlavor.ram-sysMem) / containerCount)

        memVals = { '$mapreduce.map.java.opts$':              '-Xmx'+str(int(0.8*containerMemory))+'m',
                    '$mapreduce.reduce.java.opts$':           '-Xmx'+str(int(0.8*2*containerMemory))+'m',
                    '$mapreduce.map.memory.mb$':              int(containerMemory),
                    '$mapreduce.reduce.memory.mb$':           int(2*containerMemory),
                    '$yarn.app.mapreduce.am.resource.mb$':	int(2*containerMemory),
                    '$yarn.scheduler.minimum-allocation-mb$':	int(containerMemory),
                    '$yarn.scheduler.maximum-allocation-mb$':	int(containerCount*containerMemory),
                    '$yarn.nodemanager.resource.memory-mb$':  int(containerCount*containerMemory),
                    '$yarn.app.mapreduce.am.command-opts$':   '-Xmx'+str(int(0.8*2*containerMemory))+'m'
                    }
        return memVals

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
        heatClient = ClientProvider.getOrchestrator(self.extras)

        # the current stack contains the data about the output values
        curstack = heatClient.stacks.get(stackID)

        # if no external IP has been assigned (because a possible error happened)
        externalIP = "none"

        try:
            self.entity.attributes['stack_status'] = copy.deepcopy(curstack.stack_status)
            self.entity.attributes['stack_status_reason'] = copy.deepcopy(curstack.stack_status_reason)

            # later, all outputs will be iterated and the external_ip one chosen for status value
            for element in curstack.outputs:
                if element['output_key']=='external_ip' and element['output_value'] is not None:
                    LOG.debug("external IP: "+element['output_value'])
                    externalIP = element['output_value']
                    break

            # the value will be saved among the attributes which will be returned to the user
            self.entity.attributes['externalIP'] = copy.deepcopy(externalIP)
        except:
            self.entity.attributes['externalIP'] = "none"
            pass


        if externalIP is not "none":
            statusCode, statusText = self.__getState( externalIP, "Hadoop" )
        else:
            statusCode = 0
            statusText = "Cluster is being deployed by OpenStack"

        self.entity.attributes['statusCode'] = copy.deepcopy(str(statusCode))
        self.entity.attributes['statusText'] = copy.deepcopy(statusText)

        elapsed_time = time.time() - self.start_time
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'retrieve',
                    'phase_event': 'done',
                    'response_time': elapsed_time,
                    }
        LOG.debug(json.dumps(infoDict))
        return self.entity, self.extras

    def __getState(self, ip, framework ):
        if ip is None:
            return 0, "not deployed by OpenStack"

        state = None
        try:
            # timeout of 0.1 seconds needed as without it, this call would be stuck;
            # maybe less would be enough, but it always depends on the network connection
            response = urllib2.urlopen(Request('http://'+ip+':8084/status.log'), None, 0.1)
            state = int(response.read())
        except:
            pass

        if state is None:
            return 0, "waiting for framework deployment on cluster"

        statusArray = Status.getStatusArray(framework)
        if len(statusArray) <= state:
            return -1, "there is no state like this"
        return state, statusArray[ state ]

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
        heatClient = ClientProvider.getOrchestrator(self.extras)
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
