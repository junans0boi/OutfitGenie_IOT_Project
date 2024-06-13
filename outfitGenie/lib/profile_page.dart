import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'login_page.dart';
import 'main_page.dart';
import 'add_clothes_page.dart';
import 'search_clothes_page.dart';
import 'create_outfit_page.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ProfilePage extends StatefulWidget {
  @override
  _ProfilePageState createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  String username = '';
  String email = '';
  String password = '';
  String gender = '';

  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _nicknameController = TextEditingController();

  bool _isEditing = false;

  @override
  void initState() {
    super.initState();
    _loadUserInfo();
    _loadProfile();
  }

  Future<void> _loadUserInfo() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    setState(() {
      username = prefs.getString('username') ?? '';
      email = prefs.getString('email') ?? '';
      password = prefs.getString('password') ?? '';
      gender = prefs.getString('gender') ?? '';
    });
  }

  Future<void> _loadProfile() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    setState(() {
      _usernameController.text = prefs.getString('username') ?? '';
      _nicknameController.text = prefs.getString('nickname') ?? '';
    });
  }

  Future<void> _updateProfile() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    int? userId = prefs.getInt('user_id');

    if (userId == null) {
      print("User ID is null");
      return;
    }

    final response = await http.post(
      Uri.parse('http://hollywood.kro.kr/update_profile'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, dynamic>{
        'UserID': userId,
        'Nickname': _nicknameController.text,
      }),
    );

    if (response.statusCode == 200) {
      prefs.setString('nickname', _nicknameController.text);
      setState(() {
        _isEditing = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('Profile updated successfully', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue,
      ));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('Failed to update profile', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.red,
      ));
    }
  }

  Future<void> _clearUserInfo() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => LoginPage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('프로필 페이지', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue,
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircleAvatar(
              radius: 50,
              backgroundImage: AssetImage('assets/default_profile.png'), // Add a default profile picture
              backgroundColor: Colors.grey[200],
            ),
            SizedBox(height: 20),
            if (!_isEditing) ...[
              ListTile(
                title: Text('이름', style: TextStyle(color: Colors.black)),
                subtitle: Text(username, style: TextStyle(color: Colors.black)),
              ),
              ListTile(
                title: Text('이메일', style: TextStyle(color: Colors.black)),
                subtitle: Text(email, style: TextStyle(color: Colors.black)),
              ),
              ListTile(
                title: Text('비밀번호', style: TextStyle(color: Colors.black)),
                subtitle: Text(password, style: TextStyle(color: Colors.black)),
              ),
              ListTile(
                title: Text('성별', style: TextStyle(color: Colors.black)),
                subtitle: Text(gender, style: TextStyle(color: Colors.black)),
              ),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    _isEditing = true;
                  });
                },
                child: Text('프로필 편집', style: TextStyle(color: Colors.white)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                ),
              ),
            ] else ...[
              TextField(
                controller: _usernameController,
                decoration: InputDecoration(labelText: 'Username'),
                readOnly: true,
              ),
              TextField(
                controller: _nicknameController,
                decoration: InputDecoration(labelText: 'Nickname'),
              ),
              ElevatedButton(
                onPressed: _updateProfile,
                child: Text('적용', style: TextStyle(color: Colors.white)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                ),
              ),
            ],
            ElevatedButton(
              onPressed: _clearUserInfo,
              child: Text('로그아웃', style: TextStyle(color: Colors.white)),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        items: [
          BottomNavigationBarItem(
            icon: Icon(Icons.home, color: Colors.blue),
            label: '메인 페이지',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.search, color: Colors.blue),
            label: '옷 검색',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.add_a_photo, color: Colors.blue),
            label: '옷 추가',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.create, color: Colors.blue),
            label: '옷 세트 만들기',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person, color: Colors.blue),
            label: '프로필',
          ),
        ],
        onTap: (index) {
          if (index == 0) {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => MainPage()),
            );
          } else if (index == 1) {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => SearchClothesPage()),
            );
          } else if (index == 2) {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => AddClothesPage()),
            );
          } else if (index == 3) {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => CreateOutfitPage()),
            );
          } else if (index == 4) {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => ProfilePage()),
            );
          }
        },
      ),
    );
  }
}
