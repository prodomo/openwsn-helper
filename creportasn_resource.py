import datetime
import sys
import struct
# import mysql.connector
import ConfigParser
import MySQLdb

from coapthon.resources.resource import Resource

# config = ConfigParser.RawConfigParser()
# config.read('config.cfg')


# db = MySQLdb.connect("localhost","root","sakimaru","ITRI_OpenWSN" )
# cursor = db.cursor()

# cnx = mysql.connector.connect(user=config.get('database', 'username'),
#                               database=config.get('database', 'database'),
#                               password=config.get('database', 'password'))
# cursor = cnx.cursor()


class CReportASNResource(Resource):
    def __init__(self, name="CReportASNResource", coap_server=None):
        super(CReportASNResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        print "G"

    def render_PUT(self, request):
        try:
            coap_format = ["<xx",  # padding
                           "BBBBB",  # StartASN
                           "BBBBB",  # EndASN
                           "B",  # numDeSync
                           "H",  # myRank
                           "B",  # parentTX
                           "B",  # parentTXACK
                           "B",  # lastSuccessLeft
                           "B",  # errorCounter
                           "B",  # creportasn_sequence
                           "B",  # lastCallbackSequence
                           "b",  # parentRssi
                           ]
            coap_format_str = ''.join(coap_format)

            raw_payload = request.payload
            data = struct.unpack(coap_format_str, raw_payload)
            mote = request.source[0]
            start_asn = 0
            end_asn = 0
            for i in range(0, 5, 1):
                start_asn += pow(256, i) * data[i]
                end_asn += pow(256, i) * data[i + 5]
            numDesync = data[10]
            myrank = data[11]
            tx = data[12]
            txACK = data[13]
            packet_sequence = data[16]
            last_success_left = data[14]
            error_counter = data[15]
            last_callback_sequence = data[17]
            parent_rssi = data[18]

            print "received from {0}".format(mote)
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


            if txACK == 0:
                PDR=0
            else:
                PDR=float(txACK) / float(tx)

            systemTime = datetime.datetime.now()
            currtime = systemTime.strftime("%Y-%m-%d %H:%M:%S")
            hisAddress = request.source[0]
            hisPort = request.source[1]
            hisAddress_split = hisAddress.split(':')
            address = ''
            for i in hisAddress_split[2:]:
                address += '%04x' % int(i, 16)

            parentRssi=parent_rssi
            parantRank=0
            parentAddr=0
            counter = packet_sequence

            db = MySQLdb.connect("localhost","root","sakimaru","ITRI_OpenWSN" )
            cursor = db.cursor()

            command = "INSERT INTO `delay` (`id`, `mote`, `start_asn`, `end_asn`, `diff`, `numDesync`, `myRank`, `tx`, `txACK`, `packet_sequence`, `last_success_left`, `error_counter`, `last_callback_sequence`, `parent_rssi`, `created_at`) VALUE (NULL, '{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}')".format(
                mote, start_asn, end_asn, end_asn - start_asn, numDesync, myrank, tx, txACK, packet_sequence,
                last_success_left, error_counter, last_callback_sequence, parent_rssi, currtime)

            topology_sql = "INSERT INTO itri_topology_mote(mac_addr, my_rank, p_mac_addr, p_rank, p_rssi, PDR, tx, txack, error_counter, sn, datetime) VALUES ('%s','%d', '%s', '%d', '%d', '%.2f','%d', '%d', '%d', '%d','%s') "%(address, myrank, hex(parentAddr), parantRank, parentRssi, PDR, tx, txACK, error_counter, counter, currtime)



            try:
                cursor.execute(command)
                cursor.execute(topology_sql)
                db.commit()
                print "insert DB ok"
            except:
                db.rollback()
        
            db.close()
        except:
            print "oops"
            print "Unexpected error:", sys.exc_info()
        print "---------------------------------------------------------"

        return self
