import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:io';
import 'dart:convert';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  runApp(const SmartInsectApp());
}

class SmartInsectApp extends StatelessWidget {
  const SmartInsectApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Insect Detector',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF2E7D32)),
        useMaterial3: true,
      ),
      home: const MainShell(),
    );
  }
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});
  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _tab = 0;

  // ── CHANGE THIS TO YOUR PC IP ──────────────────────
  static const String serverBase = "http://10.223.63.111:5000";
  // ──────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _tab, children: [
        DetectPage(serverBase: serverBase),
        HistoryPage(serverBase: serverBase),
        StatsPage(serverBase: serverBase),
      ]),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: (i) => setState(() => _tab = i),
        backgroundColor: Colors.white,
        indicatorColor: const Color(0xFF2E7D32).withOpacity(0.15),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.biotech_outlined),
            selectedIcon: Icon(Icons.biotech, color: Color(0xFF2E7D32)),
            label: 'Detect',
          ),
          NavigationDestination(
            icon: Icon(Icons.history_outlined),
            selectedIcon: Icon(Icons.history, color: Color(0xFF2E7D32)),
            label: 'History',
          ),
          NavigationDestination(
            icon: Icon(Icons.bar_chart_outlined),
            selectedIcon: Icon(Icons.bar_chart, color: Color(0xFF2E7D32)),
            label: 'Statistics',
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────
// DETECT PAGE
// ─────────────────────────────────────────────────────
class DetectPage extends StatefulWidget {
  final String serverBase;
  const DetectPage({super.key, required this.serverBase});
  @override
  State<DetectPage> createState() => _DetectPageState();
}

class _DetectPageState extends State<DetectPage>
    with SingleTickerProviderStateMixin {

  File?   _img;
  bool    _loading = false;
  Map<String, dynamic>? _result;
  String? _error;

  late AnimationController _animCtrl;
  late Animation<double>   _fadeAnim;
  final ImagePicker _picker = ImagePicker();

  String get predictUrl => "${widget.serverBase}/predict";

  String s(String key) {
    if (_result == null) return "";
    final v = _result![key];
    return v == null ? "" : v.toString();
  }

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 600));
    _fadeAnim = CurvedAnimation(
        parent: _animCtrl, curve: Curves.easeInOut);
  }

  @override
  void dispose() { _animCtrl.dispose(); super.dispose(); }

  void _setImg(File f) {
    setState(() { _img = f; _result = null; _error = null; });
    _animCtrl.reset();
  }

  void _reset() {
    setState(() { _img = null; _result = null; _error = null; });
    _animCtrl.reset();
  }

  Future<void> _pickGallery() async {
    final x = await _picker.pickImage(
        source: ImageSource.gallery, imageQuality: 85);
    if (x != null) _setImg(File(x.path));
  }

  Future<void> _pickCamera() async {
    final x = await _picker.pickImage(
        source: ImageSource.camera, imageQuality: 85);
    if (x != null) _setImg(File(x.path));
  }

  Future<void> _analyze() async {
    if (_img == null) return;
    setState(() { _loading = true; _result = null; _error = null; });

    try {
      final req = http.MultipartRequest('POST', Uri.parse(predictUrl));
      req.files.add(await http.MultipartFile.fromPath(
          'image', _img!.path));
      final res  = await req.send().timeout(
          const Duration(seconds: 30));
      final body = await res.stream.bytesToString();

      if (res.statusCode == 200) {
        final decoded = json.decode(body) as Map<String, dynamic>;
        setState(() { _result = decoded; _loading = false; });
        _animCtrl.forward();
        _snackbar(decoded);
      } else {
        setState(() {
          _error = "Server error: ${res.statusCode}";
          _loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = "Cannot connect to server.\n\n"
            "• server.py running on PC?\n"
            "• Same WiFi?\n"
            "• IP correct in main.dart?\n\nError: $e";
        _loading = false;
      });
    }
  }

  void _snackbar(Map<String, dynamic> d) {
    if (!mounted) return;
    final isH  = d['insect_type'] == 'Harmful';
    final name = d['insect_name']?.toString() ?? '';
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      backgroundColor:
          isH ? Colors.red.shade700 : Colors.green.shade700,
      duration: const Duration(seconds: 4),
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12)),
      content: Row(children: [
        Icon(
          isH ? Icons.warning_amber_rounded
              : Icons.check_circle_rounded,
          color: Colors.white,
        ),
        const SizedBox(width: 10),
        Expanded(child: Text(
          isH ? 'ALERT: $name detected! Take action now.'
              : '$name detected — Protect it!',
          style: const TextStyle(
              color: Colors.white, fontWeight: FontWeight.bold),
        )),
      ]),
    ));
  }

  Widget _row(IconData icon, Color col, String label, String val) {
    if (val.trim().isEmpty) return const SizedBox.shrink();
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.75),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: col.withOpacity(0.2)),
      ),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start,
          children: [
        Container(
          padding: const EdgeInsets.all(7),
          decoration: BoxDecoration(
              color: col.withOpacity(0.12),
              borderRadius: BorderRadius.circular(8)),
          child: Icon(icon, color: col, size: 16),
        ),
        const SizedBox(width: 12),
        Expanded(child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
          Text(label, style: TextStyle(
              fontWeight: FontWeight.bold,
              color: col, fontSize: 12)),
          const SizedBox(height: 3),
          Text(val, style: const TextStyle(
              fontSize: 13, color: Colors.black87, height: 1.5)),
        ])),
      ]),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F8E9),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1B5E20),
        title: const Row(children: [
          Icon(Icons.pest_control, color: Colors.white, size: 22),
          SizedBox(width: 8),
          Text('Smart Insect Detector',
              style: TextStyle(color: Colors.white,
                  fontWeight: FontWeight.bold, fontSize: 18)),
        ]),
      ),
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [

          // Header
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                  colors: [Color(0xFF2E7D32), Color(0xFF66BB6A)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight),
              borderRadius: BorderRadius.circular(20),
              boxShadow: [BoxShadow(
                  color: Colors.green.withOpacity(0.3),
                  blurRadius: 12, offset: const Offset(0, 4))],
            ),
            child: const Row(children: [
              Icon(Icons.eco, color: Colors.white, size: 44),
              SizedBox(width: 14),
              Expanded(child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                Text('Crop Protection System',
                    style: TextStyle(color: Colors.white,
                        fontSize: 16, fontWeight: FontWeight.bold)),
                SizedBox(height: 4),
                Text('AI-powered insect detection\nfor smart farming',
                    style: TextStyle(color: Colors.white70,
                        fontSize: 12, height: 1.4)),
              ])),
            ]),
          ),

          const SizedBox(height: 16),

          // Image card
          Container(
            height: 250,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [BoxShadow(
                  color: Colors.black.withOpacity(0.08),
                  blurRadius: 12, offset: const Offset(0, 4))],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(20),
              child: _img != null
                  ? Stack(fit: StackFit.expand, children: [
                      Image.file(_img!, fit: BoxFit.cover),
                      Positioned(top: 10, right: 10,
                          child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 5),
                        decoration: BoxDecoration(
                            color: Colors.black54,
                            borderRadius: BorderRadius.circular(20)),
                        child: const Text('Ready to Analyze',
                            style: TextStyle(
                                color: Colors.white, fontSize: 11)),
                      )),
                    ])
                  : Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                    Container(
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                          color: Colors.green.shade50,
                          shape: BoxShape.circle),
                      child: Icon(
                          Icons.add_photo_alternate_outlined,
                          size: 50,
                          color: Colors.green.shade400),
                    ),
                    const SizedBox(height: 14),
                    const Text('No image selected',
                        style: TextStyle(fontSize: 15,
                            color: Colors.grey,
                            fontWeight: FontWeight.w600)),
                    const SizedBox(height: 6),
                    Text('Use Camera or Gallery below',
                        style: TextStyle(fontSize: 12,
                            color: Colors.grey.shade400)),
                  ]),
            ),
          ),

          const SizedBox(height: 16),

          // Buttons
          Row(children: [
            Expanded(child: _buildBtn(
                Icons.camera_alt_rounded, 'Camera',
                const Color(0xFF2E7D32), _pickCamera)),
            const SizedBox(width: 12),
            Expanded(child: _buildBtn(
                Icons.photo_library_rounded, 'Gallery',
                const Color(0xFF1565C0), _pickGallery)),
            if (_img != null) ...[
              const SizedBox(width: 12),
              GestureDetector(
                onTap: _reset,
                child: Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: Colors.red.shade200)),
                  child: Icon(Icons.close_rounded,
                      color: Colors.red.shade400, size: 24),
                ),
              ),
            ],
          ]),

          const SizedBox(height: 16),

          if (_img != null && _result == null && !_loading)
            GestureDetector(
              onTap: _analyze,
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                      colors: [Color(0xFFE65100), Color(0xFFFF7043)]),
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: [BoxShadow(
                      color: Colors.orange.withOpacity(0.4),
                      blurRadius: 10, offset: const Offset(0, 4))],
                ),
                child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                  Icon(Icons.biotech_rounded,
                      color: Colors.white, size: 22),
                  SizedBox(width: 10),
                  Text('ANALYZE INSECT', style: TextStyle(
                      color: Colors.white, fontWeight: FontWeight.bold,
                      fontSize: 16, letterSpacing: 1.2)),
                ]),
              ),
            ),

          if (_loading)
            Container(
              margin: const EdgeInsets.only(top: 8),
              padding: const EdgeInsets.all(28),
              decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [BoxShadow(
                      color: Colors.black.withOpacity(0.06),
                      blurRadius: 12)]),
              child: Column(children: [
                const SizedBox(height: 48, width: 48,
                    child: CircularProgressIndicator(
                        color: Color(0xFF2E7D32), strokeWidth: 3)),
                const SizedBox(height: 18),
                const Text('Identifying insect...', style: TextStyle(
                    fontSize: 16, fontWeight: FontWeight.bold,
                    color: Color(0xFF2E7D32))),
                const SizedBox(height: 5),
                Text('AI is analyzing your image',
                    style: TextStyle(
                        color: Colors.grey.shade500, fontSize: 13)),
              ]),
            ),

          if (_result != null)
            FadeTransition(
                opacity: _fadeAnim, child: _buildResult()),

          if (_error != null)
            Container(
              margin: const EdgeInsets.only(top: 8),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.red.shade200)),
              child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                const Icon(Icons.error_outline_rounded,
                    color: Colors.red, size: 26),
                const SizedBox(width: 12),
                Expanded(child: Text(_error!, style: const TextStyle(
                    fontSize: 13, height: 1.5))),
              ]),
            ),

          const SizedBox(height: 30),
        ]),
      ),
    );
  }

  Widget _buildBtn(IconData icon, String label,
      Color color, VoidCallback fn) =>
      GestureDetector(
        onTap: fn,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 14),
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(14),
            boxShadow: [BoxShadow(
                color: color.withOpacity(0.3),
                blurRadius: 8, offset: const Offset(0, 3))],
          ),
          child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
            Icon(icon, color: Colors.white, size: 20),
            const SizedBox(width: 8),
            Text(label, style: const TextStyle(
                color: Colors.white, fontWeight: FontWeight.bold,
                fontSize: 15)),
          ]),
        ),
      );

  Widget _buildResult() {
    final isH     = s('insect_type') == 'Harmful';
    final color   = isH
        ? const Color(0xFFC62828) : const Color(0xFF2E7D32);
    final bgColor = isH
        ? const Color(0xFFFFF3F3) : const Color(0xFFF1F8E9);
    final gradCol = isH
        ? [const Color(0xFFC62828), const Color(0xFFE53935)]
        : [const Color(0xFF2E7D32), const Color(0xFF43A047)];

    final insectName = s('insect_name');
    final tamilName  = s('tamil_name');
    final top3 = (_result!['top3'] as List?) ?? [];

    return Container(
      margin: const EdgeInsets.only(top: 8),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.25), width: 1.5),
        boxShadow: [BoxShadow(
            color: color.withOpacity(0.15),
            blurRadius: 16, offset: const Offset(0, 6))],
      ),
      child: Column(children: [

        // Gradient header
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: LinearGradient(colors: gradCol),
            borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(20),
                topRight: Radius.circular(20)),
          ),
          child: Row(children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  shape: BoxShape.circle),
              child: Icon(
                isH ? Icons.warning_amber_rounded
                    : Icons.check_circle_rounded,
                color: Colors.white, size: 28,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
              Text(
                isH ? 'HARMFUL INSECT DETECTED'
                    : 'BENEFICIAL INSECT DETECTED',
                style: const TextStyle(color: Colors.white,
                    fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 3),
              Text('Confidence: ${s("confidence")}',
                  style: const TextStyle(
                      color: Colors.white70, fontSize: 13)),
            ])),
          ]),
        ),

        Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [

            // Insect name badge
            if (insectName.isNotEmpty)
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 14, vertical: 9),
                margin: const EdgeInsets.only(bottom: 14),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(30),
                  border: Border.all(color: color.withOpacity(0.3)),
                ),
                child: Row(mainAxisSize: MainAxisSize.min, children: [
                  Icon(Icons.pest_control, color: color, size: 16),
                  const SizedBox(width: 6),
                  Text(
                    tamilName.isNotEmpty
                        ? '$insectName  •  $tamilName'
                        : insectName,
                    style: TextStyle(color: color,
                        fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                ]),
              ),

            // HARMFUL fields
            if (isH) ...[
              _row(Icons.grass,           color, 'Crops Affected',  s('crops_affected')),
              _row(Icons.coronavirus,     color, 'Damage Caused',   s('damage')),
              _row(Icons.science,         color, 'Pesticide',       s('pesticide')),
              _row(Icons.eco,             color, 'Organic Fix',     s('organic')),
              _row(Icons.schedule,        color, 'Best Spray Time', s('best_time')),
              _row(Icons.warning_rounded, color, 'Warning',         s('warning')),
            ],

            // BENEFICIAL fields
            if (!isH) ...[
              _row(Icons.favorite_rounded, color, 'Benefit',      s('benefit')),
              _row(Icons.grass,            color, 'Crops Helped', s('crops_helped')),
              _row(Icons.lightbulb,        color, 'Advice',       s('advice')),
              _row(Icons.star_rounded,     color, 'Fun Fact',     s('fun_fact')),
            ],

            const SizedBox(height: 6),

            // Action message
            if (s('action_message').isNotEmpty)
              Container(
                padding: const EdgeInsets.all(13),
                margin: const EdgeInsets.only(bottom: 14),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: color.withOpacity(0.25)),
                ),
                child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                  Icon(Icons.task_alt_rounded, color: color, size: 20),
                  const SizedBox(width: 10),
                  Expanded(child: Text(s('action_message'),
                      style: TextStyle(color: color,
                          fontWeight: FontWeight.bold,
                          fontSize: 13, height: 1.4))),
                ]),
              ),

            // Top 3 predictions
            if (top3.isNotEmpty) ...[
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text('AI Top 3 Predictions:',
                    style: TextStyle(
                        color: color,
                        fontWeight: FontWeight.bold,
                        fontSize: 13)),
              ),
              ...top3.map((item) {
                final pct = double.tryParse(
                    (item['confidence'] as String)
                        .replaceAll('%','')) ?? 0;
                return Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  padding: const EdgeInsets.symmetric(
                      horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                        color: color.withOpacity(0.2)),
                  ),
                  child: Row(children: [
                    Icon(Icons.pest_control_outlined,
                        color: color, size: 14),
                    const SizedBox(width: 8),
                    Expanded(child: Text(
                        item['insect']?.toString() ?? '',
                        style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w500))),
                    Text(item['confidence']?.toString() ?? '',
                        style: TextStyle(
                            color: color,
                            fontWeight: FontWeight.bold,
                            fontSize: 12)),
                    const SizedBox(width: 8),
                    SizedBox(
                      width: 60,
                      height: 8,
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: pct / 100,
                          backgroundColor:
                              color.withOpacity(0.15),
                          valueColor:
                              AlwaysStoppedAnimation<Color>(
                                  color),
                        ),
                      ),
                    ),
                  ]),
                );
              }),
              const SizedBox(height: 8),
            ],

            // Timestamp
            Row(children: [
              Icon(Icons.access_time_rounded,
                  color: Colors.grey.shade400, size: 13),
              const SizedBox(width: 5),
              Text('Detected at: ${s("timestamp")}',
                  style: TextStyle(
                      color: Colors.grey.shade400, fontSize: 11)),
            ]),

            const SizedBox(height: 14),

            // Analyze again
            GestureDetector(
              onTap: _reset,
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 13),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: color.withOpacity(0.4)),
                ),
                child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                  Icon(Icons.refresh_rounded, color: color, size: 18),
                  const SizedBox(width: 8),
                  Text('Analyze Another Insect',
                      style: TextStyle(color: color,
                          fontWeight: FontWeight.w600, fontSize: 14)),
                ]),
              ),
            ),
          ]),
        ),
      ]),
    );
  }
}

