import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'logo_page.dart';
import 'login_page.dart';
import 'main_page.dart';
import 'signup_page.dart'; // 회원가입 페이지 import

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OutfitGenie',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: LogoPage(),
    );
  }
}
