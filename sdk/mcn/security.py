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
Module can handle request to Auth service.
"""

from keystoneclient.v2_0 import client


class AuthService(object):
    """
    Wrapping an Authenticaion service.
    """

    def __init__(self, endpoint):
        """
        Connect to keystone - wrap keystone client.

        :param endpoint: endpoint of e.g. keystone.
        """
        pass

    def verify(self, token):
        """
        Verify a given token.

        :param token: A security token.
        :param tenant_name: A optional tenant name.
        """
        raise NotImplementedError()


class KeyStoneAuthService(AuthService):
    """
    Wrapping an Authentication service - keystone.
    """

    def __init__(self, endpoint):
        """
        Connect to keystone - wrap keystone client.

        :param endpoint: endpoint of e.g. keystone.
        """
        self.endpoint = endpoint

    def verify(self, token, tenant_name='demo'):
        """
        Verify a given token.

        :param token: A security token.
        :param tenant_name: A optional tenant name.
        """
        try:
            client.Client(token=token,
                          tenant_name=tenant_name,
                          auth_url=self.endpoint)
            return True
        except:
            return False
