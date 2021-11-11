import socket
import threading


class Proxy:

	def __init__(self, ip="192.168.178.38", port=3000):
		self.ip = ip
		self.port = port
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.run()
		
	def run(self):
		self.server.bind((self.ip, self.port))
		self.server.listen(100)
		print("Listening on", str(self.ip) + ':' + str(self.port))

		while True:
			client_socket, addr = self.server.accept()
			print("{} has just connected!".format(addr[0]))
			t = threading.Thread(target = self.handle_request, args=(client_socket,))
			t.start()
				
	def handle_request(self, client_socket):
		while True:
			try:
				packet = client_socket.recv(4096)
				host, port = self.get_host(packet)
				packet = self.filter_packet(packet)
				if packet !='':
					print(packet)
					print(host)
					rc = self.forward(host, port, packet)
					rsp = self.get_response(rc)
					print(rsp)
					client_socket.send(rsp)
			except:
				pass

	def filter_packet(self, packet):
		return(packet)
		
		
	def get_host(self, packet):
		spack = packet.split()
		pack = spack[1]
		pack = pack.decode("utf8")
		div = pack.find(':')
		
		host = ""
		n=0
		for n in range(0, div):
			host += str(pack[n])
			n+=1
			
		host = socket.gethostbyname(host)
		
		n = 0
		port = ""
		for n in range(div+1, len(pack)):
			port += str(pack[n])
			
		return(host, port)
		
	def forward(self, host, port, packet):
		rc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		rc.connect((host, int(port)))
		rc.send(packet)
		return(rc)
		
	def get_response(self, rc):
		response = rc.recv(4096)
		return(response)
		
	def close(self):
		self.server.close()