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

# API Controllers
import cherrypy
from dns.api.controllers.zones_controller import (ZonesController)

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


    cherrypy.config.update(
        {"server.socket_host": "0.0.0.0", "server.socket_port": 8080}
    )

    dns_conf = {"/": {"request.dispatch": dns_dispatcher}}
    cherrypy.tree.mount(None, "/dns_support/v1", config=dns_conf)


    ######################################
    # Database Connection to all threads #
    ######################################
    cherrypy.engine.start()


if __name__ == "__main__":
    main()
