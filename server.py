import socket
import threading
import urllib.request
import urllib.error
import re
import lcd
from queue import Queue, Empty
from time import *

sock = 0
q = Queue() # communitating between clients
logger = Queue() # communitating between clients and lcd
request = Queue() # communitating between server and lcd
threads = []

def log(string, logger=0):

#	print the string and sends the string
#	to the lcd via safe threaded queue

	if logger != 0:
		logger.put(string)
	print('Log: ' + string)

def warn(string, logger=0):
#	same as log above. Just did it for readability. maybe?
	if logger != 0:
		logger.put(string)
	print('Warning: ' + string)

def handleDesktop(user, conns, logger):

#	receives available scripts and 
#	returns the scripts to update 
# 	the mobile clients

	scripts = []
	desktop = user
	data = ''

	while data != '!end':
		data = conns[user][0].recv(1024).decode('utf-8')
		scripts.append(data)

	log('got scripts: ' + str(scripts), logger)
	return scripts

def handleMobile(user, conns, info, logger):
#	sends available desktop and their scripts to the mobile client
	log('sending: ' + str(info) + '...', logger)
	if len(info) == 0:
		conns[user][0].send(('$Empty').encode('utf-8'))
	else:
		for key in info:
			conns[user][0].send((":" + str(key) + ":" + str(info[key]) + ",").encode('utf-8'))

def checkDesktop(user, q, info, logger):

#	checks the client id for the desired desktop
#	and makes sure available scripts are updated

	log('process user id: ' + str(user), logger)
	try:
		info = q.get(block=False, timeout=1)
	except Empty:
		warn('queue is empty')
	finally:
		return info

def handleData(conns, user, q, data, logger, info={}):

#	Determines what to do with the incoming data
#	and sends updated scripts/desktop's id to other 
#	threads using a safe threaded queue. Also, 
#	sends desired scripts to execute to desktop

	info = checkDesktop(user, q, {}, logger)

	if data == ':desktop':
		log(data + ' request', logger)
		scripts = handleDesktop(user, conns, logger)
		info[int(user)] = scripts
	elif data == ':mobile':
		log(data + ' request', logger)
		handleMobile(user, conns, info, logger)
	else:
		if user not in info:
			msg = data.split(':')
			log('exec:' + str(msg[1].split('.')[0]) + '>>' + str(msg[0]), logger) # example: 'execute script: test.bat on desktop 1'
			conns[int(msg[0])][0].send((msg[1]).encode('utf-8'))

#	checking for new desktop removes 'info' from the queue
#	thus, put it back in
	q.put(info)
	return info

def client(conns, user, q, logger, request):
	desktop = 0
	info = {}

	while True:
	#	handles disconnects/general commands and processes client data
		try:
			data = conns[user][0].recv(1024).decode('utf-8')

			if data == '!disconnect':
				conns[user][0].send((data).encode('utf-8'))
				print('-------------------------------------')
				log('disconnecting user:', logger)
				log(str(user) + '| ' + str(conns[user][1][0]), logger)
				break

			# mobile clients can ask for updates (pending design)
			# if data == '!refresh':
			#	log('sending refresh...', logger)
			#	info = checkDesktop(user, q, {}, logger)
			#	if len(info) == 0:
			#		conns[user][0].send(('$Empty').encode('utf-8'))
			#	else:
			#		for k in info:
			#			conns[k][0].send((data).encode('utf-8'))
			#		conns[user][0].send(('$Done').encode('utf-8'))
			#	q.put(info)

			elif re.match("[:A-Za-z0-9_.-]", data): 
				print('---------------- msg ----------------')
				info = handleData(conns, user, q, data, logger)

		except:
			if not data:
				break

	#	remove current desktop from list if user is a desktop
	info.pop(user, None)
	try:
		item = q.get(block=False, timeout=1) # if queue is not empty then probably needs to be updated
	except Empty:
		log('queue was empty anyway')
	finally:
		q.put(info)

	log('closing conn...', logger)
	conns[user][0].close()
	conns.pop(user, None)
	request.put((threading.get_ident(), conns))

