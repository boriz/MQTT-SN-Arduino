import socket    
import serial
import sys
import time
import datetime
from struct import *

SerPort = '/dev/ttyAMA0'
#SerPort = 'COM23'
BrokerHost = "192.168.1.10"
BrokerPort = 1883

API_DATA_LEN = 20
API_DATA_PACKET = 0x02

#convert string to hex
def ToHex(s):
	retHex=""
	for c in s:
		retHex = retHex + "%#04x " % ord(c)
	return retHex
	
#connect to serial SerPort
def ConnectSer ():
	try:
		print "Connecting to Serial:"+SerPort+" ... ",
		ser = serial.Serial(SerPort, 115200, timeout=1)		
		ser.write("ATAP\n")
		ser.flush()
		time.sleep(0.1)
		ser.flushInput()
		print "Connected"
		return ser
	except:
		print "Failed to connect to serial port"
		raise SystemExit

# Class to hold connection information
class conn:
    def __init__(self):
		self.sock
		self.src_addr
		self.frame_id
		

# Create TX data
def CreateTx (dest_addr, data):
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
	pay = pay + bytearray(unpack('2B', pack('>H', dest_addr))) # Unicast address (16 bits)

	# Create a packet (tsApiSpec)
	rep = bytearray()
	rep.append(pack('>B', API_START_DELIMITER))	# Delimiter
	rep.append(pack('>B', len(pay)))	# Length of the payload
	rep.append(pack('>B', API_DATA_PACKET))	# API ID	
	rep = rep + pay
	cs = sum(pay) & 0xFF	#checksum
	rep.append(pack('>B', cs))	# Checksum (payload only, sum of all bytes)
	return rep

	
# Parse RX data
def ParseRx (ser_data):
	# data array
	dat = bytearray(ser_data)
	
	try:
		# Header
		i=0
		delimiter = dat[i]  # Delimeter
		#print "delimiter" + str(delimiter)
		i += 1
		pay_len = dat[i]	# Payload length	
		#print "pay_len" + str(pay_len)
		i += 1
		api = dat[i] 		# API ID
		i += 1

		# payload data (tsTxDataPacket)		
		fid = dat[i]	# frame id
		i += 1
		opt = dat[i]	# option
		i += 1
		dat_len = dat[i]	# data length
		#print "dat_len" + str(dat_len)
		i += 1
		d_start = i
		d = bytearray()	# Data
		for s in range (dat_len):
			d.append(dat[i])
			i += 1
			
		# Grab source address (data start + data length)
		i = d_start + API_DATA_LEN
		src = dat[i] * 256 + dat[i+1]
		return (src, d)
		
	except:
		return (None, None)

	
# Main loop
data_ser = ""
data_udp = ""
conns = []
host_ip = socket.gethostbyname(BrokerHost)
ser = ConnectSer()
while True:
	try:
		# Try to get serial data
		if ser.inWaiting() > 0:
			data_ser = ser.read(1)
			if ord(data_ser[0]) != 0x7E:
				# Should start with 0x7E
				print "Wrong frame delimiter:%#04x" % ord(data_ser[0])
				ser.flushInput()
				data_ser = ""
				time.sleep(0.1)
				continue
			
			# Get the rest of the packet
			print "Frame start detected"
			while ser.inWaiting() > 0:				
				while ser.inWaiting() > 0:
					data_ser = data_ser + ser.read(1)				
				time.sleep(0.05)
				
		# Got serial data
		if data_ser:
			l = len(data_ser)
			print "SER Got frame:" + ToHex(data_ser) + "; len:" + str(l)
			
			# Parse the frame 
			src = None
			payload = None
			(src, payload) = ParseRx(data_ser)
			
			# Clear serial data
			data_ser=""			
			
			# Valid data?
			if src and payload:		
				# Valid data !
				print "SER Source addr:" + hex(src) 
				print "SER Payload:",
				for s in payload:
					print hex(s),
				print
				
				# Try to find a corresponding connection by source address
				cn = None
				for i in conns:
					if i.src_addr == src:
						cn = i
						print "SER Found source address:" + "%#04x" % cn.src_addr
				
				# Found record?
				if not cn:
					# Nope, create a new record
					cn = conn
					cn.src_addr = src
					cn.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
					cn.sock.bind(('',0))
					cn.sock.setblocking(0)
					cn.frame_id = 1
					conns.append(cn)
					print "SER Create new connection, Src:" + "%#04x" % cn.src_addr + " Port:" + str(cn.sock.getsockname()[1])

				# send serial data to UDP
				cn.sock.sendto(payload, (host_ip, BrokerPort))
				print "SER Sent to UDP"
			else:
				print "SER Wrong frame format" 
		
		# Check for incoming UDP data
		for i in conns:
			try:
				data_udp = i.sock.recv(256)
			except:	
				data_udp=""
			
			# Got udp data for client
			if data_udp:
				print "UDP input for address:" + "%#04x" % i.src_addr
				print "UDP payload:" + ToHex(data_udp)		
				rep = CreateTx(i.src_addr, data_udp)
				s = ''.join(rep)
				ser.write(s)
				ser.flush()
				print "UDP sent to serial:" + ToHex(s)
				time.sleep(0.05)
			
	except KeyboardInterrupt:
		print "CTRL-C"
		break
        
		
print "Closing Serial and UDP"	
ser.close()
for i in conns:
	if i.sock:
		i.sock.close()
print "Closed"

