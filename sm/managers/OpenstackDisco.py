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

NOVA_CLIENT_VERSION = 2

class OpenstackDisco(Disco):
    deployer = None
    params = None

    def __init__(self, disco_config, params):
        Disco.__init__(self, disco_config, params)

    def get_nova_client(self, auth_url, username, password, project_name, region):
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(auth_url     = auth_url,
                                        username     = username,
                                        password     = password,
                                        project_name = project_name)
        sess = session.Session(auth=auth)
        nova = client.Client(NOVA_CLIENT_VERSION, session=sess, region_name=region)
        return nova

    def deploy(self, auth_url, username, password, project_name, region, flavor_id):
        # here, parameters have to be inserted into the "parameter" component
        nova_client = self.get_nova_client(auth_url,username,password,project_name, region)
        deployed_flavor = nova_client.flavors.get(flavor_id)
        # deployed_flavor.{disk,vcpus,ram}
        parameters = {
            'parameters':
                {
                    'disksize': str(deployed_flavor.disk),
                    'memorysize': str(deployed_flavor.ram),
                    'vcpunumber': str(deployed_flavor.vcpus)
                }
        }
        Disco.inject_requested_properties(self,parameters)

        return Disco.deploy(self)

    def suspend(self):

        hc = HeatclientProvider.get_heatclient({
            "design_uri": self.params['icclab.disco.deployer.auth_url'],
            "username": self.params['icclab.disco.deployer.username'],
            "password": self.params['icclab.disco.deployer.password'],
            "tenant_name": self.params['icclab.disco.deployer.tenant_name'],
            "region": self.params['icclab.disco.deployer.region']
        })
        hc.actions.suspend(self.params["stackid"])

    def resume(self):
        hc = HeatclientProvider.get_heatclient({
            "design_uri": self.params['icclab.disco.deployer.auth_url'],
            "username": self.params['icclab.disco.deployer.username'],
            "password": self.params['icclab.disco.deployer.password'],
            "tenant_name": self.params['icclab.disco.deployer.tenant_name'],
            "region": self.params['icclab.disco.deployer.region']
        })
        hc.actions.resume(self.params["stackid"])