def lcdClient(conns, user, q, logger, request):
	desktop = 0
	info = {}

	while True:
	#	handles disconnects/general commands and processes lcd data
		try:
			data = conns[user][0].recv(1024).decode('utf-8')

			if data == '!disconnect':
				conns[user][0].send((data).encode('utf-8'))
				print('-------------------------------------')
				log('disconnecting lcd:', logger)
				log(str(user) + '| ' + str(conns[user][1][0]), logger)
				break
			elif data == '!shutdown':
				log('!close', logger)
				request.put('!shutdown')
				break

			info = checkDesktop(user, q, {}, logger)

			if data == '!refresh':
				log('sending refresh...', logger)
				if len(info) == 0:
					log('$Empty!', logger)
				else:
					temp = []
					for k in info:
						temp.append(conns[k][1][0])
						conns[k][0].send((data).encode('utf-8'))
					log('$Done! refreshed:' + str(temp), logger)

			elif data == '!info':
				log('grabbing desktops...', logger)
				if len(info) == 0:
					log('$Empty!', logger)
				else:
					for k in info:
						log('$' + str(conns[k][1][0]), logger)
					log('$Done!', logger)
					
			elif data == '!block':
				log('blocking conn...', logger)
				request.put('!block')

			q.put(info)
		except:
			if not data:
				break

def internet_on():
	try:
		urllib.request.urlopen('https://google.com', timeout=2)
		print('Log: pi is connected to the internet')
		return True
	except urllib.error.URLError as err: 
		return False

def main():
#	creates server on port 9000
	retry = 0
	while not internet_on(): 
	# 	the loop will last 25 seconds if no connection is made
		if retry >= 5:
			log('Could not connect to the internet at this time')
			return
		sleep(3)
		retry += 1

	host = ''
	port = 9000

	log('setting up socket...')
	sock = socket.socket()
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((host, port))
	sock.listen(5)

	scripts = []
	conns = {}
	quit = False
	block = False

	users = 0

#	implement LCD
	lcd.setup()
	thread = threading.Thread(target=lcd.start, args=(logger, request, port))
	thread.start()
	threads.append(thread)

#	connecting LCD to server
	conn, addr = sock.accept()
	conns[users] = (conn, addr);
	thread = threading.Thread(target=lcdClient, args=(conns, users, q, logger, request))
	thread.start()
	users += 1
	threads.append(thread)
	
	log('Listening for connections on port 9000')
	try:
#	waits for connection from client a create its own thread
		while not quit:
			conn, addr = sock.accept()
			try:
				command = request.get(block=False, timeout=1)
				if command == '!block':
					block = True
					log('$success', logger)
				elif command == '!release':
					block = False
				elif command == '!shutdown':
					quit = True
					conn.close()
					break
				elif type(command) == tuple:
					log('updating connections...')
					conns = command[1]

					log('joining thread...')
					for t in threads:
						if command[0] == t.ident:
							t.join()
							threads.remove(t)
							break
				else:
					warn('(LCD): unhandled command: ' + str(command))

			except Empty:
				pass

			if not block:
				conns[users] = (conn, addr);
				print('-------------------------------------')
				log('conn: ' + str(addr[0]), logger)

				thread = threading.Thread(target=client, args=(conns, users, q, logger, request))
				thread.start()
				users += 1
				threads.append(thread)
			else:
				log('User data blocked', logger)
	except KeyboardInterrupt:
		quit = True
		sock.shutdown(socket.SHUT_RDWR) # for now (this is here for the lcd connection)
		conns[0][0].close()
		logger.put('!close')
	finally:
#	waits for threads to join and closes socket
		log('closing server...')
		for thread in threads:
			thread.join()

		sock.close()

if __name__ == '__main__':
	main()