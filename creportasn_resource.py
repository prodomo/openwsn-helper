import datetime
import struct

from coapthon.resources.resource import Resource


class CReportASNResource(Resource):
    def __init__(self, name="CReportASNResource", coap_server=None):
        super(CReportASNResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)

    def render_PUT(self, request):
        coap_format = ["<xx",  # padding
                       "BBBBB",  # StartASN
                       "BBBBB",  # EndASN
                       "B",    # numDeSync
                       "H",    # myRank
                       "B",    # parentTX
                       "B",    # parentTXACK
                       "B",    # lastSuccessLeft
                       "B",    # errorCounter
                       "B",    # creportasn_sequence
                       "B",    # lastCallbackSequence
                       "b",    # parentRssi
                       ]
        coap_format_str = ''.join(coap_format)

        raw_payload = request.payload
        data = struct.unpack(coap_format_str, raw_payload)
        start_asn = 0
        end_asn = 0
        for i in range(0, 5, 1):
            start_asn += pow(256, i) * data[i]
            end_asn += pow(256, i) * data[i+5]
        numDesync = data[10]
        myrank = data[11]
        tx = data[12]
        txACK = data[13]
        packet_sequence = data[16]
        last_success_left = data[14]
        error_counter = data[15]
        last_callback_sequence = data[17]
        parent_rssi = data[18]
        print "received from {0}".format(request.source[0])
        print "Start: {0}; End: {1}; diff: {2}".format(start_asn, end_asn, end_asn - start_asn)
        print "Slot offset: {0}".format(end_asn % 101)
        print "System time: {0}".format(datetime.datetime.now())
        print "numDesync: {0}".format(numDesync)
        print "myrank: {0}".format(myrank)
        print "tx: {0}, txACK: {1}".format(tx, txACK)
        print "packet sequence: {0}".format(packet_sequence)
        print "last success left: {0}".format(last_success_left)
        print "errorCounter: {0}".format(error_counter)
        print "ETX: {0}".format(float(tx) / float(txACK))
        print "PDR: {0}".format(float(txACK) / float(tx))
        print "last_callback_sequence: {0}".format(last_callback_sequence)
        print "parent rssi: {0}".format(parent_rssi)
        print "---------------------------------------------------------"
        return self
