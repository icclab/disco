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

from Disco import Disco
from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client
from OpenstackDeployer import HeatclientProvider
import uuid

NOVA_CLIENT_VERSION = 2

class OpenstackDisco(Disco):
    """
    OpenstackDisco is an intermediary class between class Disco and Hurtle
    which abstracts a few properties of Openstack such as the suspension /
    resume of stacks or the parametrisation of Openstack related entities
    """
    deployer = None
    params = None

    def __init__(self, disco_config, params):
        Disco.__init__(self, disco_config, params)

    def get_nova_client(self, auth_url, username, password, project_name, region):
        """
        the Nova client is used for retrieving data of Openstack components
        :param auth_url: OS_AUTH_URL
        :param username: OS_USERNAME
        :param password: OS_PASSWORD
        :param project_name: OS_TENANT_NAME
        :param region: OS_REGION
        :return: nova client instance
        """
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(auth_url     = auth_url,
                                        username     = username,
                                        password     = password,
                                        project_name = project_name)
        sess = session.Session(auth=auth)
        nova = client.Client(NOVA_CLIENT_VERSION, session=sess, region_name=region)
        return nova

    def deploy(self, auth_url, username, password, project_name, region, flavor_id):
        """
        deployment of the cluster on Openstack
        :param auth_url: OS_AUTH_URL
        :param username: OS_USERNAME
        :param password: OS_PASSWORD
        :param project_name: OS_TENANT_NAME
        :param region: OS_REGION
        :param flavor_id: flavor of the deployed slaves
        :return: return value of the base class' deploy method
        """

        # here, parameters have to be inserted into the "parameter" component
        nova_client = self.get_nova_client( auth_url,
                                            username,
                                            password,
                                            project_name,
                                            region)

        # retrieval of the flavor to be deployed for its properties
        deployed_flavor = nova_client.flavors.get(flavor_id)

        # set the required properties within the parameters component
        parameters = {
            'parameters':
                {
                    'disksize': str(deployed_flavor.disk),
                    'memorysize': str(deployed_flavor.ram),
                    'vcpunumber': str(deployed_flavor.vcpus),
                    'uuid': str(uuid.uuid4())
                }
        }
        Disco.inject_requested_properties(self,parameters)

        # call the base class' deploy method and return its return value
        return Disco.deploy(self)

    def suspend(self):
        """
        suspend the currently deployed cluster
        """
        hc = HeatclientProvider.get_heatclient({
            "design_uri": self.params['icclab.disco.deployer.auth_url'],
            "username": self.params['icclab.disco.deployer.username'],
            "password": self.params['icclab.disco.deployer.password'],
            "tenant_name": self.params['icclab.disco.deployer.tenant_name'],
            "region": self.params['icclab.disco.deployer.region']
        })
        hc.actions.suspend(self.params["stackid"])

    def resume(self):
        """
        resume the suspended cluster
        """
        hc = HeatclientProvider.get_heatclient({
            "design_uri": self.params['icclab.disco.deployer.auth_url'],
            "username": self.params['icclab.disco.deployer.username'],
            "password": self.params['icclab.disco.deployer.password'],
            "tenant_name": self.params['icclab.disco.deployer.tenant_name'],
            "region": self.params['icclab.disco.deployer.region']
        })
        hc.actions.resume(self.params["stackid"])
