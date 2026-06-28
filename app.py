from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, TabbedContent, TabPane, Button, Label, Static, DataTable, LoadingIndicator, ProgressBar
from textual.reactive import reactive
from textual.screen import Screen
from rich.text import Text

from ui.screens.dashboard import DashboardScreen
from ui.screens.network import NetworkScreen
from ui.screens.dns import DNSScreen
from ui.screens.ssl import SSLScreen
from ui.screens.scanner import ScannerScreen
from ui.screens.crypto import CryptoScreen
from ui.screens.reports import ReportsScreen
from ui.screens.settings import SettingsScreen
from ui.widgets.sidebar import Sidebar
from ui.widgets.notifications import NotificationCenter

from config.settings import settings
from database.db import db

class CyberSuiteApp(App):
    CSS = """
    Screen {
        background: #0a0e17;
        color: #00ffcc;
    }
    
    #sidebar {
        width: 20%;
        background: #111927;
        border-right: solid #00ffcc;
    }
    
    #content {
        width: 80%;
        padding: 1;
    }
    
    .header {
        background: #0d1b2a;
        color: #00ffcc;
        padding: 1;
    }
    
    .card {
        background: #1a2634;
        border: solid #00ffcc 50%;
        padding: 1;
        margin: 1;
    }
    
    .title {
        color: #00ffcc;
        text-style: bold;
        font-size: 16;
    }
    
    .metric {
        color: #00ffcc;
        text-style: bold;
    }
    
    .value {
        color: #ff6b6b;
        text-style: bold;
    }
    
    Button {
        background: #00ffcc;
        color: #0a0e17;
        border: none;
    }
    
    Button:hover {
        background: #00ddbb;
    }
    
    DataTable {
        background: #111927;
        border: solid #00ffcc;
    }
    
    DataTable > .datatable--header {
        background: #00ffcc;
        color: #0a0e17;
    }
    
    LoadingIndicator {
        color: #00ffcc;
    }
    
    ProgressBar {
        background: #111927;
        border: solid #00ffcc;
    }
    
    ProgressBar > .progress--bar {
        background: #00ffcc;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "focus_sidebar", "Sidebar"),
        ("c", "focus_content", "Content"),
        ("/", "open_search", "Search"),
        ("p", "open_palette", "Command Palette"),
        ("n", "show_notifications", "Notifications"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Horizontal(
            Sidebar(),
            Container(
                Container(id="content"),
                id="main-content"
            ),
            id="app-container"
        )
        yield Footer()
        yield NotificationCenter()
    
    def on_mount(self) -> None:
        self.title = settings.APP_NAME
        self.sub_title = f"v{settings.APP_VERSION}"
        self._load_dashboard()
    
    def _load_dashboard(self):
        content = self.query_one("#content")
        content.remove_children()
        content.mount(DashboardScreen())
    
    def action_focus_sidebar(self):
        self.query_one(Sidebar).focus()
    
    def action_focus_content(self):
        self.query_one("#content").focus()
    
    def action_open_search(self):
        self.push_screen("search")
    
    def action_open_palette(self):
        self.push_screen("command_palette")
    
    def action_show_notifications(self):
        self.query_one(NotificationCenter).toggle()
    
    def action_quit(self):
        self.exit()

if __name__ == "__main__":
    CyberSuiteApp().run()
