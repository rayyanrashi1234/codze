# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

from ui_components import GlassCard, NeonButton, PulseDot
from scanner import FileScanner
from network import NetworkBridge
from config import SERVER_URL

# Import plyer for native Android file picking
try:
    from plyer import filechooser
except ImportError:
    filechooser = None

class AegisApp(App):
    def build(self):
        Window.clearcolor = (0.04, 0.05, 0.07, 1) # Deep dark blue background
        
        self.scanner = FileScanner()
        self.network = NetworkBridge(SERVER_URL)
        
        # Main Root Layout
        root = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        # --- 1. HEADER ---
        header = BoxLayout(size_hint_y=0.08, spacing=dp(10))
        title = Label(text="[b]AEGIS-X[/b] // MOBILE ENDPOINT", markup=True, font_size='20sp', color=(0.4, 0.98, 0.94, 1), halign='left')
        title.bind(size=title.setter('text_size'))
        
        status_box = BoxLayout(orientation='horizontal', size_hint_x=0.3)
        self.status_dot = PulseDot(color_hex="#00FF00")
        status_label = Label(text="SECURE", font_size='14sp', color=(0, 1, 0.5, 1), halign='right')
        status_box.add_widget(self.status_dot)
        status_box.add_widget(status_label)
        
        header.add_widget(title)
        header.add_widget(status_box)
        root.add_widget(header)
        
        # --- 2. STATS CARDS ---
        stats_row = BoxLayout(size_hint_y=0.12, spacing=dp(10))
        self.card_scanned = self._create_stat_card("FILES SCANNED", "0")
        self.card_blocked = self._create_stat_card("THREATS BLOCKED", "0")
        self.card_health = self._create_stat_card("SYSTEM HEALTH", "100%")
        stats_row.add_widget(self.card_scanned)
        stats_row.add_widget(self.card_blocked)
        stats_row.add_widget(self.card_health)
        root.add_widget(stats_row)
        
        # --- 3. ACTION ZONE ---
        action_card = GlassCard(size_hint_y=0.3, orientation='vertical')
        
        # File Select Button
        self.btn_scan_file = NeonButton(text="📂 SELECT & SCAN FILE", color_hex="#66FCF1", size_hint_y=0.4)
        self.btn_scan_file.bind(on_press=self.pick_and_scan_file)
        
        # Paste Input
        self.input_payload = TextInput(
            hint_text="Or paste suspicious code/payload here...",
            background_color=(0.05, 0.06, 0.08, 1),
            foreground_color=(0.8, 0.8, 0.8, 1),
            cursor_color=(0.4, 0.98, 0.94, 1),
            multiline=False,
            font_size='14sp',
            size_hint_y=0.3,
            padding=[dp(10), dp(10)]
        )
        
        # Analyze Paste Button
        self.btn_scan_paste = NeonButton(text="🔍 ANALYZE PASTED PAYLOAD", color_hex="#FF0055", size_hint_y=0.3)
        self.btn_scan_paste.bind(on_press=self.scan_pasted_payload)
        
        action_card.add_widget(self.btn_scan_file)
        action_card.add_widget(self.input_payload)
        action_card.add_widget(self.btn_scan_paste)
        root.add_widget(action_card)
        
        # --- 4. LIVE FEED ---
        feed_card = GlassCard(size_hint_y=0.42, orientation='vertical')
        feed_header = Label(text="[b]LIVE THREAT FEED[/b]", markup=True, font_size='14sp', color=(0.8, 0.8, 0.8, 1), size_hint_y=0.1, halign='left')
        feed_header.bind(size=feed_header.setter('text_size'))
        
        self.feed_scroll = ScrollView(size_hint_y=0.9)
        self.feed_label = Label(
            text="[color=#66FCF1]> System Initialized. Awaiting input...[/color]\n",
            markup=True,
            font_size='12sp',
            halign='left',
            valign='top',
            color=(0.7, 0.7, 0.7, 1)
        )
        self.feed_label.bind(size=self.feed_label.setter('text_size'))
        self.feed_scroll.add_widget(self.feed_label)
        
        feed_card.add_widget(feed_header)
        feed_card.add_widget(self.feed_scroll)
        root.add_widget(feed_card)
        
        # Start polling server for live threats every 5 seconds
        Clock.schedule_interval(self.poll_server_threats, 5.0)
        
        return root

    def _create_stat_card(self, title, value):
        card = GlassCard(orientation='vertical')
        lbl_title = Label(text=title, font_size='10sp', color=(0.6, 0.6, 0.6, 1), size_hint_y=0.4)
        lbl_value = Label(text=value, font_size='24sp', bold=True, color=(0.4, 0.98, 0.94, 1), size_hint_y=0.6)
        card.add_widget(lbl_title)
        card.add_widget(lbl_value)
        return card

    def add_feed_log(self, message, color="#C5C6C7"):
        current = self.feed_label.text
        self.feed_label.text = current + f"[color={color}]> {message}[/color]\n"
        self.feed_scroll.scroll_y = 0 # Auto scroll to bottom

    def pick_and_scan_file(self, instance):
        if not filechooser:
            self.add_feed_log("Error: File picker not available.", "#FF0055")
            return
            
        self.add_feed_log("Opening native file selector...", "#66FCF1")
        import threading
        threading.Thread(target=self._do_pick_file, daemon=True).start()

    def _do_pick_file(self):
        # Opens native Android file picker
        selection = filechooser.open_file(filters=["*.pdf", "*.txt", "*.exe", "*.js", "*.*"])
        if selection:
            file_path = selection[0]
            Clock.schedule_once(lambda dt: self._process_file(file_path), 0)
        else:
            Clock.schedule_once(lambda dt: self.add_feed_log("File selection cancelled.", "#C5C6C7"), 0)

    def _process_file(self, file_path):
        filename = file_path.split('/')[-1]
        self.add_feed_log(f"Scanning: {filename}...", "#66FCF1")
        
        # 1. Local Heuristic Scan
        result = self.scanner.scan_file_local(file_path)
        
        if result['is_malicious']:
            self.add_feed_log(f"⛔ LOCAL ALERT: {result['reason']}", "#FF0055")
            self._update_stats(blocked=True)
            # 2. Send to Server for Deep Analysis & Quarantine
            self.add_feed_log("📡 Syncing payload to Central Forensic Server...", "#FFAA00")
            self.network.send_to_server(file_path, result, self._on_server_sync)
        else:
            self.add_feed_log(f"✅ Local Scan: {result['reason']}", "#00FF88")
            self._update_stats(scanned=True)

    def scan_pasted_payload(self, instance):
        content = self.input_payload.text.strip()
        if not content:
            self.add_feed_log("Error: Payload input is empty.", "#FF0055")
            return
            
        self.add_feed_log("Analyzing pasted payload...", "#66FCF1")
        import tempfile
        import os
        temp_path = os.path.join(tempfile.gettempdir(), "aegis_temp_payload.txt")
        with open(temp_path, 'w') as f:
            f.write(content)
        self._process_file(temp_path)

    def _on_server_sync(self, success, message):
        if success:
            self.add_feed_log(f"✅ Server Sync: {message}", "#00FF88")
        else:
            self.add_feed_log(f"❌ Server Sync Failed: {message}", "#FF0055")

    def _update_stats(self, scanned=False, blocked=False):
        current_scanned = int(self.card_scanned.children[0].text)
        current_blocked = int(self.card_blocked.children[0].text)
        
        if scanned:
            self.card_scanned.children[0].text = str(current_scanned + 1)
        if blocked:
            self.card_blocked.children[0].text = str(current_blocked + 1)
            # Flash health card red briefly to show impact
            self.card_health.children[0].color = (1, 0, 0.3, 1)
            Clock.schedule_once(lambda dt: setattr(self.card_health.children[0], 'color', (0.4, 0.98, 0.94, 1)), 1.5)

    def poll_server_threats(self, dt):
        """Fetches live threats from server to show in feed"""
        self.network.fetch_live_threats(self._update_live_feed)

    def _update_live_feed(self, threats):
        # Placeholder for real-time server feed updates
        pass 

if __name__ == '__main__':
    AegisApp().run()