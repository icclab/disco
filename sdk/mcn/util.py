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
Utility functions for easier access to services.
"""

import requests
from sdk import services
from sdk.mcn import deployment
from sdk.mcn import provisioning
from sdk.mcn import security
from sdk.mcn import monitoring


from sdk.mcn.dnsaasclient import DNSaaSClientCore

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from sdk.mcn import monitoring
from sdk.mcn import dnsaasclient 


def get_deployer(token, dtype='orchestration', **kwargs):
    """
    Returns a instance of the deployment helper.

    Return None if no deployer can be found.

    :param token: The token.
    :param dtype: Defaults to 'heat'.
    """
    if dtype == 'orchestration':
        endpoint = services.get_service_endpoint(dtype, token, **kwargs)
        if endpoint is not None:
            return deployment.HeatDeployer(endpoint)
        else:
            return None
    else:
        return None


def get_provisioner(token, stype='provisioning'):
    """
    Returns Provisioning module wrapper.

    :param token: The token.
    :param stype:  Defaults to provisioning
    """
    return provisioning.SshProvisioner()


def get_security_service(token, stype='identity'):
    """
    Returns a instance of the auth service.

    :param token: The token.
    :param dtype: Defaults to 'keystone'.
    """
    if stype == 'identity':
        endpoint = services.get_service_endpoint(stype, token)
        return security.KeyStoneAuthService(endpoint)
    else:
        return None


def get_maas(token, mtype='maas', **kwargs):
    """
    Return a instance of the monitoring helper.

    :param token: The token.
    :param mtype: Defaults to 'zabbix'
    :param kwargs: optional parameters
    """
    if kwargs['tenant_name'] is not None:
        tenant = kwargs['tenant_name']
    else:
        tenant = 'demo'

    if mtype == 'maas':
        endpoint = services.get_service_endpoint(
            'http://schemas.mobile-cloud-networking.eu/occi/sm#maas',
            token, **kwargs)

        if endpoint is not None:
            # deploy logic
            maas = monitoring.ZabbixMonitoring(endpoint)
            if maas.get_location() is None:
                # POST instantiation, GET location
                maas.set_tenant(tenant)
                header = {'Category': 'maas; scheme="http://schemas.mobile-cloud-networking.eu/occi/sm#"; class="kind";',
                          'content-type': 'text/occi',
                          'x-tenant-name': tenant, 'x-auth-token': token}

                response = requests.post(endpoint+'/', headers=header)
                maas.set_location(response.headers.get('location'))
            return maas
        else:
            return None
    else:
        return None


def dispose_maas(token, maas_instance):
    """
    Disposes monitoring helper and deployed monitoring-stack

    :param token: a security token
    :param maas_instance: the to-be-disposed maas-object
    """
    if maas_instance.get_location() is not None:
        header = {'x-tenant-name': maas_instance.get_tenant(),
                  'x-auth-token': token}
        requests.delete(maas_instance.get_location(), headers=header)
        maas_instance.set_location(None)


def get_dnsaas(token, **kwargs):
    """
    Return a instance of the DNSaaS.
    A new instance is deployed if don't exist one
    :param token: The token
    """
    if kwargs['tenant_name'] is not None:
        tenant = kwargs['tenant_name']
    else:
        tenant = 'demo'

    endpoint = services.get_service_endpoint('http://schemas.mobile-cloud-networking.eu/occi/sm#dnsaas', token,
                                             **kwargs)
    if endpoint is None:
        print ("Error: Initiate the SM")
        return None
    else:
        maas_address=None
        maas_endpoint=None 
        dispose_maas=False

        if 'mcn_endpoint_api' in kwargs:
            dns_api = kwargs['mcn_endpoint_api']

            dns_action = dnsaasclient.DNSaaSClientAction(endpoint, tenant, token, dns_api)
        else:
            dns_action = dnsaasclient.DNSaaSClientAction(endpoint, tenant, token)

        if dns_action.init_dns():
            return dns_action
        else:
            return None



def dispose_dnsaas(token, dnsaas_instance):
    """
    Disposes monitoring helper and deployed monitoring-stack of DNSaaS

    :param token: a security token
    :param dnsaas_instance: an instance of DNSaaSClientAction
    """
    if dnsaas_instance.get_location() is not None:

        header = {'x-tenant-name': dnsaas_instance.get_tenant(), 'x-auth-token': token}
        requests.delete(dnsaas_instance.get_location(), headers=header)
        dnsaas_instance.set_location(None)
