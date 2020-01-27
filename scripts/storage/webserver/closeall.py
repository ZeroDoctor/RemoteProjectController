import json
import subprocess

l = []

with open('programs.json') as json_file:
    data = json.load(json_file)
    for p in data:
        l.append(p['name'])

command = ['CloseWindows']
command.extend(l)

subprocess.call(command)