import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'add_clothes_page_stub.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:geolocator/geolocator.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'logo_page.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await _requestPermissions();
  runApp(MyApp());
}

Future<void> _requestPermissions() async {
  try {
    if (!kIsWeb) {
      var status = await Permission.locationWhenInUse.status;
      if (!status.isGranted) {
        status = await Permission.locationWhenInUse.request();
      }

      if (status.isGranted) {
        await _getCurrentLocationAndSave();
      } else {
        print("위치 권한이 부여되지 않음");
      }
    }
  } catch (e) {
    print("권한 요청 중 오류 발생: $e");
  }
}

Future<void> _getCurrentLocationAndSave() async {
  if (kIsWeb) return; // 웹에서는 위치 정보를 사용하지 않음
  try {
    Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high);

    await _saveLocation(position.latitude, position.longitude);
  } catch (e) {
    print("위치를 가져오는 중 오류가 발생했습니다 : $e");
  }
}

Future<void> _saveLocation(double latitude, double longitude) async {
  try {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    String? username = prefs.getString('username');
    int? userId = prefs.getInt('user_id');

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
        print('위치를 업데이트하지 못했습니다.');
      }
    }
  } catch (e) {
    print("오류 저장 위치: $e");
  }
}

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
