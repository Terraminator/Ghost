import socket
import threading
import sys
import ssl
import os
import certifi

class Proxy:

	def __init__(self, ip="", port=3000):
		self.ip = ip
		self.port = port
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.run()
		
	def run(self):
		self.server.bind((self.ip, self.port))
		self.server.listen(100)
		print("Listening on 127.0.0.1" + ':' + str(self.port))

		while True:
			client_socket, addr = self.server.accept()
			print("{} has just connected!".format(addr[0]))
			t = threading.Thread(target = self.handle_request, args=(client_socket,))
			t.start()
				
	def handle_request(self, client_socket):
		packet = client_socket.recv(4096)
		rc = self.connect(packet)
		client_socket.send(b"HTTP/1.1 200 Established\r\n\r\n")
		while True:
			try:
				packet = b''
				packet = client_socket.recv(4096)
				if packet != b'':
					packet = self.filter_packet(packet)
					rc.send(packet)
					#print("request:", packet.decode("utf8"))
					rsp = rc.recv(8096)
					client_socket.send(rsp)
					if rsp != '':
						print("response:", rsp.decode("utf8"))
						client_socket.send(rsp)
				else:
					return(0)
				
			except Exception as e:
				print(e)
		
		
	def get_host(self, packet):
		packet = packet.decode("utf8")
		spack = packet.split()
		pack = spack[1]
		div = pack.find(':')
		
		host = ""
		n=0
		for n in range(0, div):
			host += str(pack[n])
			n+=1
			
		n = 0
		port = ""
		for n in range(div+1, len(pack)):
			port += str(pack[n])
			
		print(host, port)
		return(host, port)
		
	def connect(self, packet):
		host, port = self.get_host(packet)
		rc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		rc.settimeout(10)
		context = ssl.create_default_context()

		sock = socket.create_connection((str(socket.gethostbyname(host)), int(port)))
		ssock = context.wrap_socket(sock, server_hostname=host)
		print(ssock.version())
			
		return(ssock)
		
		
	def filter_packet(self, packet):
		return(packet)
		
	def close(self):
		self.server.close()