// ─────────────────────────────────────────────────────
// HISTORY PAGE
// ─────────────────────────────────────────────────────
class HistoryPage extends StatefulWidget {
  final String serverBase;
  const HistoryPage({super.key, required this.serverBase});
  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  List<dynamic> _items   = [];
  bool          _loading = true;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final res = await http
          .get(Uri.parse("${widget.serverBase}/history"))
          .timeout(const Duration(seconds: 10));
      if (res.statusCode == 200) {
        setState(() { _items = json.decode(res.body); _loading = false; });
      } else { setState(() => _loading = false); }
    } catch (_) { setState(() => _loading = false); }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F8E9),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1B5E20),
        title: const Row(children: [
          Icon(Icons.history, color: Colors.white, size: 22),
          SizedBox(width: 8),
          Text('Detection History', style: TextStyle(
              color: Colors.white, fontWeight: FontWeight.bold,
              fontSize: 18)),
        ]),
        actions: [IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _load)],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(
              color: Color(0xFF2E7D32)))
          : _items.isEmpty
              ? Center(child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.history, size: 64,
                        color: Colors.grey.shade300),
                    const SizedBox(height: 16),
                    Text('No detections yet', style: TextStyle(
                        fontSize: 16, color: Colors.grey.shade500)),
                  ]))
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _items.length,
                    itemBuilder: (ctx, i) {
                      final item  = _items[i] as Map;
                      final isH   = item['insect_type'] == 'Harmful';
                      final color = isH
                          ? Colors.red.shade700
                          : Colors.green.shade700;
                      final bgCol = isH
                          ? Colors.red.shade50
                          : Colors.green.shade50;
                      final name  = item['insect_name']
                              ?.toString() ?? '';

                      return Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: bgCol,
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(
                              color: color.withOpacity(0.3)),
                          boxShadow: [BoxShadow(
                              color: Colors.black.withOpacity(0.04),
                              blurRadius: 6,
                              offset: const Offset(0, 2))],
                        ),
                        child: Row(children: [
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                                color: color.withOpacity(0.1),
                                shape: BoxShape.circle),
                            child: Icon(
                              isH ? Icons.warning_amber_rounded
                                  : Icons.check_circle_rounded,
                              color: color, size: 22,
                            ),
                          ),
                          const SizedBox(width: 14),
                          Expanded(child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                            Text(
                              name.isNotEmpty ? name
                                  : (isH ? 'Harmful Insect'
                                      : 'Beneficial Insect'),
                              style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: color, fontSize: 14),
                            ),
                            const SizedBox(height: 3),
                            Text(
                              isH ? 'Apply pesticide immediately'
                                  : 'No action needed',
                              style: const TextStyle(
                                  fontSize: 12,
                                  color: Colors.black54),
                            ),
                            const SizedBox(height: 4),
                            Row(children: [
                              Icon(Icons.access_time_rounded,
                                  size: 11,
                                  color: Colors.grey.shade400),
                              const SizedBox(width: 4),
                              Text(
                                item['timestamp']?.toString() ?? '',
                                style: TextStyle(fontSize: 11,
                                    color: Colors.grey.shade400),
                              ),
                            ]),
                          ])),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 10, vertical: 5),
                            decoration: BoxDecoration(
                              color: color.withOpacity(0.12),
                              borderRadius:
                                  BorderRadius.circular(20),
                            ),
                            child: Text(
                              item['confidence']?.toString() ?? '',
                              style: TextStyle(color: color,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12),
                            ),
                          ),
                        ]),
                      );
                    },
                  ),
                ),
    );
  }
}

