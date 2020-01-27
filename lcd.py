import socket
import RPi.GPIO as GPIO
import re
import lib.display_states as ds
from queue import Queue, Empty
from time import *

BTN_PREV = 11
BTN_NEXT = 13
BTN_ENTR = 15
BTN_EXIT = 19

log = [] # server log
states = [] # all possible states/commands the user can do on LCD
current = 0 # the current state

sock = socket.socket() # this is going to get weird starting on line 132
sip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # for the ip address

def send_server(command):
	global sock
	sock.send(command.encode('utf-8'))

# the following function are custom callbacks will execute once the user 
# chooses the command through the main menu.
# also, the main menu is the first state

def menu_func(): # dont need this really
	ds.current_line = 0
	ds.menu = 1
	ds.home = 1

def refresh_func():
	send_server('!refresh')

def info_func():
	send_server('!info')

def block_func():
	send_server('!block')

def shutdown_func():
	global sock
	send_server('!shutdown')
	sleep(1)
	force_shutdown()

# end custom callbacks

def button_callback(button):
	global states, current

	if button == 0 and ds.current_line > 0:
		ds.current_line += -1
		ds.next_line(states[current].get_text())

	if button == 1:
		ds.current_line += 1
		ds.next_line(states[current].get_text())

	if button == 2:
		if ds.home == 1:
			ds.home = 0
			ds.menu = 0
			ds.clear()
			current = ds.current_line + 1
			states[current].display(scommand=True) # start the state the cursor is currently on

	if button == 3:
		if ds.home == 0:
			if current != 1:
				states[current].clear_text()
			current = 0
			states[0].display(scommand=True)

def setup():
	GPIO.setmode(GPIO.BOARD)

	GPIO.setup(BTN_PREV, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(BTN_NEXT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(BTN_ENTR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(BTN_EXIT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	GPIO.add_event_detect(BTN_PREV, GPIO.FALLING, callback=lambda x: button_callback(0), bouncetime = 300)
	GPIO.add_event_detect(BTN_NEXT, GPIO.FALLING, callback=lambda x: button_callback(1), bouncetime = 300)
	GPIO.add_event_detect(BTN_ENTR, GPIO.FALLING, callback=lambda x: button_callback(2), bouncetime = 300)
	GPIO.add_event_detect(BTN_EXIT, GPIO.FALLING, callback=lambda x: button_callback(3), bouncetime = 300)

def force_shutdown(command=0):

#	the server main while loop is constantly looking for a connection.
#	thus, in order for the shutdown request to go through a connection must
#	made. Eventually, I could create another thread listening for client connection and
# 	perhaps kill the thread from the main thread

	global host
	sip = socket.socket()
	try:
		sip.connect((host, 9000))
		if command != 0:
			sip.send(command.encode('utf-8'))
	except:
		print('Warning: failed to connect...')

	sip.close()

def sock_setup():
	global sip
	try:
		sip.connect(('10.255.255.255', 1))
		ip = sip.getsockname()[0]
	except:
		ip = '127.0.0.1'
		print('Warning: failed to get ip...')

	return ip

def start(logger, request, port):
	global host, log, sock, sip, success, current

	host = str(sock_setup())

	# It works. Definitely unorthodox, and most likely frown upon by society, probably.
	# reason describe at the bottom of this page
	sock.connect((host, port))
	print('Log: LCD connected to server...')
	sip.close()

	# if LCD is not plugged in or has different address then excepted
	if not ds.checkLCD():
		send_server('!shutdown')
		sleep(1)
		force_shutdown()
		return

	ds.init()

	states.extend([
		ds.State(
			['Menu:' + host, 
			' 1.Log', 
			' 2.Refresh',
			' 3.Desk Info',
			' 4.Block',
			' 5.Shutdown'], True, command=menu_func),

		ds.State(log, end=True),
		ds.State('Refreshing...', command=refresh_func, clear=True),
		ds.State('Get Info...', command=info_func, clear=True),
		ds.State('Blocking Conn...', command=block_func, clear=True),
		ds.State('Bye.', command=shutdown_func)
	])

	states[0].display(scommand=True)

	while True:
		try:
			command = logger.get(block=False, timeout=1)
			if command == '!close':
				print('Log: LCD disconnected from server')
				sock.close()
				sleep(1) # wait for 'bye' to be printed
				break
			elif command[0] == '!':
				print('Warning (LCD): unhandled command: ', command)
			elif command[0] == '$':
				states[current].display(command[1:len(command)])
				sleep(0.3)
			else:
				log.append(command)
				states[1].update_text(replace=log)
				if current == 1:
					states[1].display(replace=log) # hopefully log is in index 1
		except Empty:
			sleep(3)
	return

# 