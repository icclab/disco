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
Utility functions for dealing with the Design/Service registry.

TODO: M21 replace with OCCI calls!
"""

import os

from keystoneclient.v2_0 import client


def list_services(token, endpoint='http://localhost:35357/v2.0'):
    """
    List services registered within this CC.

    :param token: The token.
    :param endpoint: Optional design module uri.
    """
    # Update from OpS variable.
    if 'DESIGN_URI' in os.environ:
        endpoint = os.environ['DESIGN_URI']

    res = {}
    design = client.Client(token=token, endpoint=endpoint)
    for item in design.services.list():
        res[item.name] = {'description': item.description}
    return res


def _get_url_type(item, **kwargs):
    """
    Get the correct type of endpoint. OpenStack has both a public and internal
    URL for services.

    By default we select internalurl, otherwise if url_type is set to public
    in kwargs then select that URL.

    :param item: the openstack service whose API is requested.
    """

    # default to internal as in original implementation
    url_type = kwargs.get('url_type', 'internal')
    if url_type == 'internal':
        endpoint = item.internalurl
    elif url_type == 'public':
        endpoint = item.publicurl
    else:
        raise AttributeError('Unrecognised URL type: ' + url_type +
                             '. Supported types: public, internal')

    return endpoint


def get_service_endpoints(stype, token,
                          endpoint='http://localhost:35357/v2.0', **kwargs):
    """
    Retrieve all endpoints for a given service type
    :param stype: service type
    :param token: The token.
    :param endpoint: Optional design module uri.
    :param args: Optional arguments.
    :return:
    """
    # Update from OpS variable.
    if 'DESIGN_URI' in os.environ:
        endpoint = os.environ['DESIGN_URI']

    if 'tenant_name' in kwargs:
        tname = kwargs['tenant_name']
    else:
        raise Exception('Tenant Name missing from request')

    design = client.Client(token=token, endpoint=endpoint)
    raw_token = design.get_raw_token_from_identity_service(endpoint, token=token, tenant_name=tname)
    sc = raw_token.service_catalog
    endpoints = sc.get_endpoints(service_type=stype)

    return endpoints


def get_service_endpoint(identifier, token,
                         endpoint='http://localhost:35357/v2.0', **kwargs):
    """
    Retrieve an endpoint for a particular service addressable by this CC.

    Returns None if no endpoint could be found.

    :param identifier: Identifier for the service.
    :param token: The token.
    :param endpoint: Optional design module uri.
    :param args: Optional arguments.
    """
    # Update from OpS variable.
    if 'DESIGN_URI' in os.environ:
        endpoint = os.environ['DESIGN_URI']

    design = client.Client(token=token, endpoint=endpoint)

    if 'tenant_name' in kwargs:
        tname = kwargs['tenant_name']
    else:
        tname = 'demo'

    if 'region' in kwargs:
        region = kwargs['region']
    else:
        region = 'RegionOne'

    # find tenant id
    tenant_id = None
    for item in design.tenants.list():
        if item.name == tname:
            tenant_id = item.id
    if tenant_id is None:
        return None

    # find service description.
    service_ids = []
    for item in design.services.list():
        if item.type == identifier:
            service_ids.append(design.services.get(item.id).id)
    if len(service_ids) == 0:
        return None

    res = None
    if 'allow_multiple' in kwargs and kwargs['allow_multiple']:
            res = []

    for item in design.endpoints.list():
        for service_id in service_ids:
            if service_id == item.service_id and region == item.region:
                if 'allow_multiple' in kwargs and kwargs['allow_multiple']:
                        res.append(_get_url_type(item, **kwargs))
                else:
                    res = _get_url_type(item, **kwargs)
                    if '%(tenant_id)s' in res:
                        res = res.replace('%(tenant_id)s', tenant_id)
                    elif '$(tenant_id)s' in res:
                        res = res.replace('$(tenant_id)s', tenant_id)

    return res
