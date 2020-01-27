import lib.liq_ic2 as liq_ic2

print("Log: lcd takes a while...")
lcd = liq_ic2.LiquidCrystal_I2C(0x3f, 1, numlines=4)

def checkLCD(): # checking if the lcd has power or is readable
	return lcd.exist()

def init():
	global text, current_line, menu

	text = [] # current displayed text
	menu = 0 # if the current text is part of a menu or not
	home = 0 # if the current text is the main menu
	current_line = 0 # the current line that the cursor is on or the first line (or second line if state is a menu)

def auto_adjust(string):
#	splits string into chucks of 20 characters or less
	result = []
	if len(string) <= 20:
		result.append(string)
		return result
	
	splits = int(len(string) / 20) + 1

	for i in range(splits):
		start = i*20
		end = (start + 20)
		if(end > len(string)): end = len(string)

		result.append(string[start:end])

	return result

def print_str(string, end=False):

#	formats the string. later this will offset
#	in order for the last string in the list to
#	be on the fourth line displayed on the lcd

	result = []
	if type(string) is list:
		for s in string:
			result.extend(auto_adjust(s))
	else:
		result = auto_adjust(string)

	# offset = 0
	# if end and offset > 4:
	#	offset = len(result) - 4

	return result

def next_line(text, end=False):
#	prints the current 4 lines on the lcd
	global current_line, menu

	for i in range(4):
		temp = ''
		if i + current_line < len(text):
			if not menu == 0:
				if menu == i:
					temp = '>'
				else:
					temp = ' '

			temp += text[i+current_line] + ' ' * (20 - len(text[i+current_line]) - len(temp))
			lcd.printline(i, temp)
		else:
			lcd.printline(i, ' ' * 20) # faster than clearing the screen

def clear():
	for i in range(4):
		lcd.printline(i, ' ' * 20)

class State:

#	stores desire text to be displayed and commands to execute once pressed
#	text = list of string ready to display
#	end = if true display the end of text first
#	command = function callback
#	args = list of arguments for command callback
# 	clear = clears text once command is executed again 

	def __init__(self, text, end=False, command=0, args=0, clear=False):
		if type(text) is list:
			self.text = text
		elif type(text) is str:
			self.text = []
			self.text.append(text)
		
		self.command = command
		self.args = args
		self.end = end
		self.clear = clear

	def clear_text(self):
		if clear:
			self.text = []

	def get_text(self):
		return self.text

	def update_text(self, etext=0, replace=0):
		if etext != 0:
			self.text.extend([etext])
		elif replace != 0:
			self.text = replace

	def display(self, etext=0, replace=0, scommand=False):
		global current_line
		if scommand: self.start_command()
		

		self.update_text(etext, replace)
		self.text = print_str(self.text, self.end)

		if self.end and len(self.text) >= 5: 
			current_line = (len(self.text) - 5)
		else:
			current_line = 0

		next_line(self.text, self.end)

	def start_command(self):
		if self.command != 0:
			if self.args == 0:
				self.command()
			else:
				self.command(self.args)
