import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/cart_provider.dart';
import '../services/api_service.dart';

class CartScreen extends StatefulWidget {
  const CartScreen({super.key});

  @override
  State<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  String deliveryCity = 'Ouagadougou';
  final TextEditingController districtController = TextEditingController();
  final TextEditingController landmarkController = TextEditingController();
  final TextEditingController phoneController = TextEditingController();
  
  String paymentMethod = 'orange_money';
  bool isSubmitting = false;
  
  double distance = 0.0;
  double shippingFee = 0.0;

  void _getMockLocation() {
    setState(() {
      distance = 12.5; // distance simulée
      shippingFee = 1500.0; // 750 FCFA par 10 km arrondi
    });
    _showToast("Position récupérée ! Distance simulée : $distance km", isError: false);
  }

  void _showToast(String message, {bool isError = false}) {
    showDialog(
      context: context,
      barrierColor: Colors.black87,
      builder: (_) => Dialog(
        backgroundColor: const Color(0xFF151515),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        child: Padding(
          padding: const EdgeInsets.all(30.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(isError ? '⚠️' : (message.contains('Position') ? '📍' : '🚚'), style: const TextStyle(fontSize: 40)),
              const SizedBox(height: 15),
              Text(isError ? 'Erreur' : 'Information', style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 10),
              Text(message, style: const TextStyle(color: Colors.white70, fontSize: 14), textAlign: TextAlign.center),
            ],
          ),
        ),
      ),
    );
    Future.delayed(const Duration(seconds: 3), () {
      if (Navigator.of(context).canPop()) Navigator.of(context).pop();
    });
  }

  @override
  Widget build(BuildContext context) {
    final cart = Provider.of<CartProvider>(context);
    final totalAmount = cart.totalAmount + shippingFee;

    return Scaffold(
      appBar: AppBar(title: const Text('Ma Commande', style: TextStyle(fontWeight: FontWeight.bold))),
      body: cart.items.isEmpty
          ? const Center(child: Text('Votre panier est vide.', style: TextStyle(color: Colors.white54)))
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // 1. ITEMS
                const Text("📦 Résumé de la commande", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                const SizedBox(height: 10),
                ...cart.items.values.map((item) => Card(
                  color: Colors.white.withValues(alpha: 0.05),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: ListTile(
                    title: Text(item.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text("${item.quantity}x ${item.price} FCFA"),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
                      onPressed: () => cart.removeItem(item.id),
                    ),
                  ),
                )),
                const SizedBox(height: 25),

                // 2. LIVRAISON
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text("📍 Livraison (BF)", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    ElevatedButton.icon(
                      onPressed: _getMockLocation,
                      icon: const Icon(Icons.location_on, size: 16),
                      label: const Text("Ma position"),
                      style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF009E49), foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(horizontal: 10)),
                    )
                  ],
                ),
                const SizedBox(height: 10),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.02), borderRadius: BorderRadius.circular(16)),
                  child: Column(
                    children: [
                      DropdownButtonFormField<String>(
                        value: deliveryCity,
                        decoration: const InputDecoration(labelText: "Ville", filled: true, fillColor: Colors.black12, border: OutlineInputBorder()),
                        items: ['Ouagadougou', 'Bobo-Dioulasso', 'Koudougou'].map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                        onChanged: (val) => setState(() => deliveryCity = val!),
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: districtController,
                        decoration: const InputDecoration(labelText: "Quartier (ex: Patte d'Oie)", filled: true, fillColor: Colors.black12, border: OutlineInputBorder()),
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: landmarkController,
                        decoration: const InputDecoration(labelText: "Repère (Très important !)", filled: true, fillColor: Colors.black12, border: OutlineInputBorder()),
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: phoneController,
                        keyboardType: TextInputType.phone,
                        decoration: const InputDecoration(labelText: "Téléphone pour le livreur", filled: true, fillColor: Colors.black12, border: OutlineInputBorder()),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 25),

                // 3. PAIEMENT
                const Text("💳 Mode de Paiement", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                const SizedBox(height: 10),
                Row(
                  children: [
                    _buildPaymentMethodCard('orange_money', 'Orange', Colors.orange),
                    const SizedBox(width: 8),
                    _buildPaymentMethodCard('moov_money', 'Moov', Colors.blue),
                    const SizedBox(width: 8),
                    _buildPaymentMethodCard('cod', 'Sur\nPlace', Colors.green),
                  ],
                ),
                const SizedBox(height: 25),

                // 4. TOTAL & SUBMIT
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(color: const Color(0xFF111111), borderRadius: BorderRadius.circular(20), border: Border.all(color: const Color(0xFFF26522).withOpacity(0.3))),
                  child: Column(
                    children: [
                      Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [const Text('Total panier'), Text('${cart.totalAmount} FCFA', style: const TextStyle(fontWeight: FontWeight.bold))]),
                      const SizedBox(height: 10),
                      Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                        Text('Frais de livraison (${distance.toStringAsFixed(1)} km)', style: const TextStyle(color: Color(0xFF009E49))), 
                        Text(shippingFee > 0 ? '${shippingFee.toInt()} FCFA' : 'GPS Requis', style: const TextStyle(color: Color(0xFF009E49), fontWeight: FontWeight.bold))
                      ]),
                      const Divider(height: 30, color: Colors.white24),
                      Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                        const Text('Total à Payer', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        Text('${totalAmount.toInt()} FCFA', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFFF26522))),
                      ]),
                      const SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: isSubmitting ? null : () => _submitOrder(cart, totalAmount),
                        style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFF26522), minimumSize: const Size(double.infinity, 56), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16))),
                        child: isSubmitting 
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Text('CONFIRMER LA COMMANDE', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Colors.white)),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 40),
              ],
            ),
    );
  }

  Widget _buildPaymentMethodCard(String key, String label, Color color) {
    bool isSelected = paymentMethod == key;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => paymentMethod = key),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: isSelected ? color.withOpacity(0.1) : Colors.white.withValues(alpha: 0.05),
            border: Border.all(color: isSelected ? color : Colors.white10, width: isSelected ? 2 : 1),
            borderRadius: BorderRadius.circular(12)
          ),
          child: Column(
            children: [
              Icon(key == 'cod' ? Icons.money : Icons.phone_android, color: isSelected ? color : Colors.white54, size: 28),
              const SizedBox(height: 8),
              Text(label, style: TextStyle(color: isSelected ? color : Colors.white54, fontWeight: isSelected ? FontWeight.bold : FontWeight.normal, fontSize: 12), textAlign: TextAlign.center),
            ],
          ),
        ),
      ),
    );
  }

  void _submitOrder(CartProvider cart, double totalAmount) async {
    if (districtController.text.isEmpty || landmarkController.text.isEmpty || phoneController.text.isEmpty) {
      _showToast("Veuillez remplir tous les champs de livraison", isError: true);
      return;
    }
    setState(() => isSubmitting = true);
    try {
      final orderData = {
        "order_type": "individual",
        "delivery_city": deliveryCity,
        "delivery_district": districtController.text,
        "delivery_landmark": landmarkController.text,
        "delivery_phone": phoneController.text,
        "total_amount": totalAmount,
        "items": cart.items.values.map((i) => { "product": i.id, "quantity": i.quantity }).toList()
      };
      
      final order = await ApiService.createOrder(orderData);
      if (order != null) {
        if (paymentMethod == 'cod') {
          cart.clear();
          _showToast("Commande #${order['reference']} validée. Paiement à la livraison prévu.");
          Future.delayed(const Duration(seconds: 3), () => Navigator.pop(context));
        } else {
          final success = await ApiService.initiateMobilePayment(order['id'], paymentMethod, phoneController.text);
          if (success) {
            cart.clear();
            _showToast("Commande #${order['reference']} validée. Confirmez sur votre téléphone.");
            Future.delayed(const Duration(seconds: 3), () => Navigator.pop(context));
          } else {
            cart.clear();
            _showToast("Commande ${order['reference']} créée, mais paiement échoué.", isError: true);
            Future.delayed(const Duration(seconds: 3), () => Navigator.pop(context));
          }
        }
      } else {
        _showToast("Erreur création commande", isError: true);
      }
    } catch (e) {
      _showToast("Veuillez vérifier votre connexion", isError: true);
    } finally {
      if (mounted) setState(() => isSubmitting = false);
    }
  }
}

