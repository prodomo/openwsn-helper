import datetime
from coapthon.resources.resource import Resource


class CReportASNResource(Resource):
    def __init__(self, name="CReportASNResource", coap_server=None):
        super(CReportASNResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)

    def render_PUT(self, request):
        payload = map(ord, request.payload)
        start_asn = 0
        end_asn = 0
        for i in range(0, 5, 1):
            start_asn += pow(256, i) * payload[2 + i]
            end_asn += pow(256, i) * payload[7 + i]
        numDesync = payload[12]
        myrank = payload[13] + payload[14] * 256
        tx = payload[15]
        txACK = payload[16]
        packet_sequence = payload[19]
        last_success_left = payload[17]
        error_counter = payload[18]


        print "received from {0} : {1}".format(request.source[0], str(payload))
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
        print "---------------------------------------------------------"
        print "counter:{0},{1}".format(payload[20], payload[21])
        print "int_temp:{0},{1}".format(payload[22], payload[23])
        print "ext_temp:{0},{1}".format(payload[24], payload[25])
        print "ext_pyra:{0},{1}".format(payload[26], payload[27])
        print "int_volt:{0},{1}".format(payload[28], payload[29])
        print "gpio_pulse:{0},{1}".format(payload[30], payload[31])
        print "---------------------------------------------------------"
        return self
