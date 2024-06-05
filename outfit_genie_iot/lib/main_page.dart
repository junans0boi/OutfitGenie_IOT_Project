import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'add_clothes_page_stub.dart';
import 'profile_page.dart';
import 'search_clothes_page.dart';
import 'create_outfit_page.dart';

class MainPage extends StatefulWidget {
  @override
  _MainPageState createState() => _MainPageState();
}

class _MainPageState extends State<MainPage> {
  String _locationMessage = "위치를 사용할 수 없음";

  @override
  void initState() {
    super.initState();
    _getCurrentLocationAndSave();
  }

  Future<void> _getCurrentLocationAndSave() async {
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        setState(() {
          _locationMessage = "위치 서비스가 비활성화되었습니다";
        });
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          setState(() {
            _locationMessage = "위치 권한이 거부되었습니다.";
          });
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        setState(() {
          _locationMessage =
          "위치 권한은 영구적으로 거부되며, 권한을 요청할 수 없습니다.";
        });
        return;
      }

      Position position = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.high);
      setState(() {
        _locationMessage =
        "위도: ${position.latitude}, 경도: ${position.longitude}";
      });

      await _saveLocation(position.latitude, position.longitude);
    } catch (e) {
      print("Error getting location: $e");
    }
  }

  Future<void> _saveLocation(double latitude, double longitude) async {
    try {
      SharedPreferences prefs = await SharedPreferences.getInstance();
      String? username = prefs.getString('username');
      int? userId = prefs.getInt('user_id');
      String location = '위도: $latitude, 경도: $longitude';

      if (username != null && userId != null) {
        final response = await http.post(
          Uri.parse('http://hollywood.kro.kr/update_location'),
          headers: <String, String>{
            'Content-Type': 'application/json; charset=UTF-8',
          },
          body: jsonEncode(<String, dynamic>{
            'UserID': userId,
            'gridX': latitude,
            'gridY': longitude,
          }),
        );

        if (response.statusCode != 200) {
          print('Failed to update location');
        }
      }
    } catch (e) {
      print("Error saving location: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      bottomNavigationBar: BottomNavigationBar(
        items: [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: '메인 페이지',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.search),
            label: '옷 검색',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.add_a_photo),
            label: '옷 추가',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.create),
            label: '옷 세트 만들기',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
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
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              _locationMessage,
              style: TextStyle(fontFamily: 'NotoSans'),
            ),
            ElevatedButton(
              onPressed: _getCurrentLocationAndSave,
              child: Text(
                '위치 정보 가져오기',
                style: TextStyle(fontFamily: 'NotoSans'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
