import socket    
import serial
import sys
import time
import datetime
from struct import *

#SerPort = '/dev/ttyAMA0'
SerPort = 'COM9'
BrokerHost = "192.168.1.10"
BrokerPort = 1883
SourceAddress = 0x5DF7

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
		ser.write("ATEX\n")
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
		
	
# Main loop
data_ser = ""
data_udp = ""
conns = []
host_ip = socket.gethostbyname(BrokerHost)
ser = ConnectSer()
ser.write('\x7E\x00\x11\x90\x00\x00\x00\x00\x00\x00\x00\x00\x06\x07\x00\x01\x02\x03\x04\x05\x60');
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
			time.sleep(0.05)
			while ser.inWaiting() > 0:
				data_ser = data_ser + ser.read(1)
				time.sleep(0.05)
		
		# Got serial data
		if data_ser:
			l = len(data_ser)
			print "Got frame:" + ToHex(data_ser) + "; len:" + str(l)
			# Find source address (2 bytes)
			try:			
				src = unpack('>H', data_ser[12:14])[0]
				payload = data_ser[15:l-1]
			except:
				print "Parsing serial data exception:", sys.exc_info()
				data_ser=""	
				continue
			
			# Clear serial data
			data_ser=""			
			
			# Parse what seems to be a valid data
			print "SER Source addr:" + hex(src) 
			print "SER Payload:" + ToHex(payload)
			
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
				print "SER Create new connection:" + "%#04x" % cn.src_addr + " Port:" + str(cn.sock.getsockname()[1])

			# send serial data to UDP
			cn.sock.sendto(payload, (host_ip, BrokerPort))
			print "SER Sent Ok"

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
				rep = []
				rep.append(pack('>B', 0x7E))	# Delimiter
				rep.append(pack('>H', (len(data_udp) + 13)))	# Length, except delimiter and crc 
				rep.append(pack('B', 0x90))	# API 90				
				rep.append(pack('>Q', 0x0000000000000000))	# Src addr
				rep.append(pack('>H', SourceAddress )) # Src addr short
				rep.append(pack('B', 0x00))	# Options	
				for x in data_udp:
					rep.append(pack('B', ord(x)))	# Data	
				rep.append(pack('B', 0x00))	# Checksum
				dst = "ATDA" + hex(i.src_addr)[2:]
				print "UDP Select destination: " + dst
				ser.write("+++")
				ser.write(dst + "\n")
				ser.write("ATEX\n")
				s = ''.join(rep)
				ser.write(s)
				ser.flush()
				print "UDP sent to serial:" + ToHex(s)
				time.sleep(0.1)
				# Probably got a bunch of the OK from AT commands. Discard it
				ser.flushInput()
			
	except KeyboardInterrupt:
		print "CTRL-C"
		break
        
		
print "Closing Serial and UDP"	
ser.close()
for i in conns:
	if i.sock:
		i.sock.close()
print "Closed"

