# Remote Project Controller

Remote Project Controller (RPC) is a system that allows the user to save project and 
execute scripts from a mobile device. Currently the system only works on windows.

## Screenshots / Demo

## Getting Started

This project is more of a personal project, so theres a lot of moving parts. 

### Chrome Extension

Probably the most annoying to deal with. Make sure to change the path variable in the background.js file to ./chrome_extension/tabpage/get_tabs.html. This is only temporary due to google, smartly, not giving developer access to users systems. 

1. Open the Extension Management page by navigating to chrome://extensions.
	- The Extension Management page can also be opened by clicking on the Chrome menu, hovering over More Tools then selecting Extensions.
2. Enable Developer Mode by clicking the toggle switch next to Developer mode.
3. Click the LOAD UNPACKED button and select the extension directory.
4. Select the ./chrome_extension folder
5. Done!

I say annoying because chrome will repeatly ask to disable the extension due to secuity. One way I avoided that message was to publish it privately to google chrome web store.

### %RPC%

The project "must be" in the Documents folder in order to work.

In addition, setup a environmental variable named "RPC" to the Project

ex. setx /M RPC "C:/Users/user_name/Documents/project_name"

### NPM

npm i readline-sync

npm i websocket

npm i ps-list

npm i child-process-promise

### Python

pip install keyboard

## Tech/Frameworks used

<b> built with </b>
- [Node.js](https://nodejs.org/en/)
- [Flutter](https://flutter.dev/)

## Contribute

Please email me before sending pull request.

### Meta

Daniel Castro - danielrcastro10@gmail.com

[website](http://zerodoctor.github.io/)
