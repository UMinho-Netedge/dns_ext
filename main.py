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


import cherrypy
import json
import os
import stat

from dns.api.controllers.zones_controller import (ZonesController)
from dns.models import ProblemDetails

FILES_PATH = "/tmp/coredns/"

# API Controllers
def main():

    ##################################
    # Application support interface  #
    ##################################
    dns_dispatcher = cherrypy.dispatch.RoutesDispatcher()


    ##############################
    # Zones creation and removal #
    ##############################
    dns_dispatcher.connect(
        name="Post Zone",
        action="add_zone",
        controller=ZonesController,
        route="/api/:zoneName",
        conditions=dict(method=["POST"]),
    )

    dns_dispatcher.connect(
        name="Delete Zone",
        action="delete_zone",
        controller=ZonesController,
        route="/api/:zoneName",
        conditions=dict(method=["DELETE"]),
    )

    ################################
    # Records creation and removal #
    ################################
    dns_dispatcher.connect(
        name="Post Record",
        action="add_a_record",
        controller=ZonesController,
        route="/api/:zoneName/record",
        conditions=dict(method=["POST"]),
    )

    dns_dispatcher.connect(
        name="Delete Record",
        action="delete_a_record",
        controller=ZonesController,
        route="/api/:zoneName/record",
        conditions=dict(method=["DELETE"]),
    )


    ################################
    cherrypy.config.update(
        {"server.socket_host": "0.0.0.0", "server.socket_port": 8082}
    )

    dns_conf = {"/": {"request.dispatch": dns_dispatcher}}
    cherrypy.tree.mount(None, "/dns_support/v1", config=dns_conf)


    ######################################
    # Database Connection to all threads #
    ######################################
    cherrypy.engine.start()


def error_page_404(status, message, traceback, version):
    response = cherrypy.response
    response.headers['Content-Type'] = 'application/json'
    errorMessage = ProblemDetails(
        type="xxxx",
        title="Not Found.",
        status=404,
        detail="URI %s cannot be mapped to a valid resource." % cherrypy.request.path_info,
        instance="xxx"
    )
    return json.dumps(errorMessage.to_json())

def error_page_403(status, message, traceback, version):
    response = cherrypy.response
    response.headers['Content-Type'] = 'application/json'
    errorMessage = ProblemDetails(
        type="xxxx",
        title="Forbidden.",
        status=403,
        detail="The operation is not allowed given the current status of the resource.",
        instance="xxx"
    )
    return json.dumps(errorMessage.to_json())

def error_page_400(status, message, traceback, version):
    response = cherrypy.response
    response.headers['Content-Type'] = 'application/json'
    errorMessage = ProblemDetails(
        type="xxxx",
        title="Forbidden.",
        status=400,
        detail="The operation is not allowed given the current status of the resource.",
        instance="xxx"
    )
    return json.dumps(errorMessage.to_json())

def error_page_500(status, message, traceback, version):
    response = cherrypy.response
    response.headers['Content-Type'] = 'application/json'
    errorMessage = ProblemDetails(
        type="xxxx",
        title="Internal Server Error.",
        status=500,
        detail="The server has encountered a situation it does not know how to handle.",
        instance="xxx"
    )
    return json.dumps(errorMessage.to_json())


if __name__ == "__main__":

    #############################################
    # Create Corefile and zone0.db if not exist #
    #############################################

    corefile_path = FILES_PATH + "Corefile"
    zone0_path = FILES_PATH + "zone0.db"

    # Corefile
    if not os.path.exists(corefile_path): 
        #os.system("touch " + corefile_path)
        with open('home/api/temp_files/Corefile','r') as corefile_tmp, open(corefile_path,'w+') as corefile:
            # copy file
            for line in corefile_tmp:
                corefile.write(line)
            # set permissions (rw-rw-rw-)
            os.chmod(corefile_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
        cherrypy.log(f"Corefile created at {corefile_path}")

    # zone0.db
    if not os.path.exists(zone0_path):
        #os.system("touch " + zone0_path)
        with open('home/api/temp_files/zone0.db','r') as zone0_tmp, open(zone0_path,'w+') as zone0:
            # copy file
            for line in zone0_tmp:
                zone0.write(line)
            # set permissions (rw-rw-rw-)
            os.chmod(zone0_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)

        cherrypy.log(f"zone0.db created at {zone0_path}")

    main()
