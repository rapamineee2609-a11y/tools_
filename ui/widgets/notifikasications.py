from textual.widgets import Static, Label
from textual.containers import Container, Vertical
from textual.reactive import reactive
from datetime import datetime

class NotificationCenter(Static):
    CSS = """
    NotificationCenter {
        background: #0d1b2a;
        border: solid #00ffcc;
        padding: 1;
        width: 40%;
        height: 60%;
        position: absolute;
        right: 0;
        top: 0;
        display: none;
    }
    
    .notification-item {
        background: #111927;
        padding: 1;
        margin: 1 0;
        border: solid #00ffcc 50%;
    }
    
    .notification-time {
        color: #8899aa;
        font-size: 10;
    }
    
    .notification-title {
        color: #00ffcc;
        text-style: bold;
    }
    
    .notification-body {
        color: #ccddff;
    }
    """
    
    def compose(self):
        yield Container(
            Label("📬 Notifications", classes="logo"),
            Container(id="notification_list"),
            id="notification_container"
        )
    
    def toggle(self):
        if self.display:
            self.display = False
        else:
            self.display = True
    
    def add_notification(self, title: str, message: str, level: str = "info"):
        list_container = self.query_one("#notification_list")
        time_str = datetime.now().strftime("%H:%M:%S")
        list_container.mount(
            Container(
                Label(f"[{time_str}]", classes="notification-time"),
                Label(title, classes="notification-title"),
                Label(message, classes="notification-body"),
                classes="notification-item"
            )
        )
