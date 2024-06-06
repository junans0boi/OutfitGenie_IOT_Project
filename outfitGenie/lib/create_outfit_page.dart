import 'package:flutter/material.dart';
import 'main_page.dart';
import 'profile_page.dart';
import 'add_clothes_page.dart';
import 'search_clothes_page.dart';

class CreateOutfitPage extends StatefulWidget {
  @override
  _CreateOutfitPageState createState() => _CreateOutfitPageState();
}

class _CreateOutfitPageState extends State<CreateOutfitPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('옷 세트 만들기 페이지', style: TextStyle(color: Colors.white)),
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
      body: Center(
        child: Text('옷 세트 만들기 기능은 아직 구현되지 않았습니다.', style: TextStyle(color: Colors.black)),
      ),
    );
  }
}
