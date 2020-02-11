#######
# sm.py ~= session manager
# 
# Session manager is a quick way to access and run scripts.
# Simply a easier way to run scripts when not AFK. Mobile manager
# now will act in way to run scripts for laptops and other devices.
#
#######
import keyboard
import subprocess
from os import listdir
from os.path import isfile, join

current_folder = ""
index_folder = [""]
folders = {"":[]}
selections = []
options = 0
page = 0
done = False

def get_list(path):
# 	get list of files in the path directory
#	onlyfiles = [(i, f, 0) for i, f in enumerate(listdir(path)) if isfile(join(path, f))]
	options = []
	folder_num = 0
	# (location, name, ignore, folder = True)
	for i, f in enumerate(listdir(path)):
		if isfile(join(path, f)):
			ignore = f[1] == '-'
			options.append((i, f, ignore, False))
		elif f != "storage":
			options.insert(folder_num, (i, "^" + f, ignore, True))
			index_folder.append(f)
			folders[f] = get_list(join(path, f))
			folder_num += 1

	return options

def exec_command(data):
#	executes commands
	command = "C:\\Users\\danie\\Documents\\AutoInterface\\scripts\\" + data
	try:
		print("Log: exec => ", command, "...")
	# 	'shell=True' strongly discouraged because its vulnerable to shell injection
	#	but since we are using "start cmd /c" 'shell=True' must remain, for now.
		subprocess.call("start cmd /c " + command, shell=True) 
	except:
		print("Error: couldn't process " + command)

def show_options(files, page):
	global selections
	print('----------------------\n')
	print("Page->", page)
	result = ""
	selections = []

	i = 0
	for j, f in enumerate(files):
		
		if f[2] == False and j >= page * 10 and i < 10:
			option_num = i % 10
			i += 1 
			result += str(option_num)
			selections.append(f)
			if f[1][0] != '^':
				result += ": " + f[1][:-4] + "\n"
			else:
				result += ": " + f[1] + "\n"

	print(result)

def prevpage():
	global options, page
	page -= 1
	if page < 0: page = 0
	show_options(options, page)


def nextpage():
	global options, page
	page += 1 
	show_options(options, page)

def push_command(command):
	global options, selections, page, current_folder, done
	select = selections[command]

	if select[1][0] == '^':
		page = 0
		options = folders[select[1][1:]]
		current_folder = select[1][1:]
		show_options(options, page)
	else:
		exec_command(current_folder + "\\" + select[1])
		done = True


def home_folder():
	global options, page, current_folder

	page = 0
	options = folders[""]
	current_folder = ""
	show_options(options, page) 

def main():
	global options, page

	path = "C:\\Users\\danie\\Documents\\AutoInterface\\scripts"

	options = get_list(path)
	folders[""] = options

	show_options(options, page)
	print("press option: ")

	keyboard.add_hotkey('f', nextpage)
	keyboard.add_hotkey('a', prevpage)
	keyboard.add_hotkey('b', home_folder)

	for i in range(-1, 9):
		keyboard.add_hotkey(str(i + 1), push_command, args=[i + 1])

	while not done:
		try:
			if keyboard.is_pressed('esc'):
				print("\n----------------------\nclosing program...\n")
				break
		except Exception as e:
			print(e)
			break

if __name__ == "__main__":
	main()