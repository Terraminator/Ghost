import socket
import threading
import os
import queue
import signal

SRV_ADDR="127.0.0.1"
SRV_PORT=8080

threads=[]

try:
	with open("blacklist.txt", "r") as f:
		blacklist=f.read()
except:
	blacklist=""

def filter_in(data):
	#if data!=b"": print(b"in:", data)
	return(data)

def filter_out(data):
        #if data!=b"": print(b"out:", data)
        return(data)

def get_data(c, q):
	while True:
		try:
			buff=filter_in(c.recv(4096))
			if buff!=b"": q.put(buff)
		except Exception as e:
			print(e)
			c.close()

def send_data(c, q):
	while True:
		try:
			buff=filter_out(q.get())
			if buff!=b"": c.send(buff)
		except Exception as e:
			print(e)

def is_bad(url):
	url=url.split(":")[0]
#	print(url)
	if url in blacklist:
		print("blocked {}!".format(str(url)))
		return(True)
	else:
		return(False)

def handle_request(c, addr):
	initial_packet = c.recv(1024)
	#print(initial_packet)
	if not b"CONNECT" in initial_packet:
		print("error connect not found!")
		return(-1)
	else:
		try:
			target=initial_packet.split(b"CONNECT ")[1].split(b"HTTP")[0].decode()
			f=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if is_bad(target): return(-1)
			f.connect((target.split(":")[0], int(target.split(":")[1])))
			print("connected to", target)
			print("sending:", "HTTP/1.0 200 Connection established\r\n\r\n")
			c.send(b"HTTP/1.0 200 Connection established\r\n\r\n")
			q1 = queue.Queue()
			q2 = queue.Queue()
			in1=threading.Thread(target=get_data, args=(c,q1,))
			threads.append(in1)
			in1.start()
			out1=threading.Thread(target=send_data, args=(f,q1,))
			threads.append(out1)
			out1.start()
			in2=threading.Thread(target=get_data, args=(f,q2,))
			threads.append(in2)
			in2.start()
			out2=threading.Thread(target=send_data, args=(c,q2,))
			threads.append(out2)
			out2.start()
			print("io threads started...\ntunnel established!")
			in1.join()
			out1.join()
			in2.join()
			out2.join()
		except Exception as e:
			print(e)
			try:
				c.close()
				f.close()
			except:
				pass
def wait_for_r():
	s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((SRV_ADDR, SRV_PORT))
	s.listen(20)
	print("proxy server listening on {}:{}\nMade by Terraminator".format(SRV_ADDR, str(SRV_PORT)))
	while True:
		c,addr=s.accept()
		t=threading.Thread(target=handle_request, args=(c,addr,))
		threads.append(t)
		t.start()

def signal_handler(sig, frame):
	print("exiting...")
	for t in threads:
		del t
	exit(0)


if __name__=="__main__":
	signal.signal(signal.SIGINT, signal_handler)
	wait_for_r()
