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
Module providing basic OCCI typing.

In your SO do:

    from sdk.mcn import occi_ext

    class MyBackend(occi_ext.Backend):

        def deploy_me(self, entity, attributes, extras):
            entity.actions = [occi_ext.PROVISION_ACTION]

        def provision_me(self, entity, attributes, extras):
            entity.actions = []

    application = occi_ext.Application(MyBackend())
"""

__author__ = 'tmetsch'

from occi import backend
from occi import core_model
from occi import wsgi

SCHEME = 'http://schemas.mobile-cloud-networking.eu/occi/service#'

DEPLOY_ACTION = core_model.Action(SCHEME, 'deploy')

PROVISION_ACTION = core_model.Action(SCHEME, 'provision')

ATTRS = {'occi.mcn.stack.state': 'immutable',
         'occi.mcn.stack.id': 'immutable'}

ORCHESTRATOR = core_model.Kind(SCHEME, 'orchestrator',
                               related=[core_model.Resource.kind],
                               attributes=ATTRS,
                               actions=[DEPLOY_ACTION,
                                        PROVISION_ACTION])


class Application(wsgi.Application):
    """
    A OCCI Application.
    """

    def __call__(self, environ, response):
        """
        Pass in token.
        """
        if 'HTTP_X_AUTH_TOKEN' not in environ:
            status = '403 Forbidden'
            headers = [('Content-type', 'text/plain')]

            response(status, headers)
            return 'X-Auth-Token required...'
        if 'HTTP_X_TENANT_NAME' not in environ:
            status = '403 Forbidden'
            headers = [('Content-type', 'text/plain')]

            response(status, headers)
            return 'X-Tenant-Name required...'
        return self._call_occi(environ, response,
                               token=environ['HTTP_X_AUTH_TOKEN'],
                               tenant_name=environ['HTTP_X_TENANT_NAME'])

    def __init__(self, so_backend, backends=None):
        """
        Initialize the OCCI app.
        """
        super(Application, self).__init__()
        self.register_backend(ORCHESTRATOR, so_backend)
        self.register_backend(DEPLOY_ACTION, so_backend)
        self.register_backend(PROVISION_ACTION, so_backend)

        if isinstance(backends, dict) and len(backends) > 0:
            for item in backends:
                self.register_backend(item, backends[item])


class Backend(backend.KindBackend, backend.ActionBackend):
    """
    A simple backend to be extended by SO implementers.
    """

    def deploy_me(self, entity, attributes, extras):
        """
        Deploy the SO instance.

        :param entity: The OCCI resource entity.
        :param attributes: The attributes given during the OCCI call.
        """
        raise NotImplementedError()

    def provision_me(self, entity, attributes, extras):
        """
        Provision the SO instance.

        :param entity: The OCCI resource entity.
        :param attributes: The attributes given during the OCCI call.
        """
        raise NotImplementedError()

    def action(self, entity, action, attributes, extras):
        """
        Handles OCCI actions.
        """
        if action not in entity.actions:
            raise AttributeError('Not applicable atm.')
        elif action == DEPLOY_ACTION:
            self.deploy_me(entity, attributes, extras)
        elif action == PROVISION_ACTION:
            self.provision_me(entity, attributes, extras)