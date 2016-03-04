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
from heatclient import client
from sm.retry_http import http_retriable_request
import time
import socket
import requests
import copy
import json

__author__ = 'balazs'

HEAT_VERSION = '1'

# This Service Manager was created in order to bypass an OpenShift installation
# and deploy the Service Orchestrator on an OpenStack VM. For this, a small
# instance has to be created on OpenStack which will only execute the SO. This
# SO itself will orchestrate the distributed computing cluster and take the
# requests for deployment, provisioning, updating and disposal.

# some global variables have to be saved so that different class instances can
# access them
soStackId = {}
stackName = {}
stateNumber = {}
stateDescription = {}

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

        try:
            self.sofloatingipid = self.entity.attributes['sofloatingipid']
        except:
            raise Exception("argument sofloatingipid not given")

        try:
            self.sofloatingip = self.entity.attributes['sofloatingip']
        except:
            raise Exception("argument sofloatingip not given")

    def run(self):
        # TODO: bad practise
        global stateNumber
        global stateDescription
        global soStackId
        global stackName

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

        # status update
        self.__status(1,"started deployment of VM on OpenStack for SO")

        # Do deploy work here
        self.__deploy_so_vm()

        # status update
        self.__status(2,"SO's VM deployment initiated; waiting to finish & start SO")

        # after the deployment, we have to wait until the VM is setup and the
        # SO is listening for connections
        # TODO: this is going to result in a problem if the SO couldn't be deployed successfully! there should be a timeout with the iteration and a treatment of each outcome
        iteration = 0
        while not self.__so_complete():
            iteration += 1
            # wait some seconds with each iteration - 5 was chosen just
            # randomly in order to not make the communication too frequent but
            # still get the result quite fast. It also depends on the OpenStack
            # installation where the SO is to be deployed. (If the deployment
            # speed is low, there is no need to test it too frequently and vice
            # versa)
            time.sleep(5)

        # the second count might not be very accurate, but it gives an estimate
        LOG.debug("it took me "+str(time.time() - self.start_time)+" seconds to deploy the SO")

        # status update
        self.__status(3,"SO running; sending deploy command to it")

        # send the deploy command to the freshly instantiated SO
        self.__deploy_to_so()

        elapsed_time = time.time() - self.start_time

        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'deploy',
                    'phase_event': 'done',
                    'response_time': elapsed_time,
                    }
        LOG.debug(json.dumps(infoDict))
        return self.entity, self.extras

    def __status(self, nr, desc):
        '''
        :param nr: number of current state
        :param desc: description of current state
        :return: none
        '''
        global stateNumber
        global stateDescription
        stateNumber[self.sofloatingip] = nr
        stateDescription[self.sofloatingip] = desc

    def __so_complete(self):
        """
        __so_complete tries to open a connection with the SO on the deployed
        OpenStack VM
        :return: True if connection has been established, else False
        """
        # TODO: check if it's really non-blocking and "restrained"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((self.sofloatingip,8080))
        sock.close()
        return result==0

    def __deploy_so_vm(self):
        global soStackId
        global stackName

        # this will be the template that deploys the SO's VM on OpenStack
        template = """heat_template_version: 2014-10-16

parameters:
resources:
  so_network:
    type: OS::Neutron::Net
    properties:
      name: so_net_$randomstring$

  so_subnet:
    type: OS::Neutron::Subnet
    properties:
      network: { get_resource: so_network }
      cidr: 192.168.19.0/24
      gateway_ip: 192.168.19.1
      dns_nameservers: ["8.8.8.8","8.8.4.4"]
      allocation_pools:
        - start: 192.168.19.2
          end: 192.168.19.254

  so_router:
    type: OS::Neutron::Router
    properties:
      external_gateway_info:
        network: external-net

  router_interface:
    type: OS::Neutron::RouterInterface
    properties:
      router_id: { get_resource: so_router }
      subnet_id: { get_resource: so_subnet }

  so_port:
    type: OS::Neutron::Port
    properties:
      network: { get_resource: so_network }
      fixed_ips:
        - subnet_id: { get_resource: so_subnet }
      security_groups: [{ get_resource: so_sec_group }]

  floating_ip_assoc:
    type: OS::Neutron::FloatingIPAssociation
    properties:
      floatingip_id: $floatingip$
      port_id: { get_resource: so_port }

  so_sec_group:
    type: OS::Neutron::SecurityGroup
    properties:
      name: so_sg_$randomstring$
      rules: [
      {"direction":"ingress","protocol":"tcp","port_range_min":"22","port_range_max":"22"},
      {"direction":"ingress","protocol":"tcp","port_range_min":"8080","port_range_max":"8080"},
      ]

  so_master:
    type: OS::Nova::Server
    properties:
      name: testso_$randomstring$
      image: $sovmimagename$
      flavor: $sovmflavor$
      key_name: $sovmsshpublickey$
      networks:
        - port: { get_resource: so_port }
      user_data: |
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
        git clone $sogitaddress$
        export DESIGN_URI='$design_uri$'
        python $soapplication$
        } 2> ~/error.log | tee ~/debug.log

outputs:
"""

        # set the needed values within the VM
        randomstring = str(uuid.uuid1())
        template = template.replace("$design_uri$",CONFIG.get('service_manager','design_uri'))
        template = template.replace("$floatingip$",self.sofloatingipid)
        template = template.replace("$randomstring$",randomstring)
        template = template.replace("$sogitaddress$",CONFIG.get('openstackso','sogitaddress'))
        template = template.replace("$soapplication$",CONFIG.get('openstackso','soapplication'))
        template = template.replace("$sovmimagename$",CONFIG.get('openstackso','sovmimagename'))
        template = template.replace("$sovmflavor$",CONFIG.get('openstackso','sovmflavor'))
        template = template.replace("$sovmsshpublickey$",CONFIG.get('openstackso','sovmsshpublickey'))


        LOG.debug('deploying template:\n'+template)

        # deyloy the Heat orchestration template on OpenStack:
        token = self.extras['token']

        # design_uri contains the keystone endpoint
        design_uri = CONFIG.get('openstackso', 'heat_endpoint', '')
        if design_uri == '':
            LOG.fatal('No design_uri parameter supplied in sm.cfg')
            raise Exception('No design_uri parameter supplied in sm.cfg')

        # get the connection handle to keytone
        heatClient = client.Client(HEAT_VERSION, design_uri, token=token)
        curStackName = 'so_'+randomstring
        body = {
            'stack_name': curStackName,
            'template': template
        }
        LOG.debug('the stack\'s name is '+body['stack_name'])

        # here is where the actual SO deployment happens
        tmp = heatClient.stacks.create(**body)

        soStackId[self.sofloatingip] = tmp['stack']['id']
        stackName[self.sofloatingip] = curStackName
        LOG.debug("new stack's ID: "+tmp['stack']['id'])
        # at this point, OpenStack has control over the SO and we can only wait

    def __deploy_to_so(self):
        # from this point on, the SO will be contacted in order to deploy the
        # distributed computing cluster
        heads = {
            'X-Auth-Token':self.extras['token'],
            'X-Tenant-Name':CONFIG.get('openstackso','tenantname'),
            'Content-Type':'text/occi',
            'Accept':'text/occi',
            'Category':'orchestrator; scheme="http://schemas.mobile-cloud-networking.eu/occi/service#"'
        }
        # TODO: "http://" and / or port will result in a problem
        r = requests.put("http://"+self.sofloatingip+':8080/orchestrator/default', headers=heads)

        # everything that has to be changed in the head is the Category which
        # is switched to deploy
        heads['Category']='deploy; scheme="http://schemas.mobile-cloud-networking.eu/occi/service#"'

        # the attributes for the SO have to be transferred to it as well
        attributeString = ",".join("%s=\"%s\"" % (key,val) for (key,val) in self.entity.attributes.iteritems())
        heads['X-OCCI-Attribute']=attributeString
        # TODO: "http://" and / or port will result in a problem
        r = requests.post("http://"+self.sofloatingip+':8080/orchestrator/default?action=deploy', headers=heads)


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

    def __init__(self, entity, extras):
        Task.__init__(self, entity, extras, 'retrieve')

        try:
            self.sofloatingip = self.entity.attributes['sofloatingip']
        except:
            raise Exception("argument sofloatingip not given")


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

        # Do retrieve work here
        self.entity.attributes['so_state_nr'] = str(stateNumber[self.sofloatingip])
        self.entity.attributes['so_state_desc'] = stateDescription[self.sofloatingip]

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

        # first, the SO has to be notified that it should destroy the computing
        # cluster...
        token = self.extras['token']
        heads = {
            'X-Auth-Token':token,
            'X-Tenant-Name':CONFIG.get('openstackso','tenantname'),
             'Content-Type':'text/occi',
             'Accept':'text/occi'
        }

        # this happens with the delete command
        self.sofloatingip = self.entity.attributes['sofloatingip']
        http_retriable_request('DELETE', "http://"+self.sofloatingip+':8080/orchestrator/default', headers=heads)

        # this time, we don't have to wait anymore until the SO's VM is
        # destroyed because it's OpenStack's duty to worry about that...so
        # let's destroy the SO's VM straight away
        global soStackId

        # design_uri contains the keystone endpoint
        design_uri = CONFIG.get('openstackso', 'heat_endpoint', '')
        if design_uri == '':
            LOG.fatal('No design_uri parameter supplied in sm.cfg')
            raise Exception('No design_uri parameter supplied in sm.cfg')

        # get the connection handle to keytone
        heatClient = client.Client(HEAT_VERSION, design_uri, token=token)

        # get the floating IP of the SO's VM
        try:
            self.sofloatingip = self.entity.attributes['sofloatingip']
        except:
            raise Exception("argument sofloatingip not given")

        try:
            from novaclient import client as novaclient

            # the following doesn't work, but maybe with nova.servers.remove_floating_ip(server,ip)
            # heatClient.v2.floating_ips.delete(self.sofloatingip)
            heatClient.stacks.delete(soStackId[self.sofloatingip])
        except:
            LOG.debug("either openstack_so_manager::heatClient or openstack_so_manager::soStackId wasn't defined")

        # at this point, the computing cluster as well as the SO's VM have been
        # deleted on OpenStack

        elapsed_time = time.time() - self.start_time
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'destroy',
                    'phase_event': 'done',
                    'response_time': elapsed_time,
                    }
        LOG.debug(json.dumps(infoDict))
        return self.entity, self.extras
