import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:typed_data';
import 'main_page.dart';
import 'profile_page.dart';
import 'add_clothes_page.dart';
import 'create_outfit_page.dart';

class SearchClothesPage extends StatefulWidget {
  @override
  _SearchClothesPageState createState() => _SearchClothesPageState();
}

class _SearchClothesPageState extends State<SearchClothesPage> {
  List<Map<String, dynamic>> _clothes = [];
  final TextEditingController _categoryController = TextEditingController();
  final TextEditingController _colorController = TextEditingController();

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
          content: Text('Failed to load clothes', style: TextStyle(color: Colors.white)),
          backgroundColor: Colors.red,
        ));
      }
    }
  }

  Future<void> _searchClothes() async {
    String category = _categoryController.text.trim();
    String color = _colorController.text.trim();

    final response = await http.get(
      Uri.parse('http://hollywood.kro.kr/search_clothes?category=$category&color=$color'), // 서버 주소를 적절히 변경
    );

    if (response.statusCode == 200) {
      final List<dynamic> clothesData = jsonDecode(response.body);
      setState(() {
        _clothes = clothesData.map((clothing) => Map<String, dynamic>.from(clothing)).toList();
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('Failed to load clothes', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.red,
      ));
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
              Text(clothing['Category'] ?? '', style: TextStyle(color: Colors.black)),
              Text(clothing['Color'] ?? '', style: TextStyle(color: Colors.black)),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('옷 검색 페이지', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.blue,
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
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _categoryController,
              decoration: InputDecoration(
                labelText: 'Category',
                border: OutlineInputBorder(),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _colorController,
              decoration: InputDecoration(
                labelText: 'Color',
                border: OutlineInputBorder(),
              ),
            ),
          ),
          ElevatedButton(
            onPressed: _searchClothes,
            child: Text('Search', style: TextStyle(color: Colors.white)),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue,
            ),
          ),
          Expanded(
            child: _clothes.isNotEmpty
                ? _buildClothesGrid()
                : Center(child: CircularProgressIndicator()),
          ),
        ],
      ),
    );
  }
}
