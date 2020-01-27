/**
* File name: home.dart
* Author: Daniel Castro
* Date created: 11/28/2019
* Date last modified: 12/2/2019
* Email: danielrcastro10@gmail.com
* Flutter Version: 1.9.1
* Dart Version: 2.5.0
*/

import 'dart:io';
import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:fintranslation_mobile/main.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:random_color/random_color.dart';

import 'profile.dart';


class HomePage extends StatefulWidget {

  Socket socket;
  StreamSubscription<Uint8List> stream;
  
  HomePage(Socket socket) {
    this.socket = socket;
    socket.add(utf8.encode(':mobile'));
  }

  @override
  _HomeState createState() => new _HomeState(socket, stream);

}

class _HomeState extends State<HomePage> {

  Socket socket;
  Map<int, List<String>> scripts;
  List<Widget> buttons = List<Widget>();
  StreamSubscription<Uint8List> stream;

  _HomeState(Socket socket, StreamSubscription<Uint8List> stream) {
    this.stream = stream;
    this.scripts = new Map<int, List<String>>();
    this.socket = socket;
    this.buttons.add(Center(child: Text('nothing here...'),));
  }

  @override
  void initState() {
    listen();
    super.initState();
  }

  void listen() {
    print('listening to server...');

    stream = socket.listen((List<int> event) async {
      
      String data = utf8.decode(event);
      if(data == '!disconnect') {
        stream.cancel();
      } else {
        if(data != '\$Empty') {
          data = data.substring(1, data.length - 1);

          Map<int, List<String>> result = Map<int, List<String>>();
          List<String> str = new List<String>();

          List<String> list = data.split(':');

          for(int j = 0; j < list.length; j+=2) {
            String temp = list[j+1].substring(1, list[j+1].length - 2);
            List<String> listScripts = temp.split(', ');
            int desktop = int.parse(list[j]);

            for(int i = 0; i < listScripts.length - 1; i++) {
              str.add(listScripts[i].substring(1, listScripts[i].length - 5));
            }

            result[desktop] = str;
            str = new List<String>();
          }
          
          this.scripts.addAll(result);
          this.scripts.keys.forEach((k) => print(k));
        } else {
          this.scripts = null;
        }

        setState(() {
          buttons = getProfile(this.scripts);
        });
      }
    });
  }

  List<Widget> getProfile(Map<int, List<String>> dict) {
    List<Widget> result = new List<Widget>();

    if(dict == null) {
      result.add(Container(child:Text('nothing here...')));
      return result;
    }
    
    RandomColor randomColor = RandomColor();

    dict.forEach((k, v) {
      result.add(Container(
        padding: EdgeInsets.all(5.0),
          child: SizedBox.expand( 
            child: OutlineButton(
              child: Text('Desktop: $k'),
              shape: new RoundedRectangleBorder(borderRadius: new BorderRadius.circular(30.0)),
              borderSide: BorderSide(
                color: randomColor.randomColor(
                  colorBrightness: ColorBrightness.light, 
                  colorSaturation: ColorSaturation.highSaturation),
                width: 2),
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => Profile(id: k, scrtips: v, socket: socket),
                  ),
                );
              },
            ),
          )
        )
      );
    });

    return result;
  }

  Future<void> _onRefresh() async {
    this.scripts = new Map<int, List<String>>();
    socket.add(utf8.encode(':mobile'));
  }

  Widget build(BuildContext context) {
    return Scaffold( 
      body: Center(
        child: RefreshIndicator(
          onRefresh: _onRefresh,
          child: Container(
            child: GridView.count(
              padding: const EdgeInsets.all(20),
              crossAxisCount: 3,
              children: buttons,
            )
          )
        )
      )
    );
  }
}
