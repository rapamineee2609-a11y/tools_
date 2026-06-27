from textual import on
from textual.widgets import Static, Button, Label, ListView, ListItem
from textual.containers import Container, Vertical
from textual.reactive import reactive

class Sidebar(Static):
    CSS = """
    Sidebar {
        background: #0d1b2a;
        color: #00ffcc;
        padding: 1;
        height: 100%;
    }
    
    .logo {
        text-style: bold;
        font-size: 16;
        color: #00ffcc;
        padding: 1;
        text-align: center;
    }
    
    .menu-item {
        padding: 1;
        margin: 0 0 0 0;
        background: transparent;
        border: none;
    }
    
    .menu-item:hover {
        background: #1a2634;
        border: solid #00ffcc 50%;
    }
    
    .menu-item:focus {
        background: #00ffcc;
        color: #0a0e17;
    }
    
    .menu-label {
        color: #00ffcc;
        text-style: bold;
        padding: 0 1;
    }
    """
    
    def compose(self):
        yield Container(
            Label("⚡ Cyber Suite", classes="logo"),
            Label("PRO 2026", classes="logo"),
            Container(
                Button("📊 Dashboard", id="menu_dashboard", classes="menu-item"),
                Button("🌐 Network", id="menu_network", classes="menu-item"),
                Button("🔍 DNS", id="menu_dns", classes="menu-item"),
                Button("🔒 SSL/TLS", id="menu_ssl", classes="menu-item"),
                Button("📡 Scanner", id="menu_scanner", classes="menu-item"),
                Button("🔐 Crypto", id="menu_crypto", classes="menu-item"),
                Button("📄 Reports", id="menu_reports", classes="menu-item"),
                Button("⚙️ Settings", id="menu_settings", classes="menu-item"),
                id="menu-container"
            ),
            id="sidebar-container"
        )
    
    def on_button_pressed(self, event: Button.Pressed):
        app = self.app
        screen_map = {
            "menu_dashboard": "dashboard",
            "menu_network": "network",
            "menu_dns": "dns",
            "menu_ssl": "ssl",
            "menu_scanner": "scanner",
            "menu_crypto": "crypto",
            "menu_reports": "reports",
            "menu_settings": "settings",
        }
        
        screen_id = screen_map.get(event.button.id)
        if screen_id:
            # Memuat screen yang sesuai di content area
            from ui.screens.dashboard import DashboardScreen
            from ui.screens.network import NetworkScreen
            from ui.screens.dns import DNSScreen
            from ui.screens.ssl import SSLScreen
            from ui.screens.scanner import ScannerScreen
            from ui.screens.crypto import CryptoScreen
            from ui.screens.reports import ReportsScreen
            from ui.screens.settings import SettingsScreen
            
            screen_classes = {
                "dashboard": DashboardScreen,
                "network": NetworkScreen,
                "dns": DNSScreen,
                "ssl": SSLScreen,
                "scanner": ScannerScreen,
                "crypto": CryptoScreen,
                "reports": ReportsScreen,
                "settings": SettingsScreen,
            }
            
            content = app.query_one("#content")
            content.remove_children()
            content.mount(screen_classes[screen_id]())
