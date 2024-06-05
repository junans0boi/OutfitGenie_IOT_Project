import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:typed_data';

class SearchClothesPage extends StatefulWidget {
  @override
  _SearchClothesPageState createState() => _SearchClothesPageState();
}

class _SearchClothesPageState extends State<SearchClothesPage> {
  List<Map<String, dynamic>> _clothes = [];
  final _categoryController = TextEditingController();
  final _colorController = TextEditingController();

  Future<void> _searchClothes() async {
    final response = await http.get(
      Uri.parse('http://hollywood.kro.kr/search_clothes?category=${_categoryController.text}&color=${_colorController.text}'), // 서버 주소를 적절히 변경
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
      appBar: AppBar(title: Text('Search Clothes')),
      body: Column(
        children: [
          TextField(
            controller: _categoryController,
            decoration: InputDecoration(labelText: 'Category'),
          ),
          TextField(
            controller: _colorController,
            decoration: InputDecoration(labelText: 'Color'),
          ),
          ElevatedButton(
            onPressed: _searchClothes,
            child: Text('Search'),
          ),
          Expanded(
            child: _clothes.isNotEmpty
                ? _buildClothesGrid()
                : Center(child: Text('No clothes found')),
          ),
        ],
      ),
    );
  }
}
