from __future__ import annotations
from typing import List, Union
from jsonschema import validate
import cherrypy

from .schemas import *
from .utils import *

import pprint # Dictionaries pretty print (for testing purposes)

################################################################################
class SOA:
    def __init__(
        self, 
        name: str, 
        mname: str, 
        rname: str, 
        serial: str, 
        refresh: str, 
        retry: str, 
        expire: str, 
        ttl: str):

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
        self.serial = str(int(self.serial) + 1)

    @staticmethod
    def from_str(soa_str: str) -> SOA:
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
    def __init__(self, name: str, ip: str):
        self.name = name
        self.class_ = "IN"
        self.type = "A"
        self.ip = ip

    def __str__(self):
        return self.name + '. ' +                                               \
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