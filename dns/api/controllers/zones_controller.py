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
    """
    This function returns a string pattern that configures a zone block in the Corefile.

    :param zoneName: name of the zone to be created
    :type zoneName: str
    :param port: port of the dns server
    :type port: str
    :return: pattern of the zone block
    :rtype: str

    """
    return "\n%s:%s {\n    import snip_base\n    file /etc/coredns/%s.db {\n        reload 5s\n    }\n}" %(zoneName, port, zoneName)


class ZonesController:
    @json_out(cls=NestedEncoder)
    def add_zone(self, zoneName: str, mname: str, rname: str, refresh: str, retry: str, expire: str, ttl: str, **kwargs):
        """
        This function creates a zone in the Corefile and a zone file.

        :param zoneName: Name of the zone to be created.
        :type zoneName: str
        :param mname: Name of the master server.
        :type mname: str
        :param rname: Address of the party responsible for the zone.
        :type rname: str
        :param refresh: Time interval, in seconds, before the zone should be refreshed.
        :type refresh: str
        :param retry: Time interval, in seconds, that should elapse before a failed refresh should be retried.
        :type retry: str
        :param expire: Time value, in seconds, that specifies the upper limit on the time interval that can elapse before the zone is no longer authoritative.
        :type expire: str
        :param ttl: Time to live, in seconds. Specifies the time a nameserver or resolver should cache a negative response.
        :type ttl: str

        """

        # Make sure that there is no extra parameter
        if kwargs != {}:
            error_msg = "Invalid attribute(s): %s" % (str(kwargs))
            error = BadRequest(error_msg)
            return error.message()

        # Check if the zone file already exists raising an error if it does
        if exists(FILES_PATH + zoneName + ".db"):
            error_msg = "Zone %s already exists." % (zoneName)
            error = Forbidden(error_msg)
            return error.message()

        # Create the SOA object
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
            # Creates the zone file and writes the SOA record
            with open(FILES_PATH + "%s.db" %(zoneName), mode='w') as f:
                f.write(str(soa))
        except EnvironmentError as e:
            error_msg = "Error creating zone file:\n" + e
            error = InternalServerError(error_msg)
            return error.message()

        try:
            # Appends the configuration block of the new zone into Corefile
            core_file_zone = zone_block_pattern(zoneName, PORT)
            with open(FILES_PATH + "Corefile", mode='a') as f:
                f.write(core_file_zone)
        except EnvironmentError as e:
            error_msg = "Error raised while opening/handling Corefile:\n" + e
            error = InternalServerError(error_msg)
            return error.message()

        cherrypy.log("Created new zone named %s with SOA %s" %(zoneName, str(soa)))
        cherrypy.response.status = 200
        

    @json_out(cls=NestedEncoder)
    def delete_zone(self, zoneName: str, **kwargs):
        """
        This function deletes a zone from the Corefile and a zone file from the /etc/coredns folder.

        :param zoneName: Name of the zone to be deleted.
        :type zoneName: str

        """

        # Make sure that there is no extra parameter
        if kwargs != {}:
            error_msg = "Invalid attribute(s): %s" % (str(kwargs))
            error = BadRequest(error_msg)
            return error.message()
        
        # Rewrite the Corefile without the zone block
        try:
            with open(FILES_PATH + "Corefile", mode='r') as f:
                content = f.read()

            with open(FILES_PATH + "Corefile", mode='w') as f:
                new_content = re.sub(zone_block_pattern(zoneName, PORT), '', content, re.MULTILINE)
                f.write(new_content)
        except EnvironmentError as e:
            error_msg = "Error handling Corefile:\n" + e
            error = InternalServerError(error_msg)
            return error.message()

        # Delete the zone file
        try:
            os.remove(FILES_PATH + "%s.db" %(zoneName))
        except OSError:
            error_msg = "Inexistent zone name."
            error = NotFound(error_msg)
            return error.message()

        cherrypy.log("Deleted Zone %s!" %(zoneName))
        cherrypy.response.status = 200


    @json_out(cls=NestedEncoder)
    def add_a_record(self, zoneName: str, name: str, ip: str, ttl: str, **kwargs):
        """
        This function adds an A record to a zone file.

        :param zoneName: Name of the zone to which the record will be added.
        :type zoneName: str
        :param name: Name of the host.
        :type name: str
        :param ip: IP address of the host.
        :type ip: str
        :param ttl: Time to live, in seconds. Specifies the time a nameserver or resolver should cache a negative response.
        :type ttl: str

        """

        # Make sure that there is no extra parameter
        if kwargs != {}:
            error_msg = "Invalid attribute(s): %s" % (str(kwargs))
            error = BadRequest(error_msg)
            return error.message()

        # Create the A record object
        a_record = A_rec(name, ip, ttl)

        # Append the A record to the zone file and increment the serial number in the SOA record
        try:
            with open(FILES_PATH + "%s.db" %(zoneName), mode='a') as f:
                f.write(str(a_record))

            with open(FILES_PATH + "%s.db" %(zoneName), mode='r') as f:
                # SOA serial increment so zone update is granted
                content = f.readlines()
        except EnvironmentError as e:
            error_msg = "Error handling zone file:\n" + e
            error = InternalServerError(error_msg)
            return error.message()

        # Construction of the new SOA record, with the incremented serial number
        # grating the zone update, into a string, which will be the first line 
        # of the rewritten zone file.
        soa = SOA.from_str(content[0])
        soa.update()
        content[0] = str(soa)

        try:
            with open(FILES_PATH + "%s.db" %(zoneName), mode='w') as f:
                f.write(''.join(content))
        except EnvironmentError as e:
            error_msg = "Error handling zone file:\n" + e
            error = InternalServerError(error_msg)
            return error.message()

        cherrypy.log("Add A record line in zone %s: %s" %(zoneName, str(a_record)))


    @json_out(cls=NestedEncoder)
    def delete_a_record(self, zoneName: str, name: str, **kwargs):
        """
        This function deletes an A record from a zone file.

        :param zoneName: Name of the zone from which the record will be deleted.
        :type zoneName: str
        :param name: Name of the host.
        :type name: str

        """
        # Make sure that there is no extra parameter
        if kwargs != {}:
            error_msg = "Invalid attribute(s): %s" % (str(kwargs))
            error = BadRequest(error_msg)
            return error.message()


        try:
            with open(FILES_PATH + zoneName + ".db", mode='r') as f:
                content = f.readlines()
        except EnvironmentError as e:
            error_msg = "Error reading zone file:\n" + e
            error = InternalServerError(error_msg)
            return error.message()


        # Update the SOA record serial number
        soa = SOA.from_str(content[0])
        soa.update()
        content[0] = str(soa)
        content = ''.join(content)

        # Search for the A record to be deleted and delete it.
        try:
            with open(FILES_PATH + zoneName + ".db", mode='w') as f:
                new_content = re.sub(r'%s.*\n' %(name), '', content, re.DOTALL)
                f.write(new_content)
        except EnvironmentError as e:
            error_msg = "Error handling zone file:\n" + e
            error = InternalServerError(error_msg)
            return error.message()
