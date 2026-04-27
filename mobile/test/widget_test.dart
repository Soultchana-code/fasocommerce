import 'package:flutter_test/flutter_test.dart';
import 'package:fasocommerce_mobile/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const FasoCommerceApp());

    // Verify that the login text is present
    expect(find.text('fasocommerce'), findsOneWidget);
  });
}
