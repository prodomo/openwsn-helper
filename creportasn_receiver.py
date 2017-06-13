from coapthon.server.coap import CoAP
from creportasn_resource import CReportASNResource
from uinject_coap_resource import UinjectCoapResource
import datetime

UINJECT_COAP_PORT = 2000
UDP_PORT = 5683
UDP_IP = "bbbb::1"

class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port))
        self.add_resource('reportasn', CReportASNResource())
        #self.add_resource('uinject_coap', UinjectCoapResource())

server = CoAPServer(UDP_IP, UDP_PORT)
try:
    server.listen(10)
except KeyboardInterrupt:
    print "Server Shutdown"
    server.close()
    print "Exiting..."
