import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:typed_data';

class ViewClothesPage extends StatefulWidget {
  @override
  _ViewClothesPageState createState() => _ViewClothesPageState();
}

class _ViewClothesPageState extends State<ViewClothesPage> {
  List<Map<String, dynamic>> _clothes = [];

  @override
  void initState() {
    super.initState();
    _loadClothes();
  }

  Future<void> _loadClothes() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    String? username = prefs.getString('username');
    if (username != null) {
      final response = await http.get(
        Uri.parse('http://hollywood.kro.kr/clothes/$username'), // 서버 주소를 적절히 변경
      );

      if (response.statusCode == 200) {
        final List<dynamic> clothesData = jsonDecode(response.body);
        setState(() {
          _clothes = clothesData.map((clothing) => Map<String, dynamic>.from(clothing)).toList();
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Failed to load clothes'),
        ));
      }
    }
  }

  Widget _buildClothesGrid() {
    return GridView.builder(
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
      ),
      itemCount: _clothes.length,
      itemBuilder: (context, index) {
        final clothing = _clothes[index];
        final imageData = base64Decode(clothing['ImageData']);
        return Card(
          child: Column(
            children: [
              Image.memory(Uint8List.fromList(imageData)),
              Text(clothing['Category'] ?? ''),
              Text(clothing['Color'] ?? ''),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('View Clothes')),
      body: _clothes.isNotEmpty
          ? _buildClothesGrid()
          : Center(child: CircularProgressIndicator()),
    );
  }
}
