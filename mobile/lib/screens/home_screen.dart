import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../providers/cart_provider.dart';
import 'cart_screen.dart';
import 'order_list_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<dynamic> products = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  Future<void> _loadProducts() async {
    final fetched = await ApiService.fetchProducts();
    setState(() {
      products = fetched;
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final cart = Provider.of<CartProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'fasocommerce',
          style: TextStyle(fontWeight: FontWeight.w900, fontSize: 24, letterSpacing: -1),
        ),
        actions: [
          // Bouton Panier avec Badge
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.shopping_bag_outlined), 
                onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => const CartScreen())),
              ),
              if (cart.itemCount > 0)
                Positioned(
                  right: 8,
                  top: 8,
                  child: Container(
                    padding: const EdgeInsets.all(2),
                    decoration: BoxDecoration(color: const Color(0xFFF26522), borderRadius: BorderRadius.circular(10)),
                    constraints: const BoxConstraints(minWidth: 16, minHeight: 16),
                    child: Text('${cart.itemCount}', textAlign: TextAlign.center, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
                  ),
                )
            ],
          ),
          // Bouton Historique des commandes
          IconButton(
            icon: const Icon(Icons.history), 
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => const OrderListScreen())),
          ),
        ],
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              'Prêt pour vos achats groupés ? 🇧🇫',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(
            child: isLoading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFFF26522)))
                : products.isEmpty
                    ? const Center(child: Text("Aucun produit trouvé."))
                    : GridView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          childAspectRatio: 0.7,
                          crossAxisSpacing: 16,
                          mainAxisSpacing: 16,
                        ),
                        itemCount: products.length,
                        itemBuilder: (context, index) {
                          final p = products[index];
                          return _buildProductCard(p, cart);
                        },
                      ),
          ),
        ],
      ),
    );
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
              Text(isError ? '⚠️' : '🚀', style: const TextStyle(fontSize: 40)),
              const SizedBox(height: 15),
              Text(isError ? 'Erreur' : 'Succès', style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
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

  void _showGroupBuyModal(Map<String, dynamic> product) async {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1A1A1A),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      isScrollControlled: true,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (BuildContext context, StateSetter setModalState) {
            bool isLoadingSessions = true;
            List<dynamic> sessions = [];

            void fetchSessions() async {
              final fetched = await ApiService.getGroupBuySessions(product['id']);
              if (mounted) {
                setModalState(() {
                  sessions = fetched;
                  isLoadingSessions = false;
                });
              }
            }

            if (isLoadingSessions) fetchSessions();

            return Padding(
              padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom, left: 24, right: 24, top: 24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          "📦 Achats groupés : ${product['name']}",
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Colors.white),
                        ),
                      ),
                      IconButton(icon: const Icon(Icons.close, color: Colors.white54), onPressed: () => Navigator.pop(context))
                    ],
                  ),
                  const SizedBox(height: 20),
                  if (isLoadingSessions)
                    const Center(child: CircularProgressIndicator(color: Color(0xFFF26522)))
                  else if (sessions.isNotEmpty)
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text("Rejoignez un groupe existant !", style: TextStyle(color: Colors.white54, fontSize: 14)),
                        const SizedBox(height: 15),
                        ...sessions.map((s) => Container(
                          margin: const EdgeInsets.only(bottom: 10),
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          decoration: BoxDecoration(color: const Color(0xFF222222), borderRadius: BorderRadius.circular(12)),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text("De ${s['organizer_name'] ?? 'Client'}", style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                                  Text("${s['current_quantity']} / ${s['target_quantity']} requis", style: const TextStyle(fontSize: 12, color: Color(0xFF009E49))),
                                ],
                              ),
                              ElevatedButton(
                                onPressed: () async {
                                  try {
                                    await ApiService.joinGroupBuySession(s['id'], 1);
                                    Navigator.pop(context);
                                    _showToast("Félicitations ! Vous avez rejoint le groupe d'achat.");
                                  } catch (e) {
                                    Navigator.pop(context);
                                    _showToast(e.toString().replaceAll('Exception: ', ''), isError: true);
                                  }
                                },
                                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF009E49), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))),
                                child: const Text("Rejoindre", style: TextStyle(color: Colors.white)),
                              )
                            ],
                          ),
                        )),
                        const SizedBox(height: 10),
                        SizedBox(
                          width: double.infinity,
                          child: OutlinedButton(
                            onPressed: () => _createSession(product),
                            style: OutlinedButton.styleFrom(side: const BorderSide(color: Color(0xFFF26522)), padding: const EdgeInsets.all(16)),
                            child: const Text("Lancer un autre groupe", style: TextStyle(color: Color(0xFFF26522))),
                          ),
                        )
                      ],
                    )
                  else
                    Column(
                      children: [
                        const Center(child: Text("Aucun groupe ouvert.", style: TextStyle(color: Colors.white54))),
                        const SizedBox(height: 20),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: () => _createSession(product),
                            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFF26522), padding: const EdgeInsets.all(16), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
                            child: const Text("Lancer le premier groupe !", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                          ),
                        )
                      ],
                    ),
                  const SizedBox(height: 30),
                ],
              ),
            );
          },
        );
      },
    );
  }

  void _createSession(Map<String, dynamic> product) async {
    Navigator.pop(context);
    try {
      final newSession = await ApiService.createGroupBuySession({
        "product": product['id'],
        "target_quantity": product['bulk_min_quantity'] ?? 5,
        "unit_price_at_bulk": product['bulk_price'] ?? product['unit_price']
      });
      if (newSession != null && newSession['id'] != null) {
        await ApiService.joinGroupBuySession(newSession['id'], 1);
      }
      _showToast("Nouveau groupe lancé ! Partagez le lien avec vos amis.");
    } catch (e) {
      _showToast("Veuillez vous connecter pour créer un groupe", isError: true);
    }
  }

  Widget _buildProductCard(Map<String, dynamic> product, CartProvider cart) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: ClipRRect(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
              child: Container(
                width: double.infinity,
                color: Colors.white10,
                child: product['image'] != null
                    ? Image.network(product['image'], fit: BoxFit.cover)
                    : const Icon(Icons.image_not_supported, color: Colors.white38),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  product['name'] ?? 'Inconnu',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                ),
                const SizedBox(height: 6),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text("Prix unitaire", style: TextStyle(color: Colors.white54, fontSize: 10)),
                    Text("${product['unit_price']} FCFA", style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11)),
                  ],
                ),
                if (product['bulk_price'] != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 2),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text("Achat Groupé", style: TextStyle(color: Color(0xFF009E49), fontSize: 10)),
                        Text("${product['bulk_price']} FCFA", style: const TextStyle(color: Color(0xFF009E49), fontWeight: FontWeight.bold, fontSize: 11)),
                      ],
                    ),
                  ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () {
                          cart.addItem(product['id'], product['name'], double.parse(product['unit_price'].toString()));
                          _showToast("${product['name']} ajouté au panier !");
                        },
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 8), side: const BorderSide(color: Colors.white24),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))
                        ),
                        child: const Icon(Icons.shopping_cart_checkout, size: 16, color: Colors.white70),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      flex: 2,
                      child: ElevatedButton(
                        onPressed: product['bulk_price'] != null ? () => _showGroupBuyModal(product) : null,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFF26522),
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))
                        ),
                        child: const Text("Grouper", style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                      ),
                    )
                  ],
                )
              ],
            ),
          )
        ],
      ),
    );
  }
}
