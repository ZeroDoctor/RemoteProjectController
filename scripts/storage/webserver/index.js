"use strict";
var homedrive = process.env.homedrive;
var homepath = process.env.homepath;
var tabspath = 'file:///' + homedrive + homepath + '/Documents/AutoInterface/chrome_extension/tabpage/get_tabs.html';

// websocket, process, process list, http servers, and file system
var webSocketServer = require('websocket').server;
var spawn = require('child_process').spawn;
var exec = require('child_process').exec;
var psList = require('ps-list');
var http = require('http');
var fs = require("fs");

var contents = fs.readFileSync("programs.json");
var programlist = JSON.parse(contents);
var programs = [];

const input = require('readline-sync');

var filename = input.question('Session Name?: ');
var proj_file = input.question('Project Path?: ');
var close_explorer = input.question('Close Explorer (y/n): ');
var proj_exist = false;


main();

async function main() {
    if(filename.length == 0) {
        filename = makeid(6);
    }
    
    filename += ".bat";
    filename = "../../s-" + filename;
    createfile(filename);
    if(proj_file.length != 0 && proj_file.includes('C:')) {
        addtofile('cd "' + proj_file + '" && start .\n');
        proj_exist = true;
    }
    await getprocess(programlist);
}

function makeid(length) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for ( var i = 0; i < length; i++ ) {
       result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
}

function createfile(filename) {
    fs.writeFile(filename, '@echo off\ncls\necho loading session...\n', function (err) {
        if (err) throw err;
        console.log(filename + ' Created!');
    });
}

function addtofile(commands) {
    fs.appendFile(filename, commands, function (err) {
        if (err) throw err;
        console.log(filename + ' Updated! with ' + commands);
    });
}

async function getprocess(programlist) {
    var serverstart = false;
    var list = await psList();
    var commands = "";

    for(var i = 0; i < list.length; i++) {
        var temp = list[i]['name'];
        
        if(!serverstart && temp == 'chrome.exe') {
            serverstart = true;
            programs.push(temp);
            start();
            try {
                setTimeout(function(){startclient()}, 1000);
            } catch (error) {
                console.log(error);
            }
        } else if(programs.indexOf(temp) == -1) {
            var exist = -1;
            var temp_project = '';
            // re-visit this later
            for(var j = 0; j < programlist.length; j++) {
                if(programlist[j]['name'] == temp) {
                    exist = j;
                    temp_project = programlist[j];
                    break;
                }
            }

            if(exist != -1) {
				programs.push(temp);
				var comm = ''
                if(proj_file.length != 0 && proj_exist && temp_project['texteditor']) {
                    comm = 'call ' + programlist[exist]['path'] + ' "' + proj_file + '"\n';
                } else {
                    comm = 'call ' + programlist[exist]['path'] + '\n';
				}

				comm = programlist[exist]['additional'] + ' ' + comm;
				commands += comm;

            }
        }
    }

    if(commands.length > 0) {
        addtofile(commands);
        
        if(close_explorer == "y") {
            spawn('restart_explorer.bat', []);
        }
    
    }

    return true;
}

function startclient() {
    spawn('chrome', [tabspath]);
}

function start() {

    var url_list = []

    // Port where we'll run the websocket server
    var webSocketsServerPort = 8080;

    /**
     * HTTP server
     */
    var server = http.createServer(function(request, response) {});
    server.listen(webSocketsServerPort, function() {});
    console.log('listening to connection...');

    /**
     * WebSocket server
     */
    var wsServer = new webSocketServer({
        // WebSocket server is tied to a HTTP server. WebSocket
        // request is just an enhanced HTTP request.
        httpServer: server
    });

    // This callback function is called every time someone
    // tries to connect to the WebSocket server
    wsServer.on('request', function(request) {
        var connection = request.accept(null, request.origin); 

        console.log((new Date()) + ' Connection accepted.');

        // user sent some message
        connection.on('message', function(message) {
            
            if (message.type === 'utf8') { 
                url_list = message.utf8Data.split(',').slice(0, url_list.length - 1);
                var command = 'start "" chrome';
                for(var i = 0; i < url_list.length; i++) {
                    command += ' "' + url_list[i] + '"';
                }
                command += '\nexit\n';
                addtofile(command);
                connection.close();
            }
        });

        // user disconnected
        connection.on('close', function(connection) {
            console.log((new Date()) + " Peer " + connection.remoteAddress + " disconnected.");
            server.close();
        });
    });

    server.on('close', function() {
        destoryprograms();
    });
}

function destoryprograms() {
    console.log(programs);
    spawn('CloseWindows', programs);
    setTimeout(function() {process.exit();}, 1000);
}