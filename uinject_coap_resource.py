from coapthon.resources.resource import Resource
import socket
import struct
from datetime import datetime
import MySQLdb
import thread
import time
import os

enableAck = 1
secPerPkt = 45
neigRankDic = {}
serialSnDic = {}
calRcvRate = {}
progStartTime = datetime.now()

class UinjectCoapResource(Resource):
    def __init__(self, name="UinjectCoapResource", coap_server=None):
        super(UinjectCoapResource, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        neigRankDic = {}
        serialSnDic = {}
        calRcvRate = {}
        progStartTime = datetime.now()

    def render_PUT(self, request):
        payload = map(ord, request.payload)

        neigList = []
        rssiList = []
        Saddr = 0xffff
        Rssi = -99
        counter = payload[3]*256+payload[2]
        tplg_Code = payload[4]
        needAck = (tplg_Code & 0x20)
        tplg_mode = tplg_Code
        PDR = 0.0
        PDR += payload[5]
        PDR /= 255.0
        tplg_parent = payload[6]*256 + payload[7]
        tplg_rank = payload[8]*256 + payload[9]
        tplg_numNeig = payload[10]

        hisAddress = request.source[0]
        hisPort = request.source[1]

        for c in range(0,10):
            if c < tplg_numNeig:
                Saddr= payload[c*3+11]
                Saddr *=256
                Saddr += payload[c*3+12]
                Rssi = payload[c*3+13]
                Rssi -= 255
                neigList.append(Saddr)
                rssiList.append(Rssi)
                print 'RSSI = {0}'.format(Rssi)
            else:
                Saddr= 0
                Rssi= 0
                neigList.append(Saddr)
                rssiList.append(Rssi)

        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "received from {0} and port={1} ".format(request.source[0], request.source[1])
        print "received from {0} : {1}".format(request.source[0], str(payload))
        print "length of payload {0}.".format(len(payload))
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print 'counter = {4}, d1={0},d2={1:.2f},d3={2}, parent={3}, neigs='.format(tplg_mode,PDR,tplg_numNeig, hex(tplg_parent), counter) + ' '.join( hex(c) for c in neigList[0:tplg_numNeig])
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"


        db = MySQLdb.connect("localhost","root","sakimaru","ITRI_OpenWSN" )
        cursor = db.cursor()
        sql= "CREATE TABLE IF NOT EXISTS itri_topology_current_neighbors ( `devAddr` VARCHAR(45), `SN` INT(11), `mode` VARCHAR(45), `PDR` FLOAT, `rank` INT(11) , `parentAddr` VARCHAR(45), `neighborNum` INT(11), datetime DATETIME, `n1` VARCHAR(45), `n2` VARCHAR(45), `n3` VARCHAR(45),`n4` VARCHAR(45),`n5` VARCHAR(45),`n6` VARCHAR(45),`n7` VARCHAR(45),`n8` VARCHAR(45),`n9` VARCHAR(45),`n10` VARCHAR(45), `rssi1` INT(11),`rssi2` INT(11),`rssi3` INT(11),`rssi4` INT(11),`rssi5` INT(11),`rssi6` INT(11),`rssi7` INT(11),`rssi8` INT(11),`rssi9` INT(11),`rssi10` INT(11), PRIMARY KEY(`devAddr`))"

        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

        db.close()

        print 'normal process here below !!'

        if len(payload) > 51:
            print 'illegal data length (%d Bytes), but we continue' % len(payload)
            return self
        else:
            print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

            if self.pktSn_check(hisAddress, counter):
               print 'we receive duplicate udp data sn={0}'.format(counter)
               return self
            else:
               self.pktSn_update(hisAddress, counter)
            #print 'd1={0},d2={1},d3={2}, n1={3:4x}, n2={4:4x}'.format(d1,d2,d3,neigList[0],neigList[1])

            self.neigRank_update(hisAddress, tplg_rank)
            #print neigRankDic

            hisAddr_split = hisAddress.split(':')
            tplg_src_addr = ''
            for i in hisAddr_split[2:]:
               tplg_src_addr += '%04x' % int(i,16)
            print 'addr=%s' % tplg_src_addr
            t = datetime.now()
            currtime = t.strftime("%Y-%m-%d %H:%M:%S")

            db = MySQLdb.connect("localhost","root","sakimaru","ITRI_OpenWSN" )
            cursor = db.cursor()

        #mySql cmd
            sql = "INSERT INTO itri_topology_neighbors(mode, neighborNum, devAddr,PDR,\
            parentAddr, datetime, SN, rank,\
            n1,n2,n3,n4,n5,\
            n6,n7,n8,n9,n10,\
            rssi1,rssi2,rssi3,rssi4,rssi5,\
            rssi6,rssi7,rssi8,rssi9,rssi10) \
            VALUES ('%s', '%d', '%s', '%.2f',\
                '%04x', '%s', '%d', '%d',\
                '%04x','%04x','%04x','%04x','%04x',\
                '%04x','%04x','%04x','%04x','%04x',\
                '%d','%d','%d','%d','%d',\
                '%d','%d','%d','%d','%d')" \
                %(hex(tplg_mode), tplg_numNeig, tplg_src_addr, PDR,\
                tplg_parent, currtime, counter, tplg_rank,\
                neigList[0],neigList[1],neigList[2],neigList[3],neigList[4],\
                neigList[5],neigList[6],neigList[7],neigList[8],neigList[9],\
                rssiList[0],rssiList[1],rssiList[2],rssiList[3],rssiList[4],\
                rssiList[5],rssiList[6],rssiList[7],rssiList[8],rssiList[9])

            sql_rp = "REPLACE INTO itri_topology_current_neighbors(mode, neighborNum, devAddr,PDR,\
            parentAddr, datetime, SN, rank,\
            n1,n2,n3,n4,n5,\
            n6,n7,n8,n9,n10,\
            rssi1,rssi2,rssi3,rssi4,rssi5,\
            rssi6,rssi7,rssi8,rssi9,rssi10) \
            VALUES ('%s', '%d', '%s', '%.2f',\
                '%04x', '%s', '%d', '%d',\
                '%04x','%04x','%04x','%04x','%04x',\
                '%04x','%04x','%04x','%04x','%04x',\
                '%d','%d','%d','%d','%d',\
                '%d','%d','%d','%d','%d')" \
                %(hex(tplg_mode), tplg_numNeig, tplg_src_addr, PDR,\
                tplg_parent, currtime, counter, tplg_rank,\
                neigList[0],neigList[1],neigList[2],neigList[3],neigList[4],\
                neigList[5],neigList[6],neigList[7],neigList[8],neigList[9],\
                rssiList[0],rssiList[1],rssiList[2],rssiList[3],rssiList[4],\
                rssiList[5],rssiList[6],rssiList[7],rssiList[8],rssiList[9])
            try:
                # Execute the SQL command
                cursor.execute(sql)
                cursor.execute(sql_rp)
                # Commit your changes in the database
                db.commit()

                #lock.acquire()
                # Execute the SQL command
                #cursor.execute(sql_to_tmp)
                # Commit your changes in the database
                #db.commit()
                #lock.release()
            except:
                # Rollback in case there is any error
                db.rollback()

            # disconnect from server
            db.close()

            print 'done insert data into table itri_topology_neighbors'

            self.moteRecv_update(tplg_src_addr)
            self.dispMoteRate()

        return self

    def moteRecv_update(self, macAddr):
        if macAddr in calRcvRate:
            calRcvRate[macAddr] = calRcvRate[macAddr] + 1
        else:
            calRcvRate.update({macAddr:1})
        return 1

    def dispMoteRate(self):
        #estimate how many pkt should be by time
        t = datetime.now()
        currTimeStr = t.strftime("%Y-%m-%d %H:%M:%S")
        globalTimeStr = progStartTime.strftime("%Y-%m-%d %H:%M:%S")

        elapseT= t - progStartTime
        estPkt = elapseT / secPerPkt
        estPkt_sec = estPkt.total_seconds()
        total = int(estPkt_sec) + 1.0

        for macAddr in calRcvRate:
            rate = calRcvRate[macAddr] / total
            #rate = rate * 100
            print 'Time:{0}, addr={1}, recvCnt={2}, total={3}, rate={4:.1%}'.format(currTimeStr, macAddr, calRcvRate[macAddr], total, rate)

    def neigRank_update(self, macAddr, rank):
        neigRankDic.update({macAddr:rank})
        return 1

    def pktSn_update(self, macAddr,snNum):
        serialSnDic.update({macAddr:snNum})
        return 1

    def pktSn_check(self, macAddr,snNum):
        try:
            if serialSnDic[macAddr] == snNum:
                print "the same sn"
                return 1
            else:
                print "not the same"
                return 0
        except:
            return 0

    def prune_table(self, srcTableName,dstTableName):
        db = MySQLdb.connect("localhost","root","sakimaru","ITRI_OpenWSN" )
        cursor = db.cursor()
        cursor.execute("")
        row = cursor.fetchone()
        while row is not None:
            row = cursor.fetchone()

    def age_mechanism(self):
        #sort by date
        db_seg = MySQLdb.connect("localhost","root","sakimaru","ITRI_OpenWSN" )
        db_tmp = MySQLdb.connect("localhost","root","sakimaru","ITRI_OpenWSN" )
        cursor_tmp = db_age.cursor()
        cursor_seg = db_seg.cursor()
        
        #get entry
        cursor_tmp.execute("SELECT * FROM itri_topology_tmp")
        cursor_seg.execute("SELECT * FROM itri_topology_seg")
        row = cursor_tmp.fetchone()
        while row is not None:
            #check ss_table for duplicate mac addr
            row[1]
            row = cursor_tmp.fetchone()


        #set age_cnt=0, insert into Result table

        #truncate tmp table

        #search for entry GTR MAX in table Resutl

        #truncate sstable, copy result table into it
        
        cursor_age.execute(sql)
        db_age.commit()
        db_age.close()

    def threadTimer(self, string, sleeptime, lock, *args):
        while(True):
            lock.acquire()
            print 'enter {0} timerThread, clear table'.format(string)
            db_tmp = MySQLdb.connect("localhost","root","sakimaru","ITRI_OpenWSN" )
            cursor_tmp = db_tmp.cursor()
            cursor_tmp("SELECT * FROM itri_topology_tmp")
            row_tmp = cursor_tmp.fetchone()
            while row_tmp is not NONE:
                row_tmp = cursor_tmp.fetchone()

            time.sleep(2)
            lock.release()
            time.sleep(sleeptime)
