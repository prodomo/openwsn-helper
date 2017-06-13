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
        counter = payload[21]*256+payload[20]
        int_temp = payload[23]*256+payload[22]
        ext_temp = payload[25]*256+payload[24]
        ext_pyra = payload[27]*256+payload[26]
        int_volt = payload[29]*256+payload[28]
        gpio_pulse = payload[31]*256+payload[30]

        hisAddress = request.source[0]
        hisPort = request.source[1]


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
        print "counter:{0}".format(counter)
        print "int_temp:{0}".format(int_temp)
        print "ext_temp:{0}".format(ext_temp)
        print "ext_pyra:{0}".format(ext_pyra)
        print "int_volt:{0}".format(int_volt)
        print "gpio_pulse:{0}".format(gpio_pulse)
        print "---------------------------------------------------------"
        return self