// ─────────────────────────────────────────────────────
// STATISTICS PAGE
// ─────────────────────────────────────────────────────
class StatsPage extends StatefulWidget {
  final String serverBase;
  const StatsPage({super.key, required this.serverBase});
  @override
  State<StatsPage> createState() => _StatsPageState();
}

class _StatsPageState extends State<StatsPage> {
  List<dynamic> _items   = [];
  bool          _loading = true;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final res = await http
          .get(Uri.parse("${widget.serverBase}/history"))
          .timeout(const Duration(seconds: 10));
      if (res.statusCode == 200) {
        setState(() {
          _items   = json.decode(res.body);
          _loading = false;
        });
      } else { setState(() => _loading = false); }
    } catch (_) { setState(() => _loading = false); }
  }

  @override
  Widget build(BuildContext context) {
    final total   = _items.length;
    final harmful = _items.where(
        (x) => x['insect_type'] == 'Harmful').length;
    final benef   = total - harmful;
    final harmPct = total > 0 ? harmful / total : 0.0;
    final benePct = total > 0 ? benef   / total : 0.0;

    // Count per insect name
    final Map<String, int> insectCount = {};
    for (final item in _items) {
      final name = item['insect_name']?.toString() ?? 'Unknown';
      insectCount[name] = (insectCount[name] ?? 0) + 1;
    }
    final sortedInsects = insectCount.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return Scaffold(
      backgroundColor: const Color(0xFFF1F8E9),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1B5E20),
        title: const Row(children: [
          Icon(Icons.bar_chart, color: Colors.white, size: 22),
          SizedBox(width: 8),
          Text('Statistics', style: TextStyle(color: Colors.white,
              fontWeight: FontWeight.bold, fontSize: 18)),
        ]),
        actions: [IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _load)],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(
              color: Color(0xFF2E7D32)))
          : RefreshIndicator(
              onRefresh: _load,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [

                  // Summary cards
                  Row(children: [
                    Expanded(child: _statCard('Total',
                        total.toString(),
                        Icons.analytics_rounded,
                        const Color(0xFF1565C0))),
                    const SizedBox(width: 12),
                    Expanded(child: _statCard('Harmful',
                        harmful.toString(),
                        Icons.warning_amber_rounded,
                        Colors.red.shade700)),
                    const SizedBox(width: 12),
                    Expanded(child: _statCard('Beneficial',
                        benef.toString(),
                        Icons.check_circle_rounded,
                        Colors.green.shade700)),
                  ]),

                  const SizedBox(height: 20),

                  _barCard('Harmful Insects', harmful, total,
                      Colors.red.shade700, harmPct),
                  const SizedBox(height: 12),
                  _barCard('Beneficial Insects', benef, total,
                      Colors.green.shade700, benePct),

                  const SizedBox(height: 20),

                  // Field safety status
                  Container(
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(colors: harmPct > 0.5
                          ? [Colors.red.shade700, Colors.red.shade500]
                          : [Colors.green.shade700,
                             Colors.green.shade500]),
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [BoxShadow(
                          color: (harmPct > 0.5
                              ? Colors.red : Colors.green)
                              .withOpacity(0.3),
                          blurRadius: 12,
                          offset: const Offset(0, 4))],
                    ),
                    child: Row(children: [
                      Icon(
                        harmPct > 0.5
                            ? Icons.dangerous_rounded
                            : Icons.shield_rounded,
                        color: Colors.white, size: 40,
                      ),
                      const SizedBox(width: 14),
                      Expanded(child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                        Text(
                          harmPct > 0.5
                              ? 'Field Alert!'
                              : 'Field is Safe',
                          style: const TextStyle(color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          harmPct > 0.5
                              ? 'More harmful insects detected.\nImmediate action required!'
                              : 'More beneficial insects detected.\nYour crops are protected.',
                          style: const TextStyle(color: Colors.white70,
                              fontSize: 12, height: 1.4),
                        ),
                      ])),
                    ]),
                  ),

                  const SizedBox(height: 20),

                  // Most detected insects
                  if (sortedInsects.isNotEmpty) ...[
                    const Text('Most Detected Insects',
                        style: TextStyle(fontSize: 15,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF2E7D32))),
                    const SizedBox(height: 10),
                    ...sortedInsects.take(5).map((entry) {
                      final maxCount = sortedInsects.first.value;
                      final pct = entry.value / maxCount;
                      final isH = ['Aphid','Whitefly','Caterpillar',
                          'Mealybug','Thrips'].contains(entry.key);
                      final col = isH
                          ? Colors.red.shade700
                          : Colors.green.shade700;

                      return Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                              color: col.withOpacity(0.2)),
                        ),
                        child: Column(
                            crossAxisAlignment:
                                CrossAxisAlignment.start,
                            children: [
                          Row(children: [
                            Icon(
                              isH ? Icons.warning_amber
                                  : Icons.check_circle,
                              color: col, size: 16,
                            ),
                            const SizedBox(width: 8),
                            Expanded(child: Text(entry.key,
                                style: TextStyle(
                                    color: col,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 13))),
                            Text('${entry.value}x',
                                style: TextStyle(
                                    color: col,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 13)),
                          ]),
                          const SizedBox(height: 8),
                          ClipRRect(
                            borderRadius: BorderRadius.circular(4),
                            child: LinearProgressIndicator(
                              value: pct,
                              backgroundColor:
                                  col.withOpacity(0.15),
                              valueColor:
                                  AlwaysStoppedAnimation<Color>(
                                      col),
                              minHeight: 8,
                            ),
                          ),
                        ]),
                      );
                    }),
                  ],

                  const SizedBox(height: 30),
                ]),
              ),
            ),
    );
  }

  Widget _statCard(String label, String value,
      IconData icon, Color color) =>
      Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [BoxShadow(
              color: Colors.black.withOpacity(0.06),
              blurRadius: 8, offset: const Offset(0, 3))],
        ),
        child: Column(children: [
          Icon(icon, color: color, size: 26),
          const SizedBox(height: 8),
          Text(value, style: TextStyle(fontSize: 24,
              fontWeight: FontWeight.bold, color: color)),
          const SizedBox(height: 4),
          Text(label, style: TextStyle(
              fontSize: 11, color: Colors.grey.shade500)),
        ]),
      );

  Widget _barCard(String label, int count, int total,
      Color color, double pct) =>
      Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14),
          boxShadow: [BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8, offset: const Offset(0, 2))],
        ),
        child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
            Text(label, style: TextStyle(
                fontWeight: FontWeight.bold,
                color: color, fontSize: 14)),
            Text('$count / $total', style: TextStyle(
                color: color, fontWeight: FontWeight.bold,
                fontSize: 14)),
          ]),
          const SizedBox(height: 10),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: pct,
              backgroundColor: color.withOpacity(0.15),
              valueColor: AlwaysStoppedAnimation<Color>(color),
              minHeight: 14,
            ),
          ),
          const SizedBox(height: 6),
          Text('${(pct*100).toStringAsFixed(1)}% of detections',
              style: TextStyle(fontSize: 12,
                  color: Colors.grey.shade500)),
        ]),
      );
}