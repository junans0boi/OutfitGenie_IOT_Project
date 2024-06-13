import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'main_page.dart';
import 'profile_page.dart';
import 'search_clothes_page.dart';
import 'create_outfit_page.dart';

class AddClothesPage extends StatefulWidget {
  @override
  _AddClothesPageState createState() => _AddClothesPageState();
}

class _AddClothesPageState extends State<AddClothesPage> {
  List<File> _images = [];
  final picker = ImagePicker();

  Future pickImagesFromGallery() async {
    final pickedFiles = await picker.pickMultiImage();

    setState(() {
      if (pickedFiles != null) {
        _images = pickedFiles.map((file) => File(file.path)).toList();
      } else {
        print('No image selected.');
      }
    });
  }

  Future<void> _uploadImages() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    int? userId = prefs.getInt('user_id');

    if (userId == null) {
      print("User ID is null");
      return;
    }

    for (File image in _images) {
      String base64Image = base64Encode(await image.readAsBytes());
      final response = await http.post(
        Uri.parse('http://hollywood.kro.kr/upload_clothes/'),
        headers: <String, String>{
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: {
          'user_id': userId.toString(),
          'image_data': base64Image,
          'category': 'default', // Replace 'default' with actual category input from user if available
          'color': 'default', // Replace 'default' with actual color input from user if available
        },
      );

      if (response.statusCode == 200) {
        print('Image uploaded successfully.');
      } else {
        print('Failed to upload image: ${response.body}');
      }
    }

    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text('Images uploaded successfully', style: TextStyle(color: Colors.white)),
      backgroundColor: Colors.blue,
    ));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Add Clothes', style: TextStyle(color: Colors.white)),
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
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            _images.isEmpty
                ? Text('No image selected.', style: TextStyle(color: Colors.black))
                : Wrap(
              children: _images.map((image) {
                return Image.file(image, width: 100, height: 100);
              }).toList(),
            ),
            ElevatedButton(
              onPressed: pickImagesFromGallery,
              child: Text('Select Images from Gallery', style: TextStyle(color: Colors.white)),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
              ),
            ),
            _images.isNotEmpty
                ? ElevatedButton(
              onPressed: _uploadImages,
              child: Text('Upload', style: TextStyle(color: Colors.white)),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
              ),
            )
                : Container(),
          ],
        ),
      ),
    );
  }
}
