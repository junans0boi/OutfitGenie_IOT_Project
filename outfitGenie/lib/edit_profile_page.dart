import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class EditProfilePage extends StatefulWidget {
  @override
  _EditProfilePageState createState() => _EditProfilePageState();
}

class _EditProfilePageState extends State<EditProfilePage> {
  final _nicknameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  bool _isEditing = false;

  String _nickname = '';
  String _email = '';
  String _password = '';

  @override
  void initState() {
    super.initState();
    _loadUserInfo();
  }

  Future<void> _loadUserInfo() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    setState(() {
      _nickname = prefs.getString('nickname') ?? 'UserNickname';
      _email = prefs.getString('email') ?? '';
      _password = prefs.getString('password') ?? '';

      _nicknameController.text = _nickname;
      _emailController.text = _email;
      _passwordController.text = _password;
    });
  }

  Future<void> _saveProfile() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    prefs.setString('nickname', _nicknameController.text);
    prefs.setString('email', _emailController.text);
    prefs.setString('password', _passwordController.text);

    int? userId = prefs.getInt('user_id');
    if (userId == null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('User ID not found', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.red,
      ));
      return;
    }

    final response = await http.post(
      Uri.parse('http://hollywood.kro.kr/update_profile'), // 서버 주소를 적절히 변경
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, dynamic>{
        'user_id': userId,
        'nickname': _nicknameController.text,
        'email': _emailController.text,
        'password': _passwordController.text,
      }),
    );

    if (response.statusCode == 200) {
      setState(() {
        _nickname = _nicknameController.text;
        _email = _emailController.text;
        _password = _passwordController.text;
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Profile', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            CircleAvatar(
              radius: 50,
              backgroundImage: AssetImage('assets/default_profile.png'), // Add a default profile picture
              backgroundColor: Colors.grey[200],
            ),
            SizedBox(height: 20),
            if (!_isEditing) ...[
              ListTile(
                title: Text('Nickname', style: TextStyle(color: Colors.black)),
                subtitle: Text(_nickname, style: TextStyle(color: Colors.black)),
              ),
              ListTile(
                title: Text('Email', style: TextStyle(color: Colors.black)),
                subtitle: Text(_email, style: TextStyle(color: Colors.black)),
              ),
              ListTile(
                title: Text('Password', style: TextStyle(color: Colors.black)),
                subtitle: Text(_password, style: TextStyle(color: Colors.black)),
              ),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    _isEditing = true;
                  });
                },
                child: Text('Edit Profile', style: TextStyle(color: Colors.white)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  padding: EdgeInsets.symmetric(horizontal: 50, vertical: 15),
                ),
              ),
            ] else ...[
              TextField(
                controller: _nicknameController,
                decoration: InputDecoration(
                  labelText: 'Nickname',
                  border: OutlineInputBorder(),
                ),
              ),
              SizedBox(height: 20),
              TextField(
                controller: _emailController,
                decoration: InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.emailAddress,
              ),
              SizedBox(height: 20),
              TextField(
                controller: _passwordController,
                decoration: InputDecoration(
                  labelText: 'Password',
                  border: OutlineInputBorder(),
                ),
                obscureText: true,
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: _saveProfile,
                child: Text('Apply', style: TextStyle(color: Colors.white)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  padding: EdgeInsets.symmetric(horizontal: 50, vertical: 15),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
