import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'edit_profile_page.dart';
import 'view_clothes_page.dart';
import 'login_page.dart'; // LoginPage import

class ProfilePage extends StatefulWidget {
  @override
  _ProfilePageState createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  String _nickname = '';

  @override
  void initState() {
    super.initState();
    _loadNickname();
  }

  Future<void> _loadNickname() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    setState(() {
      _nickname = prefs.getString('nickname') ?? 'UserNickname';
    });
  }

  void _navigateToEditProfilePage() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => EditProfilePage()),
    );
  }

  void _navigateToViewClothesPage() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => ViewClothesPage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('프로필')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                CircleAvatar(
                  radius: 50,
                  backgroundImage: AssetImage('assets/profile_placeholder.png'), // 프로필 이미지 경로
                ),
                SizedBox(height: 16),
                Text(
                  _nickname,
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 16),
                ElevatedButton(
                  onPressed: _navigateToEditProfilePage,
                  child: Text('프로필 편집'),
                ),
              ],
            ),
          ),
          ElevatedButton(
            onPressed: _navigateToViewClothesPage,
            child: Text('등록된 옷 다시 불러오기'),
          ),
          ElevatedButton(
            onPressed: () async {
              SharedPreferences prefs = await SharedPreferences.getInstance();
              prefs.remove('isLoggedIn');
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => LoginPage()),
              );
            },
            child: Text('로그아웃'),
          ),
        ],
      ),
    );
  }
}