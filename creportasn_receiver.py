from coap import coap
from coap.coapResource import coapResource
from coap import coapDefines
import datetime

UDP_PORT = 5683
UDP_IP = "bbbb::1"


class exResource(coapResource):
    def __init__(self):
        coapResource.__init__(
            self,
            path='reportasn'
        )

    def GET(self, options=[]):
        print "Get received"

    def PUT(self, options, payload):
        start_asn = 0
        end_asn = 0
        for i in range(0, 5, 1):
            start_asn += pow(256, i) * payload[2 + i]
            end_asn += pow(256, i) * payload[7 + i]
        numDesync = payload[12]
        myrank = payload[13] + payload[14] * 256
        tx = payload[15]
        txACK = payload[16]
        print "received from {0} : {1}".format(options[1][0], str(payload))
        print "Start: {0}; End: {1}; diff: {2}".format(start_asn, end_asn, end_asn - start_asn)
        print "System time: {0}".format(datetime.datetime.now())
        print "numDesync: {0}".format(numDesync)
        print "myrank: {0}".format(myrank)
        print "tx: {0}, txACK: {1}".format(tx, txACK)
        print "ETX: {0}".format(float(tx) / float(txACK))
        print "PDR: {0}".format(float(txACK) / float(tx))
        print "---------------------------------------------------------"

        respCode = coapDefines.COAP_RC_2_01_CREATED
        respOptions = []
        respPayload = []

        return (respCode, respOptions, respPayload)


coap_server = coap.coap(udpPort=UDP_PORT)
coap_server.addResource(exResource())
