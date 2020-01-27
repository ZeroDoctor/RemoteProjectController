import socket
import threading
import sys
import time
import msvcrt
import subprocess
from os import listdir
from os.path import isfile, join
from queue import Queue, Empty

sock = 0
path = 0 # path to the available scripts that can be executed
scripts = [] # scripts that can be executed
threads = []
q = Queue()

def getList():
# 	get list of files in the path directory
	onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
	onlyfiles.append('!end')
	return onlyfiles

def execCommand(data, path):
#	executes commands
	command = path + "\\" + data
	try:
		print("Log: exec => ", command, "...")
	# 	'shell=True' strongly discouraged because its vulnerable to shell injection
	#	but since we are using "start cmd /c" 'shell=True' must remain, for now.
		subprocess.call("start cmd /c " + command, shell=True) 
	except:
		print("Error: couldn't process " + command)

def sendScripts(scripts):
#	sends scripts to the server
	sock.send(':desktop'.encode('utf-8'))

	print('Log: sending ', scripts, "...")
	for file in scripts:
		sock.send(file.encode('utf-8'))
		time.sleep(0.25)

def main(ip):
	global sock, threads, q
	host = ip
	port = 9000

	sock = socket.socket()
	sock.settimeout(3)
	
	try:
		sock.connect((host, port))
	except socket.timeout:
		print('could not connect to server on: ', host, ' with port: ', port)
		return

	sock.settimeout(None)

	def getMessages(q, path, scripts):
	#	receive commands from server
		while True:
			data = sock.recv(1024).decode('utf-8')
			while True:
				try:
					command = q.get(block=True, timeout=1)
					q.task_done()

					if type(command) is list:
						scripts = command # send scripts to 'sendMessage' thread
					elif command == '!quit':
						print('Log: closing receving...')
						return
				except Empty:
					break

			if data == '!refresh':
				print('Log: resending scripts...')
				scripts = getList()
				sendScripts(scripts)
			elif any(data in s for s in scripts): # if data from server matches available scripts
				execCommand(data, path)
			
	def sendMessage(q, scripts):
	#	sends scripts to server and disconnect command to server
		sendScripts(scripts)

		while True:
			msg = msvcrt.getch()
			if msg == b'q':
				q.put('!quit') # sends quit command to 'getMessages' thread
				sock.send('!disconnect'.encode('utf-8'))
				print('Log: disconnecting...')
				return
			elif msg == b'r':
				print('Log: resending scripts...')
				scripts = getList()
				sendScripts(scripts)
				q.put(scripts)

	scripts = getList()
	thread = threading.Thread(target=getMessages, args=(q, path, scripts))
	threads.append(thread)

	thread = threading.Thread(target=sendMessage, args=(q, scripts))
	threads.append(thread)

	for thread in threads:
		thread.start()

	while True:
		pass

if __name__ == "__main__":
	if len(sys.argv) != 3:
		sys.exit("Error - usage " + sys.argv[0] + " <IPAddress> " + " <Path>")

	try:
		print("Press 'q' to quit or 'r' to refresh: ")
		path = sys.argv[2]
		main(sys.argv[1])
	except KeyboardInterrupt:
		print('Log: closing...')
		time.sleep(0.5)
	finally:
		q.join()
		for thread in threads:
			thread.join()
		sock.close()
		print('exited gracefully')