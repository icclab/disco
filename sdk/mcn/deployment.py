#   Copyright (c) 2013-2015, Intel Performance Learning Solutions Ltd, Intel Corporation.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Module for the Deployment of Service Instance.
"""

import uuid

from heatclient import client

HEAT_VERSION = '1'


class Deployer(object):
    """
    Used to interact with the deployment module.
    """

    def __init__(self, endpoint):
        """
        Initializes helper for deployment.

        :param endpoint: endpoint of the CC internal deployment service.
        """
        pass

    def deploy(self, template, token, **kwargs):
        """
        Deploy the stack define by a template. Will return identifier for this
        stack.

        :param template: The template.
        :param token: token for this request.
        :param kwargs: Optional arguments.
        """
        raise NotImplementedError()

    def update(self, identifier, template, token, **kwargs):
        """
        Updates an already deployed stack.

        :param identifier: Identifier of a previously deployed stack.
        :param token: token for this request.
        :param kwargs: Optional arguments.
        """
        raise NotImplementedError()

    def dispose(self, identifier, token):
        """
        Disposes an deployed stack.

        :param identifier: Identifier of a previously deployed stack.
        :param token: token for this request.
        """
        raise NotImplementedError()

    def get_template(self, identifier, token):
        """
        Retrieves the template describing the current instantiation of
        the stack.

        :param identifier: Identifier of a previously deployed stack.
        :param token: token for this request.
        """
        raise NotImplementedError()

    def details(self, identifier, token):
        """
        Retrieve details of the stack.

        :param identifier: Identifier of a previously deployed stack.
        :param token: token for this request.
        """
        raise NotImplementedError()

    def check_output(self, field_name, identifier, token):
        """
        Check the results of a specific field in the outputs dictionary.
        None if not yet found.

        :param field_name: Name of the field as defined in the template.
        :param identifier: Identifier of a previously deployed stack.
        :param token: token for this request.
        """
        raise NotImplementedError()


class HeatDeployer(Deployer):
    """
    Used to interact with the deployment module (in this case Heat).
    """

    def __init__(self, endpoint):
        """
        Initializes helper for deployment.

        :param endpoint: endpoint of the CC internal deployment service.
        """
        self.endpoint = endpoint

    def deploy(self, template, token, **kwargs):
        """
        Deploy the stack define by a template. Will return identifier for this
        stack.

        :param template: The template.
        :param token: token for this request.
        :param kwargs: Optional arguments.
        """
        if 'name' in kwargs:
            name = kwargs['name']
            kwargs.pop('name')
        else:
            # needs to start with letter!
            name = 'stack_' + str(uuid.uuid1())

        heat = client.Client(HEAT_VERSION, self.endpoint, token=token,
                             **kwargs)

        body = {'stack_name': name,
                'template': template}

        if 'parameters' in kwargs:
            body['parameters'] = kwargs['parameters']

        tmp = heat.stacks.create(**body)

        return tmp['stack']['id']

    def update(self, identifier, template, token, **kwargs):
        """
        Updates an already deployed stack.

        :param identifier: Identifier of a previously deployed stack.
        :param token: token for this request.
        :param kwargs: Optional arguments.
        """
        heat = client.Client(HEAT_VERSION, self.endpoint, token=token,
                             **kwargs)

        body = {'template': template}
        if 'parameters' in kwargs:
            body['parameters'] = kwargs['parameters']

        heat.stacks.update(identifier, **body)

    def dispose(self, identifier, token):
        """
        Disposes an deployed stack.

        :param identifier: Identifier of a previously deployed stack.
        :param token: token for this request.
        """
        heat = client.Client(HEAT_VERSION, self.endpoint, token=token)
        return heat.stacks.delete(identifier)

    def get_template(self, identifier, token):
        """
        Retrieves the template describing the current instantiation of
        the stack.

        :param identifier: Identifier of a previously deployed stack.
        :param token: token for this request.
        """
        heat = client.Client(HEAT_VERSION, self.endpoint, token=token)
        res = heat.stacks.template(identifier)

        return res

    def details(self, identifier, token):
        """
        Retrieve details of the stack.

        :param identifier: Identifier of a previously deployed stack.
        :param token: token for this request.
        """
        heat = client.Client(HEAT_VERSION, self.endpoint, token=token)
        stk = heat.stacks.get(identifier).to_dict()

        # FYI: stack states are here: http://docs.aws.amazon.com/
        # AWSCloudFormation/latest/UserGuide/using-cfn-describing-stacks.html

        res = {'state': stk['stack_status'],
               'name': stk['stack_name'],
               'id': stk['id']}

        if 'outputs' in stk:
            res['output'] = stk['outputs']

        return res

    def check_output(self, field_name, identifier, token):
        """
        Check the results of a specific field in the outputs dictionary.
        None if not yet found.

        :param field_name: Name of the field as defined in the template.
        :param identifier: Identifier of a previously deployed stack.
        :param token: token for this request.
        """
        res = None

        heat = client.Client(HEAT_VERSION, self.endpoint, token=token)
        stk = heat.stacks.get(identifier).to_dict()

        if 'outputs' in stk:
            for item in stk['outputs']:
                if item['output_key'] == field_name:
                    res = item['output_value']

        return res


class AWSDeployer(Deployer):
    """
    Deploys on AWS public cloud.
    """
