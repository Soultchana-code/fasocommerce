import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = "http://10.0.2.2:8000/api/v1";

  static String? _token;
  static void setToken(String token) => _token = token;

  static Future<Map<String, dynamic>?> login(String identifier, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/users/login/'),
        headers: { "Content-Type": "application/json" },
        body: json.encode({ 
          "email_or_phone": identifier, 
          "password": password 
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _token = data['access'];
        return data;
      }
      return null;
    } catch (e) {
      print("LOGIN ERROR: $e");
      return null;
    }
  }

  // RÉCUPÉRER LES COMMANDES
  static Future<List<dynamic>> fetchOrders() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/orders/'),
        headers: { "Authorization": "Bearer $_token" },
      );
      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return data['results'] ?? data;
      }
    } catch (e) { print(e); }
    return [];
  }

  // CRÉER UNE COMMANDE
  static Future<Map<String, dynamic>?> createOrder(Map<String, dynamic> orderData) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/orders/'),
        headers: { 
          "Content-Type": "application/json",
          "Authorization": "Bearer $_token" 
        },
        body: json.encode(orderData),
      );
      if (response.statusCode == 201) return json.decode(response.body);
    } catch (e) { print(e); }
    return null;
  }

  // INITIER LE PAIEMENT (ORANGE/MOOV)
  static Future<bool> initiateMobilePayment(int orderId, String method, String phone) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/payments/initiate/'),
        headers: { 
          "Content-Type": "application/json",
          "Authorization": "Bearer $_token" 
        },
        body: json.encode({
          "order_id": orderId,
          "provider": method,
          "phone_number": phone
        }),
      );
      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) { print(e); }
    return false;
  }

  static Future<List<dynamic>> fetchProducts() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/products/'));

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        if (data is Map && data.containsKey('results')) {
          return data['results'];
        }
        return data as List<dynamic>;
      } else {
        throw Exception("Erreur lors du chargement des produits (${response.statusCode})");
      }
    } catch (e) {
      print("API ERROR: $e");
      return [];
    }
  }

  // --- ACHATS GROUPÉS ---

  static Future<List<dynamic>> getGroupBuySessions(int productId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/orders/group-buy/?product=$productId&status=open'),
        headers: _token != null ? { "Authorization": "Bearer $_token" } : {},
      );
      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return data['results'] ?? data;
      }
    } catch (e) { print("Error sessions: $e"); }
    return [];
  }

  static Future<Map<String, dynamic>?> joinGroupBuySession(int sessionId, int quantity) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/orders/group-buy/$sessionId/join/'),
        headers: { 
          "Content-Type": "application/json",
          "Authorization": "Bearer $_token" 
        },
        body: json.encode({"quantity": quantity}),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return json.decode(utf8.decode(response.bodyBytes));
      } else {
        throw Exception(json.decode(utf8.decode(response.bodyBytes))['error'] ?? 'Erreur inconnue');
      }
    } catch (e) { rethrow; }
  }

  static Future<Map<String, dynamic>?> createGroupBuySession(Map<String, dynamic> data) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/orders/group-buy/'),
        headers: { 
          "Content-Type": "application/json",
          "Authorization": "Bearer $_token" 
        },
        body: json.encode(data),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return json.decode(utf8.decode(response.bodyBytes));
      } else {
        throw Exception(json.decode(utf8.decode(response.bodyBytes))['error'] ?? 'Erreur inconnue');
      }
    } catch (e) { rethrow; }
  }
}

