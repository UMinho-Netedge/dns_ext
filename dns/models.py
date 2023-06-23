# Copyright 2022 Universidade do Minho
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.


from __future__ import annotations
from typing import List, Union
from jsonschema import validate
import cherrypy

from .schemas import *
from .utils import *

# Dictionaries pretty print (for testing purposes)
import pprint 

###################################
# Classes used by the controllers #
###################################
class SOA:
    """
    This type represents the Start Of Authority (SOA) record which is required
    for each zone. The SOA record contains the following fields:
        - name of the zone
        - e-mail address of the party responsible for administering the domain’s zone file, 
        - the current serial number of the zone, 
        - various timing elements (measured in seconds).
    """
    def __init__(
        self, 
        name: str, 
        mname: str, 
        rname: str, 
        serial: str, 
        refresh: str, 
        retry: str, 
        expire: str, 
        ttl: str
    ):
        """
        :param name: Name of the zone
        :type name: str
        :param mname: The <domain-name> of the name server that was the original or primary source of data for this zone.
        :type mname: str
        :param rname: Address of the party responsible for the zone. A period “.” is used in place of an “@” symbol. For email addresses that contain a period, this will be escaped with a slash “/”.
        :type rname: str
        :param serial: Version number of the zone. As you make changes to your zone file, the serial number will increase.
        :type serial: str
        :param refresh: Time interval, in seconds, before the zone should be refreshed (checking for a Serial Number increase).
        :type refresh: str
        :param retry: Time interval, in seconds, that should elapse before a failed refresh should be retried.
        :type retry: str
        :param expire: Time value, in seconds, that specifies the upper limit on the time interval that can elapse before the zone is no longer authoritative.
        :type expire: str
        :param ttl: Time to live (TTL) value, in seconds, that specifies the time a nameserver or resolver should cache a negative response.
        :type ttl: str
        """

        self.name = name
        self.class_ = "IN"
        self.type = "SOA"
        self.mname = mname
        self.rname = rname
        self.serial = serial
        self.refresh = refresh
        self.retry = retry
        self.expire = expire
        self.ttl = ttl

    def update(self):
        """
        Updates the SOA record serial number incrementing it by one.
        With this update, when the refresh time is reached, the zone will be updated.
        """
        self.serial = str(int(self.serial) + 1)

    @staticmethod
    def from_str(soa_str: str) -> SOA:
        """
        Creates an SOA object from a string.
        :param soa_str: SOA record in string format
        :type soa_str: str
        :return: SOA object
        :rtype: SOA
        """
        soa = soa_str.split()
        return SOA(
            name=soa[0][:-1], 
            mname=soa[3][:-1], 
            rname=soa[4][:-1], 
            serial=soa[5], 
            refresh=soa[6], 
            retry=soa[7],
            expire=soa[8], 
            ttl=soa[9])

    def __str__(self):
        """
        Returns the SOA record in string format.
        :return: SOA record in string format
        :rtype: str
        """
        return self.name + '. ' +                                               \
               self.class_ + ' ' +                                              \
               self.type + ' ' +                                                \
               self.mname + '. ' +                                              \
               self.rname + '. ' +                                              \
               self.serial + ' ' +                                              \
               self.refresh + ' ' +                                             \
               self.retry + ' ' +                                               \
               self.expire + ' ' +                                              \
               self.ttl + '\n'


class A_rec:
    """
    This type represents the A record which is used to map a domain name to an IP address.
    The A record contains the following fields:
        - name of the domain
        - record class (IN): There are three classes of DNS records: IN (Internet), CH (Chaosnet), and HS (Hesiod).
        - record type (A): Where the format of a record is defined. There are several types of DNS records, including A, AAAA, CNAME, MX, NS, PTR, SOA, SRV, and TXT.
        - IP address
        - (Time to live) Amount of time in seconds that a DNS record will be cached by an outside DNS server or resolver.
    """
    def __init__(self, name: str, ip: str, ttl: str):
        """
        :param name: Name of the domain
        :type name: str
        :param ip: IP address
        :type ip: str
        :param ttl: (Time to live) Amount of time in seconds that a DNS record will be cached by an outside DNS server or resolver.
        :type ttl: str
        """
        self.name = name
        self.class_ = "IN"
        self.type = "A"
        self.ip = ip
        self.ttl = ttl

    def __str__(self):
        """
        Returns the A record in string format.
        :return: A record in string format
        :rtype: str
        """
        return self.name + '. ' +                                               \
               self.ttl + ' ' +                                                 \
               self.class_ + ' ' +                                              \
               self.type + ' ' +                                                \
               self.ip + '\n'


#################
# ERROR CLASSES #
#################

class ProblemDetails:
    def __init__(self, type: str, title: str, status: int, detail: str, instance: str):
        """
        :param type: A URI reference according to IETF RFC 3986 that identifies the problem type
        :param title: A short, human-readable summary of the problem type
        :param status: The HTTP status code for this occurrence of the problem
        :param detail: A human-readable explanation specific to this occurrence of the problem
        :param instance: A URI reference that identifies the specific occurrence of the problem
        """
        self.type = type
        self.title = title
        self.status = status
        self.detail = detail
        self.instance = instance

    def to_json(self):
        return dict(
            type=self.type,
            title=self.title,
            status=self.status,
            detail=self.detail,
            instance=self.instance,
        )
        

class Error:
    def __init__(self, type: str, title: str, status: int, detail: str, instance: str):
        self.type = type
        self.title = title
        self.status = status
        self.detail = detail
        self.instance = instance

    def message(self):
        cherrypy.response.status = self.status

        return ProblemDetails(
            type=self.type,
            title=self.title,
            status=self.status,
            detail=self.detail,
            instance=self.instance
        )

class BadRequest(Error):
    def __init__(self, e: Exception):
        Error.__init__(
            self,
            type="xxx",
            title="Bad Request",
            status=400,
            detail=str(e).split('\n')[0],
            instance="xxx"
        )

class NotFound(Error):
    def __init__(self, detail: str = "This resource was not found"):
        Error.__init__(
            self,
            type="xxx",
            title="Not Found",
            status=404,
            detail=detail,
            instance="xxx"
        )

class Forbidden(Error):
    def __init__(self, detail : str = "This operation not allowed"):
        Error.__init__(
            self,
            type="xxx",
            title="Forbidden",
            status=403,
            detail=detail,
            instance="xxx"
        )

class Conflict(Error):
    def __init__(self, detail : str = "This operation cannot be executed "     \
                                      "currently, due to a conflict with the " \
                                      "state of the resource"):
        Error.__init__(
            self,
            type="xxx",
            title="Conflict",
            status=409,
            detail=detail,
            instance="xxx"
        )

class TooManyRequests(Error):
    def __init__(self, detail : str = "This operation cannot be executed due " \
                                      "excess of requests"):
        Error.__init__(
            self,
            type="xxx",
            title="Too Many Requests",
            status=429,
            detail=detail,
            instance="xxx"
        )

class PreconditionFailed(Error):
    def __init__(self, e: Exception):
        Error.__init__(
            self,
            type="xxx",
            title="Precondition Failed",
            status=412,
            detail=str(e).split('\n')[0],
            instance="xxx"
        )

class InternalServerError(Error):
    def __init__(self, e: Exception):
        Error.__init__(
            self,
            type="xxx",
            title="Internal Server Error",
            status=500,
            detail=str(e).split('\n')[0],
            instance="xxx"
        )