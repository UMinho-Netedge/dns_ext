import json
import sys
import jsonschema
import cherrypy
import time

sys.path.append("../../")
from dns.models import *
from json.decoder import JSONDecodeError


class ZonesController:

    @cherrypy.tools.json_in()
    def add_zone(self, zoneName: str):
        cherrypy.log("Add Zone %s!" %(zoneName))

        soa = SOA(
                    name=zoneName,
                    mname="ns1.primaryserver.com",
                    rname="admin.netedge.com",
                    serial=time.strftime("%Y%m%d%H", time.localtime()),
                    refresh="7200",
                    retry="3600",
                    expire="1209600",
                    ttl="3600"
                    )

        with open("/home/api/coredns/%s.db" %(zoneName), mode='w+') as f:
            f.write(str(soa))
            #f.write("example.com.        IN  SOA dns.example.com. robbmanes.example.com. 2015082544 7200 3600 1209600 3600")

        core_file_zone = "\n%s:1053 {\n\timport snip_base\n\tfile /etc/coredns/%s.db {\n\t\treload 5s\n\t}\n}\n" %(zoneName, zoneName)
        with open("/home/api/coredns/Corefile", mode='a') as f:
            f.write(core_file_zone)

        with open("/home/api/coredns/Corefile", mode='r') as f:
            content = f.read()
        cherrypy.log(content)
        

    @cherrypy.tools.json_in()
    def delete_zone(self, zoneName: str):
        cherrypy.log("Delete Zone %s!" %(zoneName))