import json
import sys
import jsonschema
import cherrypy
import time
import re
import os

sys.path.append("../../")
from dns.models import *
from json.decoder import JSONDecodeError
from os.path import exists

PORT = '1053'
FILES_PATH = "/tmp/coredns/"

def zone_block_pattern(zoneName: str, port: str):
    return "\n%s:%s {\n    import snip_base\n    file /etc/coredns/%s.db {\n        reload 5s\n    }\n}" %(zoneName, port, zoneName)


class ZonesController:
    @json_out(cls=NestedEncoder)
    def add_zone(self, zoneName: str, mname: str, rname: str, refresh: str, retry: str, expire: str, ttl: str):
        if exists(FILES_PATH + zoneName + ".db"):
            error_msg = "Zone %s already exists." % (zoneName)
            error = Forbidden(error_msg)
            return error.message()

        soa = SOA(
                    name=zoneName,
                    mname=mname,
                    rname=rname,
                    serial=time.strftime("%Y%m%d%H", time.localtime()),
                    refresh=refresh,
                    retry=retry,
                    expire=expire,
                    ttl=ttl
                    )

        try:
            # Create zonefile
            with open(FILES_PATH + "%s.db" %(zoneName), mode='w') as f:
                f.write(str(soa))
        except EnvironmentError as e:
            error_msg = "Error creating zone file:\n" + e
            error = InternalServerError(error_msg)
            return error.message()

        try:
            # Append the new zone configuration to Corefile
            core_file_zone = zone_block_pattern(zoneName, PORT)
            with open(FILES_PATH + "Corefile", mode='a') as f:
                f.write(core_file_zone)
        except EnvironmentError as e:
            error_msg = "Error creating opening Corefile:\n" + e
            error = InternalServerError(error_msg)
            return error.message()

        cherrypy.log("Created new zone named %s with SOA %s" %(zoneName, str(soa)))
        cherrypy.response.status = 200
        

    @json_out(cls=NestedEncoder)
    def delete_zone(self, zoneName: str):
            
        try:
            with open(FILES_PATH + "Corefile", mode='r') as f:
                content = f.read()

            with open(FILES_PATH + "Corefile", mode='w') as f:
                new_content = re.sub(zone_block_pattern(zoneName, PORT), '', content, re.MULTILINE)
                f.write(new_content)
        except EnvironmentError as e:
            error_msg = "Error opening Corefile:\n" + e
            error = InternalServerError(error_msg)
            return error.message()

        try:
            os.remove(FILES_PATH + "%s.db" %(zoneName))
        except OSError:
            error_msg = "Inexistent zone name."
            error = NotFound(error_msg)
            return error.message()

        cherrypy.log("Deleted Zone %s!" %(zoneName))
        cherrypy.response.status = 200


    @json_out(cls=NestedEncoder)
    def add_a_record(self, zoneName: str, name: str, ip: str, ttl: str):
        a_record = A_rec(name, ip, ttl)
        with open(FILES_PATH + "%s.db" %(zoneName), mode='a') as f:
            f.write(str(a_record))

        with open(FILES_PATH + "%s.db" %(zoneName), mode='r') as f:
            # SOA serial increment so zone update is granted
            content = f.readlines()
            
        soa = SOA.from_str(content[0])
        soa.update()
        content[0] = str(soa)

        with open(FILES_PATH + "%s.db" %(zoneName), mode='w') as f:
            f.write(''.join(content))

        cherrypy.log("Add A record line in zone %s: %s" %(zoneName, str(a_record)))


    @json_out(cls=NestedEncoder)
    def delete_a_record(self, zoneName: str, name: str):
        with open(FILES_PATH + zoneName + ".db", mode='r') as f:
            content = f.readlines()

        soa = SOA.from_str(content[0])
        soa.update()
        content[0] = str(soa)
        content = ''.join(content)

        with open(FILES_PATH + zoneName + ".db", mode='w') as f:
            new_content = re.sub(r'%s.*\n' %(name), '', content, re.DOTALL)
            f.write(new_content)
