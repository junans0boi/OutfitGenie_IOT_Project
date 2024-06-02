import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

class AddClothesPage extends StatefulWidget {
  @override
  _AddClothesPageState createState() => _AddClothesPageState();
}

class _AddClothesPageState extends State<AddClothesPage> {
  File? _image;
  final _categoryController = TextEditingController();
  final _colorController = TextEditingController();

  Future<void> _pickImage() async {
    final pickedFile = await ImagePicker().getImage(source: ImageSource.camera);

    if (pickedFile != null) {
      final directory = await getApplicationDocumentsDirectory();
      final imagePath = '${directory.path}/${DateTime.now().millisecondsSinceEpoch}.png';
      final imageFile = await File(pickedFile.path).copy(imagePath);

      setState(() {
        _image = imageFile;
      });
    }
  }

  Future<void> _saveImage(File image) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    String? username = prefs.getString('username');
    int? userId = prefs.getInt('user_id');
    if (username != null && userId != null) {
      final response = await http.post(
        Uri.parse('http://hollywood.kro.kr/users/$userId/clothes/'),
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8',
        },
        body: jsonEncode(<String, String>{
          'username': username,
          'imagePath': image.path,
          'category': _categoryController.text,
          'color': _colorController.text,
        }),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Clothes added successfully'),
        ));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Failed to add clothes'),
        ));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Add Clothes')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _image != null ? Image.file(_image!) : Text('No image selected.'),
            TextField(
              controller: _categoryController,
              decoration: InputDecoration(labelText: 'Category'),
            ),
            TextField(
              controller: _colorController,
              decoration: InputDecoration(labelText: 'Color'),
            ),
            ElevatedButton(
              onPressed: _pickImage,
              child: Text('Capture Clothes'),
            ),
            ElevatedButton(
              onPressed: () {
                if (_image != null) {
                  _saveImage(_image!);
                }
              },
              child: Text('Add Clothes'),
            ),
          ],
        ),
      ),
    );
  }
}
