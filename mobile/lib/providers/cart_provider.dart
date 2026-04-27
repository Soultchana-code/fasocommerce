import 'package:flutter/material.dart';

class CartItem {
  final int id;
  final String name;
  final double price;
  int quantity;

  CartItem({required this.id, required this.name, required this.price, this.quantity = 1});
}

class CartProvider with ChangeNotifier {
  final Map<int, CartItem> _items = {};

  Map<int, CartItem> get items => _items;

  int get itemCount => _items.length;

  double get totalAmount {
    double total = 0.0;
    _items.forEach((key, item) {
      total += item.price * item.quantity;
    });
    return total;
  }

  void addItem(int id, String name, double price) {
    if (_items.containsKey(id)) {
      _items.update(id, (existing) => CartItem(
        id: existing.id, 
        name: existing.name, 
        price: existing.price, 
        quantity: existing.quantity + 1
      ));
    } else {
      _items.putIfAbsent(id, () => CartItem(id: id, name: name, price: price));
    }
    notifyListeners();
  }

  void removeItem(int id) {
    _items.remove(id);
    notifyListeners();
  }

  void clear() {
    _items.clear();
    notifyListeners();
  }
}
