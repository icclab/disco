# Copyright (c) 2017. Zuercher Hochschule fuer Angewandte Wissenschaften
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# Author: Balazs Meszaros

import copy
import json
import time
import uuid

from OpenstackDeployer import OpenstackDeployer
from sm.log import LOG
from sm.managers.Disco import Disco
from sm.managers.generic import Task
from sm.config import CONFIG
from OpenstackDisco import OpenstackDisco
from FileDeployer import FileDeployer

__author__ = 'balazs'

HEAT_VERSION = '1'

class DeployerFactory:
    @staticmethod
    def get_deployer(arguments, extras):
        attributes = {}
        for key, value in arguments.iteritems():
            if key.startswith("icclab.disco.deployer."):
                attributes[key.replace("icclab.disco.deployer.","")] = value

        if "type" in attributes:
            if attributes["type"]=="FileDeployer":
                return FileDeployer(attributes)

        # default case: OpenstackDeployer
        attributes["design_uri"] = CONFIG.get('service_manager', 'design_uri',
                                              '')
        attributes["token"] = extras["token"]
        attributes["stack_name"] = 'disco_' + str(uuid.uuid1())
        attributes["tenant_name"] = extras["tenant_name"]
        return OpenstackDeployer(attributes)


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

    def merge_dict(self, source, destination):
        """
        run me with nosetests --with-doctest file.py

        >> > a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' }
        } }
        >> > b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' }
        } }
        >> > merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog',
        'fail' : 'cat', 'number' : '5' } } }
        True
        """
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                self.merge_dict(value, node)
            else:
                destination[key] = value
        return destination

    def run(self):
        try:
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

            deployer = DeployerFactory.get_deployer(self.entity.attributes,self.extras)

            framework_directory = CONFIG.get('disco','framework_directory','')

            disco_config = {"deployer": deployer, "framework_directory": framework_directory, "root_component": "heat", "root_component_state": "end"}
            discoinst = OpenstackDisco(disco_config, self.entity.attributes)

            #TODO: make dependency to add to a configuration
            # dependencies as {'dependency1': {'state1': {'value1': 'possible value','value2': None},
            #                                    ...},
            #                  'dependency2': {}
            #                 }
            # dependencies have to be injected before resolving dependencies as
            dependencies = None
            try:
                if 'icclab.disco.dependencies.inject' in self.entity.attributes:
                    exec("dependencies = %s" % self.entity.attributes['icclab.disco.dependencies.inject'] )

                    # dependencies have to be injected into shell (state: end) component as that one provides direct access to bash
                    # build dependency dictionary:
                    deps = {}
                    for dep_name,dep_state in dependencies.items():
                        if dep_state=="":
                            dep_state="default"
                        deps[dep_name] = {dep_state:{}}
                    discoinst.inject_dependency("shell", {"end": deps})
            except Exception as e:
                self.entity.attributes['disco_status'] = 'dependency injection ' \
                                                         'went wrong: %s' % e.message
                self.entity.attributes['status'] = "deployment error: exception " \
                                                   "at the included dependencies " \
                                                   "- please refer to manual"
                self.entity.attributes['stackid'] = ""

                #
                return self.entity, self.extras

            # dependencies have to be resolved before property injection as the properties will require those same components
            discoinst.resolve_dependencies()

            # here, the requested properties are extracted from the HTTP request and inserted into the components
            properties = {}
            for prop_name, prop_value in self.entity.attributes.iteritems():
                if prop_name.startswith("icclab.disco.components."):
                    property = prop_name.split(".")
                    component_name = property[-2]
                    property_name = property[-1]
                    if component_name not in properties:
                        properties[component_name] = {}
                    properties[component_name][property_name] = prop_value

            # at this point, some individual property settings can be done
            properties = self.merge_dict({'heat': {'mastername': 'disco-manager', 'slavename': 'disco-worker'}},properties)
            discoinst.inject_requested_properties(properties)

            stackinfo = discoinst.deploy(CONFIG.get('service_manager', 'design_uri', ''),
                                         self.entity.attributes['icclab.disco.deployer.username'],
                                         self.entity.attributes['icclab.disco.deployer.password'],
                                         self.extras['tenant_name'],
                                         self.entity.attributes['icclab.disco.components.heat.masterflavor']
                                         )
            if not issubclass(stackinfo.__class__,Exception):
                self.entity.attributes['stackid'] = stackinfo['stack']['id']
            else:
                self.entity.attributes['status'] = "deployment didn't work out because: %(1)s - %(2)s (%(3)s)" % {"1": str(stackinfo.error['title']), "2": str(stackinfo.error['explanation']),"3": str(stackinfo.error['error']['message'])}
                self.entity.attributes['stackid'] = ""

        except Exception as e:
            LOG.debug(e.message)
        return self.entity, self.extras


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

        argument = {
            'design_uri': CONFIG.get('service_manager', 'design_uri', ''),
            'username': self.entity.attributes['icclab.disco.deployer.username'],
            'tenant_name': self.extras['tenant_name'],
            'password': self.entity.attributes['icclab.disco.deployer.password'],
            'stack_name': 'disco_' + str(uuid.uuid1()),
            'region': self.entity.attributes['icclab.disco.deployer.region'],
            'token': self.extras['token']
            }
        deployer = OpenstackDeployer(argument)

        framework_directory = CONFIG.get('disco','framework_directory','')

        disco_config = {"deployer": deployer, "framework_directory": framework_directory, "root_component": "heat", "root_component_state": "end"}
        discoinst = OpenstackDisco(disco_config, self.entity.attributes)

        if self.entity.attributes['stackid'] is not "":
            stackinfo = discoinst.retrieve(self.entity.attributes['stackid'], None)
            try:
                for output in stackinfo:
                    if output['output_value'] == None:
                        output['output_value'] = ""
                    self.entity.attributes[output['output_key']] = output['output_value']
                current_stack = deployer.hc.stacks.get(                    self.entity.attributes['stackid'])
                self.entity.attributes['stack_status'] = copy.deepcopy(                    current_stack.stack_status)

            except:
                self.entity.attributes['external_ip'] = 'none'
        else:
            self.entity.attributes['disco_status'] = 'nothing here right now'

        # this has to be done because Hurtle doesn't convert a multiline string into a valid JSON
        if "ssh_private_key" in self.entity.attributes:
            self.entity.attributes["ssh_private_key"] = self.entity.attributes["ssh_private_key"].replace("\n","\\n")

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
        #TODO: following might lead to problems if icclab.disco.deployer.* is used differently
        argument = {
            'design_uri': CONFIG.get('service_manager', 'design_uri', ''),
            'username': self.entity.attributes['icclab.disco.deployer.username'],
            'tenant_name': self.extras['tenant_name'],
            'password': self.entity.attributes['icclab.disco.deployer.password'],
            'stack_name': 'disco_' + str(uuid.uuid1()),
            'region': self.entity.attributes['icclab.disco.deployer.region'],
            'token': self.extras['token']
            }
        deployer = OpenstackDeployer(argument)

        framework_directory = CONFIG.get('disco','framework_directory','')

        disco_config = {"deployer": deployer, "framework_directory": framework_directory, "root_component": "shell", "root_component_state": "end"}
        discoinst = OpenstackDisco(disco_config, self.entity.attributes)

        stackinfo = discoinst.delete(self.entity.attributes['stackid'])


        elapsed_time = time.time() - self.start_time
        infoDict = {
                    'sm_name': self.entity.kind.term,
                    'phase': 'destroy',
                    'phase_event': 'done',
                    'response_time': elapsed_time,
                    }
        LOG.debug(json.dumps(infoDict))
        return self.entity, self.extras
