/**
* File name: main.dart
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

import 'widget/page/profile.dart';
import 'widget/page/home.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AutoScript Interface',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(title: 'Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> with WidgetsBindingObserver {
  
  PageController pageController;
  int page = 1;
  bool found = false;
  String ip;

  Socket socket;
  Future<Widget> myFuture;
  HomePage frontpage;

  final TextEditingController _loginController = new TextEditingController();

  @override
  void initState() {
    pageController = new PageController(initialPage: this.page);
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    disconnect();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    setState(() {
      if(state == AppLifecycleState.inactive) {
        disconnect();
      }
      found = false;
    });
  }

  void onFloatingPressed() {
    disconnect();
    found = false;
    setState(() {});
  }

  void disconnect() {
    print("disconnecting...");
    // I won't combind the two if statements yet
    // still working on testing the code in the middle
    if(socket != null && found)
      socket.add(utf8.encode('!disconnect'));
    
    /*if(frontpage.stream != null) {
      frontpage.stream.cancel();
    }*/
    
    if(socket != null && found)
      socket.close();
  }

  void onTap(int index) {
    pageController.animateToPage(
    index, duration: const Duration(milliseconds: 300),
    curve: Curves.ease);
  }

  void onPageChanged(int page) {
    setState(() {
      this.page = page;
    });
  }

  Future<Widget> connect() async {
    try {
      print("######## try ########");
      socket = await Socket.connect(ip, 9000, timeout: Duration(seconds: 7));
      frontpage = new HomePage(socket);
    } catch(exception) {
      print("failed to connect");
      return errorpage();
    }
    print("##### connected #####");
    return homepage();
  }

  Widget homepage() {
    return new Scaffold(
        appBar: AppBar(
          title: Center(
            child: Text("Interface"),
          ),
        ),
        body: PageView(
          children: <Widget>[
            frontpage,
            // TODO: add settings and library pages
            // adding pages crashes frontpage because it start a new 'listen to server' stream 
          ],
          controller: pageController,
          onPageChanged: onPageChanged,
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: onFloatingPressed,
          child: Icon(Icons.close),
        ),
        bottomNavigationBar: BottomNavigationBar(
          currentIndex: this.page,
          onTap: onTap,
          items: [
            new BottomNavigationBarItem(
              icon: new Icon(Icons.settings),
              title: new Text('Settings'),
              backgroundColor: Colors.black54,
            ),
            new BottomNavigationBarItem(
              icon: new Icon(Icons.home),
              title: new Text('Home'),
              backgroundColor: Colors.black54,
            ),
            new BottomNavigationBarItem(
              icon: new Icon(Icons.library_books),
              title: new Text('Libaray'),
              backgroundColor: Colors.black54,
            ),
          ],
        )
    );
  }

  Widget errorpage() {
    return new Scaffold(
        appBar: AppBar(
          title: Center(child: Text("ERROR: couldn't connect")),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () {
            found = false;
            setState(() {});
          },
          child: Icon(Icons.refresh),
        ),
        body: Center(
          child: Text("Could not connect to server with ip: "),
        ),
      );
  }

  Widget loginpage() {
    return MaterialApp(
      theme: ThemeData.dark(),
      home: Scaffold(
        appBar: AppBar(
          title: Center(child: Text("Login")),
        ),
        body: Container (
          margin: EdgeInsets.all(25.0),
          child:Center(
            child: TextFormField(
              controller: _loginController,
              onFieldSubmitted: (String input) {
                ip = input;
                found = true;
                setState(() {
                  myFuture = connect();
                });
              },
              decoration: InputDecoration(labelText: 'Enter ip'),
            )
          ),
        )
      )
    );
  }

  Widget buildpage() {
    return MaterialApp(
      theme: ThemeData.dark(),
      initialRoute: '/',
      routes: {
        '/profile': (context) => Profile(),
      },
      home: FutureBuilder(
        future: myFuture,
        builder: (BuildContext context, AsyncSnapshot<Widget> widget) {
          if(!widget.hasData) {
            print("trying to connect..." + " no data");
            return new Scaffold(
              appBar: AppBar(
                title: Center(
                  child: Text("Connecting..."),
                ),
              ),
              body: Center(child: CircularProgressIndicator()),
            );
          }

          return widget.data;
        },
      )
    );
  }

  Widget login() {
    if(!found) {
      return loginpage();
    } else {
      return buildpage();
    }
  }

  Widget build(BuildContext context) {
    return login();
  }
}
