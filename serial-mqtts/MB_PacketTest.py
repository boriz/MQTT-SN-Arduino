import socket  
import serial
import sys
import time
import datetime
from struct import *

#SerPort = '/dev/ttyAMA0'
SerPort = 'COM19'
DEST_ADDR = 0xEAF6

# From firmware_at_api.h
API_DATA_LEN = 20
AT_PARAM_LEN = 8 
API_START_DELIMITER = 0x7E

OPTION_CAST_MASK = 0x40    #option unicast or broadcast MASK
OPTION_ACK_MASK = 0x80    #option ACK or not MASK

API_REMOTE_AT_REQ = 0x17
API_DATA_PACKET = 0x02
API_TX_REQ = 0x01          #Tx a packet to special short address
API_TX_RESP = 0x03
API_RX_PACKET = 0x81       #received a packet from air,send to UART

ATIO = 0x70

#convert string to hex
def ToHex(s):
	retHex=""
	for c in s:
		retHex = retHex + "%#04x " % c
	return retHex

	
# Connect to serial SerPort
def ConnectSer ():
	try:
		print "Connecting to Serial:"+SerPort+" ... ",
		ser = serial.Serial(SerPort, 115200, timeout=1)		
		ser.flush()
		print "Connected"
		return ser
	except:
		print "Failed to connect to serial port"
		raise SystemExit

		
# Create TX data
def CreateTx (data):
	# data array
	dat = bytearray(data)

	# payload data (tsTxDataPacket)
	pay = bytearray()
	pay.append (pack('>B', 1)) # frame id
	pay.append (pack('>B', 0)) # option
	pay.append (pack('>B', len(dat))) # data length
	pay = pay + dat # add data
	for s in range (API_DATA_LEN - len(dat)):	# fill the rest of the data with zeros
		pay.append (pack('>B', 0))
	pay = pay + bytearray(unpack('2B', pack('>H', DEST_ADDR))) # Unicast address (16 bits)

	# Create a packet (tsApiSpec)
	rep = bytearray()
	rep.append(pack('>B', API_START_DELIMITER))	# Delimiter
	rep.append(pack('>B', len(pay)))	# Length of the payload
	rep.append(pack('>B', API_TX_REQ))	# API ID	
	rep = rep + pay
	cs = sum(pay) & 0xFF	#checksum
	rep.append(pack('>B', cs))	# Checksum (payload only, sum of all bytes)
	return rep

	
# Create At frame
def CreateAtIO (par):
	# data array
	p = bytearray(par)

	# payload data (tsTxDataPacket)
	pay = bytearray()
	pay.append (pack('>B', 1)) # frame id
	pay.append (pack('>B', 0)) # option
	pay.append (pack('>B', ATIO)) # ATIO command
	pay = pay + p # add data (AtIO command parameters)
	for s in range (AT_PARAM_LEN - len(p)):	# fill the rest of the parameters with zeros
		pay.append (pack('>B', 0))
	pay = pay + bytearray(unpack('2B', pack('>H', DEST_ADDR))) # Unicast address (16 bits)

	# Create a packet (tsApiSpec)
	rep = bytearray()
	rep.append(pack('>B', API_START_DELIMITER))	# Delimiter
	rep.append(pack('>B', len(pay)))	# Length of the payload
	rep.append(pack('>B', API_REMOTE_AT_REQ))	# API ID	
	rep = rep + pay
	cs = sum(pay) & 0xFF	#checksum
	rep.append(pack('>B', cs))	# Checksum (payload only, sum of all bytes)
	return rep


# Main program
# Create API_TX_REQ packet
s = CreateTx('Test')
#s = CreateAtIO('\x09\x01')	# IO pin for LED9, turn it on

# Print it
print "Packet:" + ToHex(s)

# Send over serial
print "Sending Serial"
ser = ConnectSer()
ser.write(s)
ser.flush()
if ser:
	ser.close()
print "Done"

