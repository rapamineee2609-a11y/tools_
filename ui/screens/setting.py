from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Button, Input, Switch, Dropdown, TextArea, DataTable
from textual import on
from database.db import db
from config.settings import settings

class SettingsScreen(Screen):
    CSS = """
    SettingsScreen {
        background: #0a0e17;
    }
    
    .setting-group {
        background: #111927;
        border: solid #00ffcc;
        margin: 1;
        padding: 1;
    }
    
    .setting-label {
        color: #00ffcc;
        text-style: bold;
    }
    """
    
    def compose(self):
        yield Container(
            Static("⚙️ Settings", classes="title"),
            Container(
                Label("Appearance", classes="setting-label"),
                Horizontal(
                    Label("Dark Mode:"),
                    Switch(value=True, id="dark_mode"),
                ),
                Label("Theme:"),
                Dropdown([
                    ("Cyber Green", "cyber"),
                    ("Matrix", "matrix"),
                    ("Neon Blue", "neon"),
                ], id="theme_select"),
                classes="setting-group"
            ),
            Container(
                Label("Logging", classes="setting-label"),
                Label("Log Level:"),
                Dropdown([
                    ("DEBUG", "debug"),
                    ("INFO", "info"),
                    ("WARNING", "warning"),
                    ("ERROR", "error"),
                ], id="log_level"),
                classes="setting-group"
            ),
            Container(
                Label("System", classes="setting-label"),
                Label(f"App Name: {settings.APP_NAME}"),
                Label(f"Version: {settings.APP_VERSION}"),
                Label(f"Database: {settings.DATABASE_URL}"),
                Label(f"Report Path: {settings.REPORT_PATH}"),
                classes="setting-group"
            ),
            Container(
                Label("Storage", classes="setting-label"),
                Label("Total Scans:"),
                Static(id="total_scans", classes="value"),
                Label("Last Scan:"),
                Static(id="last_scan", classes="value"),
                classes="setting-group"
            ),
            Button("Save Settings", id="save_settings"),
            Button("Clear Logs", id="clear_logs"),
            Button("Clean Database", id="clean_db"),
            id="settings-container"
        )
    
    async def on_mount(self):
        await self._update_stats()
    
    async def _update_stats(self):
        history = db.get_scan_history(limit=1000)
        total = len(history)
        last = history[0]["timestamp"] if history else "N/A"
        self.query_one("#total_scans").update(str(total))
        self.query_one("#last_scan").update(last)
    
    @on(Button.Pressed, "#save_settings")
    def on_save_settings(self):
        dark_mode = self.query_one("#dark_mode").value
        theme = self.query_one("#theme_select").value
        log_level = self.query_one("#log_level").value
        
        db.save_config("dark_mode", dark_mode)
        db.save_config("theme", theme)
        db.save_config("log_level", log_level)
        
        self.app.query_one(NotificationCenter).add_notification(
            "Settings Saved",
            "Configuration updated successfully.",
            "success"
        )
    
    @on(Button.Pressed, "#clear_logs")
    def on_clear_logs(self):
        # Clear logs
        with db._get_connection() as conn:
            conn.execute("DELETE FROM logs")
            conn.commit()
        self.app.query_one(NotificationCenter).add_notification(
            "Logs Cleared",
            "All log entries have been removed.",
            "warning"
        )
    
    @on(Button.Pressed, "#clean_db")
    def on_clean_db(self):
        with db._get_connection() as conn:
            conn.execute("DELETE FROM scan_history WHERE timestamp < datetime('now', '-30 days')")
            conn.commit()
        self.app.query_one(NotificationCenter).add_notification(
            "Database Cleaned",
            "Old records removed.",
            "success"
        )
