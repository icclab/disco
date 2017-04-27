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

class FileDeployer(Deployer):

    def __init__(self, args):
        self.args = args

    def deploy(self, heatTemplate):
        """Deploy given Heat template on Openstack.

        """
        saved_file = open(self.args["path"],"w")
        saved_file.write(heatTemplate)
        saved_file.close()

        return None

    def retrieve(self, stack_id, requested_output):

        return None

    def delete(self, stack_id):
        return None