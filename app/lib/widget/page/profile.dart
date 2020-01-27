/**
* File name: profile.dart
* Author: Daniel Castro
* Date created: 11/28/2019
* Date last modified: 12/2/2019
* Email: danielrcastro10@gmail.com
* Flutter Version: 1.9.1
* Dart Version: 2.5.0
*/

import 'dart:io';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter/rendering.dart';
import 'package:random_color/random_color.dart';

class Profile extends StatefulWidget {
  
  int id;
  List<String> scripts;
  Socket socket;

  Profile({int id, List<String> scrtips, Socket socket}) {
    this.scripts = scrtips;
    this.socket = socket;
    this.id = id;
  }

  @override
  _Profile createState() => new _Profile(id, scripts, socket);

}

class _Profile extends State<Profile> with WidgetsBindingObserver {

  int id;
  List<String> scripts;
  Socket socket;

  _Profile(int id, List<String> scripts, Socket socket) {
    this.scripts = scripts;
    this.socket = socket;
    this.id = id;
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    setState(() {
      if(state == AppLifecycleState.inactive || state == AppLifecycleState.paused) {
        Navigator.maybePop(context);
      }
    });
  }

  List<Widget> getButtons() {
    List<Widget> result = new List<Widget>();

    if(scripts == null) {
      result.add(Container(child:Text('nothing here')));
      return result;
    }

    RandomColor randomColor = RandomColor();

    for(int i = 0; i < scripts.length; i++) {
      result.add(Container(
        padding: EdgeInsets.all(5.0),
          child: SizedBox.expand(
            child: OutlineButton(
              child: Text(scripts[i]),
              shape: new RoundedRectangleBorder(borderRadius: new BorderRadius.circular(30.0)),
              borderSide: BorderSide(
                color: randomColor.randomColor(
                  colorBrightness: ColorBrightness.light, 
                  colorSaturation: ColorSaturation.highSaturation
                ),
                width: 2),
              onPressed: () {
                socket.add(utf8.encode('$id:' + scripts[i] + '.bat'));
              },
            ),
          )
        )
      );
    }

    return result;
  }

  Widget build(BuildContext context) {
    return Scaffold( 
      appBar: AppBar(title: Text('Profile #$id'),),
      body: Center(
        child: Container(
          child: GridView.count(
            padding: const EdgeInsets.all(20),
            crossAxisCount: 3,
            children: getButtons(),
          )
        )
      )
    );
  }
}