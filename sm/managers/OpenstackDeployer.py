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

from keystoneclient.v2_0 import client as keystoneclient
from heatclient import client as heatclient
from Deployer import Deployer
import uuid
import logging

HEAT_VERSION = '1'

# ClientProvider returns the appropriate client after fetching the needed service catalog
class HeatclientProvider():
    @staticmethod
    def get_heatclient(extras):

        # first, a connection to keystone has to be established in order to load the service catalog for the orchestration endpoint (heat)
        # the design_uri has to be given in the sm.cfg file so that no other OpenStack deployment can be used
        kc = keystoneclient.Client(auth_url=extras['design_uri'],
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


class OpenstackDeployer(Deployer):

    def __init__(self, *args, **kwargs):
        """Create a heatclient instance.
        In kwargs, the following values have to be set: design_uri, username, password, tenant_name and region. These credentials need to be a valid Openstack login.
        """

        self.logger = logging.getLogger("disco")
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.stack_name = args[0]['stack_name']

        self.logger.addHandler(ch)
        self.hc = HeatclientProvider.get_heatclient(args[0])

    def deploy(self, heatTemplate):
        """Deploy given Heat template on Openstack.
        :param heatTemplate:    Heat template as a string which describes the cluster
        :return: stack.create's return value if successful, otherwise the thrown Exception
        """

        # set the required attributes (stack name and Heat template) to what is needed

        heatTemplate = heatTemplate.rstrip()

        body = {
            'stack_name': self.stack_name,
            'template': heatTemplate
        }
        self.logger.info('the stack\'s name is '+body['stack_name'])
        tmp = None
        try:
            tmp = self.hc.stacks.create(**body)
        except Exception as e:
            tmp = e
        return tmp

    def retrieve(self, stack_id):
        '''
        retrieve the requested output values given in list
        :param stack_id: ID of requested stack's outputs
        :return: each available requested output value as dictionary or None in case of exception
        '''
        current_stack = self.hc.stacks.get(stack_id)

        return_value = {}

        try:
            return current_stack.outputs
        except:
            return None

        # the value will be saved among the attributes which will be returned to the user
        return return_value

    def delete(self, stack_id):
        """
        delete will delete the stack with the given stack id from OpenStack
        :param stack_id: stack's id on OpenStack
        :return: True for successful, False otherwise
        """
        try:
            body = {
                'stack_id': stack_id
            }
            try:
                self.hc.stacks.delete(**body)
            except:
                return False
            return True
        except:
            return False
