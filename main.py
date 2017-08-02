import time
import datetime
import sys
from coap import coapDefines
from coap import coap
import mysql.connector
from coap.coapResource import coapResource

UDP_PORT = 5683
UDP_IP = "bbbb::1"

cnx = mysql.connector.connect(user='cps', database='cps', password='cps')
cursor = cnx.cursor()

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
            start_asn += pow(256, i) * payload[2+i]
            end_asn += pow(256, i) * payload[7 + i]
        numDesync = payload[12]
        myrank = payload[13] + payload[14]*256
        tx = payload[15]
        txACK = payload[16]
        packet_sequence = payload[19]
        last_success_left = payload[17]
        error_counter = payload[18]
        print "received from {0} : {1}".format(options[1][0], str(payload))
        print "Start: {0}; End: {1}; diff: {2}".format(start_asn, end_asn, end_asn-start_asn)
        print "Slot offset: {0}".format(end_asn%101)
        print "System time: {0}".format(datetime.datetime.now())
        print "numDesync: {0}".format(numDesync)
        print "myrank: {0}".format(myrank)
        print "tx: {0}, txACK: {1}".format(tx, txACK)
        print "packet sequence: {0}".format(packet_sequence)
        print "last success left: {0}".format(last_success_left)
        print "errorCounter: {0}".format(error_counter)
        print "ETX: {0}".format(float(tx) / float(txACK))
        print "PDR: {0}".format(float(txACK) / float(tx))
        try:

            command = "INSERT INTO `delay` (`id`, `mote`, `start_asn`, `end_asn`, `diff`, `numDesync`, `myRank`, `tx`, `txACK`, `packet_sequence`, `last_success_left`, `error_counter`, `created_at`) VALUE (NULL, '{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', NULL)".format(options[1][0], start_asn, end_asn, end_asn-start_asn, numDesync, myrank, tx, txACK, packet_sequence, last_success_left, error_counter)

            cursor.execute(command)
            cnx.commit()
            import requests

            data = {
                "mote": options[1][0],
                "timeStamp": time.time(),
                "startASN": start_asn,
                "endASN": end_asn,
                "diff": end_asn-start_asn,
                "numDesync": numDesync,
                "myRank": myrank,
                "tx": tx,
                "txACK": txACK,
                "packetSequence": packet_sequence,
                "lastSuccessLeft": last_success_left,
                "errorCounter": error_counter
            }

            import json
            # r = requests.post('http://140.124.184.204:8080/Cloud/WSN/Insert', data=json.dumps(data), )
            # # cursor.close()
            # cnx.close()
        except:
            print "oops"
            print "Unexpected error:", sys.exc_info()[0]
        print "---------------------------------------------------------"
        respCode = coapDefines.COAP_RC_2_01_CREATED
        respOptions = []
        respPayload = []

        return (respCode, respOptions, respPayload)
#
coap_server =coap.coap(udpPort=UDP_PORT)
#
coap_server.addResource(exResource())
