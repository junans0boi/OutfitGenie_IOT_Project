import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:typed_data';

class CreateOutfitPage extends StatefulWidget {
  @override
  _CreateOutfitPageState createState() => _CreateOutfitPageState();
}

class _CreateOutfitPageState extends State<CreateOutfitPage> {
  List<Map<String, dynamic>> _clothes = [];
  List<Map<String, dynamic>> _selectedClothes = [];

  @override
  void initState() {
    super.initState();
    _loadClothes();
  }

  Future<void> _loadClothes() async {
    final response = await http.get(
      Uri.parse('http://hollywood.kro.kr/clothes'), // 서버 주소를 적절히 변경
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

  void _toggleSelection(Map<String, dynamic> clothing) {
    setState(() {
      if (_selectedClothes.contains(clothing)) {
        _selectedClothes.remove(clothing);
      } else {
        _selectedClothes.add(clothing);
      }
    });
  }

  Future<void> _saveOutfit() async {
    final response = await http.post(
      Uri.parse('http:/hollywood.kro.kr/create_outfit'), // 서버 주소를 적절히 변경
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, dynamic>{
        'outfit': _selectedClothes,
      }),
    );

    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('Outfit created successfully'),
      ));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('Failed to create outfit'),
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
        return GestureDetector(
          onTap: () => _toggleSelection(clothing),
          child: Card(
            child: Column(
              children: [
                Image.memory(Uint8List.fromList(imageData)),
                Text(clothing['Category'] ?? ''),
                Text(clothing['Color'] ?? ''),
                if (_selectedClothes.contains(clothing))
                  Icon(Icons.check_circle, color: Colors.green),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Create Outfit')),
      body: Column(
        children: [
          Expanded(
            child: _clothes.isNotEmpty
                ? _buildClothesGrid()
                : Center(child: CircularProgressIndicator()),
          ),
          ElevatedButton(
            onPressed: _saveOutfit,
            child: Text('Save Outfit'),
          ),
        ],
      ),
    );
  }
}
