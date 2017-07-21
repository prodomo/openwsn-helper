import datetime
from coapthon.resources.resource import Resource
import MySQLdb
import string
import struct

CONST = 0.58134
OFFSET_DATASHEET_25C = 827 #// 1422*CONST, from Datasheet
TEMP_COEFF = CONST * 4.2 #// From Datasheet
OFFSET_0C = OFFSET_DATASHEET_25C - (25 * TEMP_COEFF)

class CReportASNResource(Resource):
    def __init__(self, name="CReportASNResource", coap_server=None):
        super(CReportASNResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)

    def render_PUT(self, request):
        payload = map(ord, request.payload)
        # start_asn = 0
        # end_asn = 0
        # for i in range(0, 5, 1):
        #     start_asn += pow(256, i) * payload[2 + i]
        #     end_asn += pow(256, i) * payload[7 + i]
        # numDesync = payload[12]
        # myrank = payload[13] + payload[14] * 256
        # tx = payload[15]
        # txACK = payload[16]
        # packet_sequence = payload[19]
        # last_success_left = payload[17]
        # error_counter = payload[18]     
        # counter = payload[21]*256+payload[20]
        # int_temp = payload[23]*256+payload[22]
        # ext_temp = payload[25]*256+payload[24]
        # ext_pyra = payload[27]*256+payload[26]
        # int_volt = payload[29]*256+payload[28]
        # gpio_pulse = payload[31]*256+payload[30]

        myrank = payload[2] + payload[3] * 256
        parentAddr = payload[5]+payload[4]*256
        parantRank = payload[6]+payload[7]*256
        tx = payload[8]
        txACK = payload[9]
        parentRssi = 0-payload[10]
        last_success_left = payload[11]
        error_counter = payload[12]
        counter = payload[13]+payload[14]*256
        int_temp = payload[15]+payload[16]*256
        ext_temp = payload[17]+payload[18]*256
        ext_pyra = payload[19]+payload[20]*256
        int_volt = payload[21]+payload[22]*256
        gpio_pulse = payload[23]+payload[24]*256
        PDR=float(txACK) / float(tx)


        systemTime = datetime.datetime.now()
        hisAddress = request.source[0]
        hisPort = request.source[1]

        print "received from {0} : {1}".format(request.source[0], str(payload))
        # print "Start: {0}; End: {1}; diff: {2}".format(start_asn, end_asn, end_asn - start_asn)
        # print "Slot offset: {0}".format(end_asn % 101)
        print "System time: {0}".format(systemTime)
        # print "numDesync: {0}".format(numDesync)
        print "myrank: {0}".format(myrank)
        print "parent addr: {0}".format(hex(parentAddr))
        print "parent rank: {0}".format(parantRank)
        print "parent rssi: {0}".format(parentRssi)
        print "tx: {0}, txACK: {1}, linkPDR:{2}".format(tx, txACK, PDR)
        # print "packet sequence: {0}".format(packet_sequence)
        # print "last success left: {0}".format(last_success_left)
        print "errorCounter: {0}".format(error_counter)
        # print "ETX: {0}".format(float(tx) / float(txACK))
        # print "PDR: {0}".format(float(txACK) / float(tx))
        print "---------------------------------------------------------"
        print "counter:{0}".format(counter)
        print "int_temp:{0}".format(int_temp)
        print "ext_temp:{0}".format(ext_temp)
        print "ext_pyra:{0}".format(ext_pyra)
        print "int_volt:{0}".format(int_volt)
        print "gpio_pulse:{0}".format(gpio_pulse)
        print "---------------------------------------------------------"

        #pure_value = int_temp
        temp_volt = int_temp * CONST
        #i_temp_real = (temp_volt - OFFSET_0C) / TEMP_COEFF
        i_temp_real = int_temp
        print 'internal temp = %2.2f' % i_temp_real

        hisAddress_split = hisAddress.split(':')
        #pure_value = ext_temp
        temp_real = self.convert_adc_to_temp_by_id(hisAddress_split[5], ext_temp)
        #temp_volt = pure_value / 615.80
        #temp_real = pure_value *0.069 - 20.09
        print 'external temp = %2.2f' % temp_real

        #pure_value = ext_pyra
        if (ext_pyra > 2047):
            pyra_real = 0
            print 'detect estimated pyra < 0'
            pyra_raw = ext_pyra
        else:
            #pyra_volt = pure_value * 1200 / 2048
            #pyra_real = pyra_volt * 1000 / 1200
            pyra_raw = ext_pyra
            pyra_real = self.convert_adc_to_batt_by_id(hisAddress_split[5], ext_pyra)
            print 'PA0={0}, estimated pyra = {1}'.format(ext_pyra, pyra_real)
        print 'external batt = %2.2f V' % pyra_real

        #pure_value = int_volt
        #i_volt_real = pure_value / 586.85
        i_volt_real = int_volt
        #print 'raw i_volt = %2.2f' % i_volt_real
        print 'raw i_volt = %d' % i_volt_real

        address = ''
        for i in hisAddress_split[2:]:
            address += '%04x' % int(i, 16)
        
        print 'hisAddress=%s %s %s %s'%(hisAddress_split[2],hisAddress_split[3],hisAddress_split[4],hisAddress_split[5])

        #open db connection 
        db = MySQLdb.connect("localhost","root","sakimaru","ITRI_OpenWSN" )
        cursor = db.cursor()

        #get current time
        #t = datetime.datetime.now()
        currtime = systemTime.strftime("%Y-%m-%d %H:%M:%S")

        #mySql cmd
        sql = "INSERT INTO itri_MOEA_sensor(sn, mac_addr, \
            ext_temperature, pyranometer, datetime, int_temperature, battery_volt) \
            VALUES ('%d', '%s', '%.2f', '%d', '%s', '%.2f', '%.2f')" %\
            (counter, address, temp_real, pyra_raw, currtime, i_temp_real, pyra_real)
        rps_sql = "REPLACE INTO itri_MOEA_current_sensor(sn, mac_addr, \
            ext_temperature, pyranometer, datetime, int_temperature, battery_volt) \
            VALUES ('%d', '%s', '%.2f', '%d', '%s', '%.2f', '%.2f')" %\
            (counter, address, temp_real, pyra_raw, currtime, i_temp_real, pyra_real)
        
        topology_sql = "INSERT INTO itri_topology_mote(mac_addr, my_rank, p_mac_addr, p_rank, p_rssi, PDR, tx, txack, error_counter, sn, datetime) \
        VALUES('%s','%d', '%s', '%d', '%d', '%.2f','%d', '%d', '%d', '%d','%s')" \
        %(address, myrank, hex(parentAddr), parantRank, parentRssi, PDR, tx, txACK, error_counter, counter, currtime)

        try:
            # Execute the SQL command
            cursor.execute(sql)
            cursor.execute(rps_sql)
            cursor.execute(topology_sql)
            # Commit your changes in the database
            db.commit()
        except:
            # Rollback in case there is any error
            db.rollback()
        
        # disconnect from server
        db.close()

        print 'insert DB ok !!'

        return self

    def convert_adc_to_batt_by_id(self, in_ID, in_value):
        matrix2 = {'a732':42, 'a720':-24, 'a6f4':0, 'a714':8, 'a636':6, 'a739':26, 'a6ab':10, 'a668':13, 'a6b2':0, 'a6fa':28, 'a6e4':-12}

        parm_global_carib_batt = 0.9925
        parm_digi2volt=3.3/2047.0
        parm_digi2volt *= parm_global_carib_batt
        #parm_ADCvolt2BATTvolt = 1/0.4498
        parm_ADCvolt2BATTvolt = 1/0.5035

        value = matrix2.get(in_ID)

        print 'offset={0} for {1}'.format(value, in_ID)

        if (value == None ):
            offset = 0
        else:
            offset = value

        temp_volt = (in_value + offset)
        tmp_real = temp_volt * parm_digi2volt
        tmp_real2 = tmp_real * parm_ADCvolt2BATTvolt

        print 'external pure Battery ADC value = {0}, estimated Volt={1}V, estimated BattV={2}'.format(in_value, tmp_real, tmp_real2)

        return tmp_real2

    def convert_adc_to_temp_by_id(self, in_ID, in_value):
        matrix = {'a732':42, 'a720':-24, 'a6f4':0, 'a714':8, 'a636':6, 'a739':26, 'a6ab':10, 'a668':13, 'a692':2, 'a6fa':28}

        value = matrix.get(in_ID)

        print 'offset={0} for {1}'.format(value, in_ID)

        if (value == None ):
            offset = 0
        else:
            offset = value

        temp_volt = (in_value + offset) / 615.80
        tmp_real = (in_value + offset) *0.069 - 20.09

        print 'external pure temp ADC value = {0}, estimated Volt={1}V, estimated temp={2}'.format(in_value, temp_volt, tmp_real)

        return tmp_real