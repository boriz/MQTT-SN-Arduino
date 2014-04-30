import socket    
import serial
import sys
import time
import datetime

SerPort = '/dev/ttyAMA0'
#BrokerHost = "192.168.0.2"
BrokerHost = "localhost"
BrokerPort = 1883
LocalPort = 1887
#BrokerHost = "test.mosquitto.org"
#BrokerPort = 1883


#convert string to hex
def prnHex(s):
	for c in s:
		print "%#04x" % ord(c),

	
#connect to serial BrokerPort
def ConnectSer ():
	global ser
	try:
		print "Connecting to Serial ... ", SerPort
		ser = serial.Serial(SerPort, 115200, timeout=1)
		ser.flush()
	except:
		print "Failed to connect to serial BrokerPort"
		raise SystemExit
		
	print "Connected"
	print

def ConnectUDP ():
	global sockLocal
	try:
		print "Creating UDP Listener ... "
		sockLocal = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sockLocal.bind(("0.0.0.0", LocalPort))
		sockLocal.setblocking(0)
	except:
		print "Failed to bind"
		ser.close()
		raise SystemExit
					 
	print "Connected"
	print

	
# def ConnectTCP ():
	# global sock
	# try:
		# host_ip = socket.gethostbyname(BrokerHost)
		# print "Connecting to TCP server ... ", host_ip
		# sockLocal = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# sockLocal.connect((host_ip, BrokerPort))
		# sockLocal.setblocking(0)
	# except:
		# print "Failed to connect TCP server"
		# ser.close()
		# raise SystemExit
					 
	# print "Connected"
	# print

	
# Main loop
ConnectSer()
#ConnectTCP()
ConnectUDP()

data_ser = ""
data_tcp = ""
while True:
	try:
		if ser.inWaiting() > 0:
			#st=datetime.now()
			while ser.inWaiting() > 0:
				data_ser = data_ser + ser.read(1)
			time.sleep(0.01)
			continue
		if data_ser:
			if not sockLocal:
				ConnectTCP()
				ConnectUDP()
			print "SER IN>",
			prnHex(data_ser)
#			sockLocal.sendall(data_ser)
			host_ip = socket.gethostbyname(BrokerHost)
			#sockSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sockLocal.sendto(data_ser, (host_ip, BrokerPort))
			#sockSend.close()
			print "   -> Sent"
			data_ser=""
		
		#data_tcp = sockLocal.recv(1024)	
		try:
			data_tcp, address = sockLocal.recvfrom(1024)
		except socket.error:	
			data_tcp=""
		
		if data_tcp:
			print "TCP IN>",
			prnHex(data_tcp)
			ser.write(data_tcp) 
			print "   -> Sent"
    		
#		sys.stdin.read()
	except KeyboardInterrupt:
		print "CTRL-C"
		break
        
	# except IOError, e: 
		#error 10054 connection closed
		# if e.errno == 10054:
			# print "TCP disconnect exception"
			# sock.close()
			# continue
		
		#error 10035 is no data available, it is non-fatal
		# if e.errno != 10035:
			# print "Failed to send/receive: " + e.strerror
			# break
		
	# except Exception, e:
		# print "Exception: " + e.strerror
		# break
		
print "Closing Serial and TCP"	
sockLocal.close()
ser.close()
print "Closed"

