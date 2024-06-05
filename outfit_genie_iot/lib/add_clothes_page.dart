import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:permission_handler/permission_handler.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:html' as html; // 웹에서 파일 선택을 위해 추가

class AddClothesPage extends StatefulWidget {
  @override
  _AddClothesPageState createState() => _AddClothesPageState();
}

class _AddClothesPageState extends State<AddClothesPage> {
  List<Uint8List> _images = []; // 웹에서는 Uint8List로 이미지 데이터를 저장
  final _categoryController = TextEditingController();
  final _colorController = TextEditingController();
  final ImagePicker _picker = ImagePicker();
  bool _isImageSelected = false;

  @override
  void initState() {
    super.initState();
    _requestPermissions();
  }

  Future<void> _requestPermissions() async {
    if (!kIsWeb) {
      await Permission.camera.request();
      await Permission.photos.request();
      await Permission.storage.request();
    }
  }

  Future<void> _pickImageFromCamera() async {
    if (kIsWeb) {
      // 웹에서는 카메라 접근 불가능
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('웹에서는 카메라를 사용할 수 없습니다.'),
      ));
      return;
    }

    try {
      final pickedFile = await _picker.pickImage(source: ImageSource.camera);
      if (pickedFile != null) {
        final bytes = await pickedFile.readAsBytes();
        setState(() {
          _images.add(bytes);
          _isImageSelected = true;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Failed to pick image: $e'),
        ));
      }
    }
  }

  Future<void> _pickImageFromGallery() async {
    if (kIsWeb) {
      try {
        html.FileUploadInputElement uploadInput = html.FileUploadInputElement();
        uploadInput.accept = 'image/*';
        uploadInput.click();

        uploadInput.onChange.listen((e) {
          final files = uploadInput.files;
          if (files!.isNotEmpty) {
            final reader = html.FileReader();
            reader.readAsArrayBuffer(files[0]);
            reader.onLoadEnd.listen((e) {
              setState(() {
                _images.add(reader.result as Uint8List);
                _isImageSelected = true;
              });
            });
          }
        });
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Failed to pick images: $e'),
        ));
      }
    } else {
      try {
        final pickedFiles = await _picker.pickMultiImage();
        if (pickedFiles != null && pickedFiles.isNotEmpty) {
          for (var pickedFile in pickedFiles) {
            final bytes = await pickedFile.readAsBytes();
            setState(() {
              _images.add(bytes);
              _isImageSelected = true;
            });
          }
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text('Failed to pick images: $e'),
          ));
        }
      }
    }
  }

  Future<void> _saveImages() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    int? userId = prefs.getInt('user_id');
    if (userId != null) {
      for (var image in _images) {
        final base64Image = base64Encode(image);
        final uri = Uri.parse('http://hollywood.kro.kr/upload_clothes/');
        var request = http.MultipartRequest('POST', uri);
        request.fields['user_id'] = userId.toString();
        request.fields['category'] = _categoryController.text;
        request.fields['color'] = _colorController.text;
        request.files.add(http.MultipartFile.fromBytes('file', image, filename: 'upload.png'));

        final response = await request.send();

        if (response.statusCode != 200) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(
              content: Text('Failed to add some clothes'),
            ));
          }
          return;
        }
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Clothes added successfully'),
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
            if (_images.isNotEmpty)
              Expanded(
                child: GridView.builder(
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 3,
                  ),
                  itemCount: _images.length,
                  itemBuilder: (context, index) {
                    return GestureDetector(
                      onTap: () {
                        if (mounted) {
                          setState(() {
                            _isImageSelected = true;
                          });
                        }
                      },
                      child: Image.memory(_images[index]),
                    );
                  },
                ),
              ),
            if (_isImageSelected)
              Column(
                children: [
                  TextField(
                    controller: _categoryController,
                    decoration: InputDecoration(labelText: 'Category'),
                  ),
                  TextField(
                    controller: _colorController,
                    decoration: InputDecoration(labelText: 'Color'),
                  ),
                ],
              ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: _pickImageFromCamera,
                  child: Text('사진 촬영'),
                ),
                ElevatedButton(
                  onPressed: _pickImageFromGallery,
                  child: Text('사진 선택'),
                ),
              ],
            ),
            if (_isImageSelected)
              ElevatedButton(
                onPressed: _saveImages,
                child: Text('업로드'),
              ),
          ],
        ),
      ),
    );
  }
}
