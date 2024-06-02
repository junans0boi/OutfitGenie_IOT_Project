import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'login_page.dart';

class ProfilePage extends StatelessWidget {
  Future<List<Map<String, dynamic>>> _getClothes() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    int? userId = prefs.getInt('userId');
    if (userId != null) {
      final response = await http.get(
        Uri.parse('http://hollywood.kro.kr/users/$userId/clothes/'),
      );

      if (response.statusCode == 200) {
        List<dynamic> clothes = jsonDecode(response.body);
        return clothes.map((item) => item as Map<String, dynamic>).toList();
      } else {
        throw Exception('Failed to load clothes');
      }
    }
    return [];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Profile')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Nickname: UserNickname'),
            ElevatedButton(
              onPressed: () async {
                List<Map<String, dynamic>> clothes = await _getClothes();
                // 옷 목록 보기
              },
              child: Text('Show Registered Clothes'),
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
              child: Text('Logout'),
            ),
          ],
        ),
      ),
    );
  }
}
