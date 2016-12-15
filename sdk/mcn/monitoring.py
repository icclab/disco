#   Copyright (c) 2014, Technische Universitaet Berlin
#   All Rights Reserved.
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
Module dealing with monitoring relate calls.
"""

import time

import requests

from zabbix_api import ZabbixAPI


class Monitoring(object):
    """
    Wraps around the MaaS.
    """

    def get_address(self, token):
        """
        Returns MaaS_IP

        :param token: a security token
        """
        raise NotImplementedError()

    def get_metric(self, host, item, **kwargs):
        """
        Returns the last value of "item" from "host"

        :param host: hostname of itemholder
        :param item: itemname of wanted item
        :param kwargs: optional arguments
        :return:
        """
        raise NotImplementedError()


class ZabbixMonitoring(Monitoring):
    """
    Wraps around the MaaS.
    """

    # class variables to implement those as a singleton
    __location = None
    __address = None
    __tenant = None

    @classmethod
    def set_location(cls, arg):
        """
        Sets classvariable __location

        :param arg: new location
        """
        if arg != cls.__location:
            cls.__location = arg

    @classmethod
    def get_location(cls):
        """
        Returns classvariable __location
        """
        return cls.__location

    @classmethod
    def set_address(cls, arg):
        """
        Sets classvariable __address

        :param arg: new address
        """
        if arg != cls.__address:
            cls.__address = arg

    @classmethod
    def get_tenant(cls):
        """
        Returns classvariable __tenant
        """
        return cls.__tenant

    @classmethod
    def set_tenant(cls, arg):
        """
        Sets classvariable __tenant

        :param arg: new tenant
        """
        if arg != cls.__tenant:
            cls.__tenant = arg

    def __init__(self, endpoint='http://localhost:8888/maas/'):
        """
        Initializes helper for monitoring.

        :param endpoint: Optional maassm uri
        """
        self.__endpoint = endpoint
        self.__tenant = None

    def get_address(self, token):
        """
        Returns MaaS_IP

        :param token: a security token
        """
        if self.get_location() is not None:
            # get address and return
            hdr = {'x-tenant-name': self.get_tenant(), 'x-auth-token': token}
            response = requests.get(self.__location, headers=hdr)
            # check if the stack is deployed yet, selfcall otherwise
            if 'CREATE_COMPLETE' in response.content:
                # TODO: clean the messy parsing
                self.set_address(
                    [x for x in response.content.splitlines()
                     if 'mcn.endpoint.maas=' in x]
                    [-1].split('=')[-1].strip('"'))
                return self.__address
            else:
                time.sleep(30)
                return self.get_address(token)
        else:
            return None

    def get_metric(self, host, item, **kwargs):
        """
        Returns the last value of "item" from "host"

        :param host: hostname of itemholder
        :param item: itemname of wanted item
        :param kwargs: Optional parameter
        :return:
        """
        if self.__address is not None:
            if 'password' in kwargs:
                password = kwargs['password']
            else:
                password = 'zabbix'
            if 'username' in kwargs:
                username = kwargs['username']
            else:
                username = 'admin'

            zapi = ZabbixAPI(server='http://'+self.__address+'/zabbix',
                             path="", log_level=0)
            zapi.login(username, password)
            hostid = zapi.host.get({"filter": {"host": host}})[0]["hostid"]

            item_values = zapi.item.get({"params": {"hostids": hostid},
                                         "filter": {"name": item,
                                                    "hostid": hostid}})

            return item_values[0]["lastvalue"]
        else:
            return None
