from textual import on
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import Header, Footer, Static, Label, Button, DataTable, ProgressBar, LoadingIndicator
from textual.reactive import reactive
from rich.text import Text
from rich.table import Table
from rich.console import Console

import psutil
import subprocess
import asyncio
from datetime import datetime
import aiohttp

from database.db import db
from core.network import get_public_ip, get_local_ip, check_internet

class DashboardScreen(Screen):
    CSS = """
    DashboardScreen {
        background: #0a0e17;
    }
    
    .grid-container {
        layout: grid;
        grid-size: 4 4;
        grid-gutter: 1 1;
        padding: 1;
    }
    
    .card {
        background: #111927;
        border: solid #00ffcc 50%;
        padding: 1;
        height: 8;
    }
    
    .card-title {
        color: #00ffcc;
        text-style: bold;
    }
    
    .card-value {
        color: #ff6b6b;
        text-style: bold;
        font-size: 16;
    }
    
    .card-sub {
        color: #8899aa;
    }
    
    .chart-container {
        background: #111927;
        border: solid #00ffcc;
        padding: 1;
        height: 20;
        margin-top: 1;
    }
    
    .table-container {
        background: #111927;
        border: solid #00ffcc;
        padding: 1;
        height: 15;
        margin-top: 1;
    }
    """
    
    def compose(self):
        yield Container(
            Horizontal(
                Container(
                    Static("CPU", classes="card-title"),
                    Static(id="cpu_value", classes="card-value"),
                    Static("", classes="card-sub"),
                    classes="card"
                ),
                Container(
                    Static("RAM", classes="card-title"),
                    Static(id="ram_value", classes="card-value"),
                    Static("", classes="card-sub"),
                    classes="card"
                ),
                Container(
                    Static("Storage", classes="card-title"),
                    Static(id="storage_value", classes="card-value"),
                    Static("", classes="card-sub"),
                    classes="card"
                ),
                Container(
                    Static("Battery", classes="card-title"),
                    Static(id="battery_value", classes="card-value"),
                    Static("", classes="card-sub"),
                    classes="card"
                ),
                classes="grid-container"
            ),
            Horizontal(
                Container(
                    Static("Internet Status", classes="card-title"),
                    Static(id="internet_status", classes="card-value"),
                    Static("", classes="card-sub"),
                    classes="card"
                ),
                Container(
                    Static("Public IP", classes="card-title"),
                    Static(id="public_ip", classes="card-value"),
                    Static("", classes="card-sub"),
                    classes="card"
                ),
                Container(
                    Static("Local IP", classes="card-title"),
                    Static(id="local_ip", classes="card-value"),
                    Static("", classes="card-sub"),
                    classes="card"
                ),
                Container(
                    Static("Running Tasks", classes="card-title"),
                    Static(id="running_tasks", classes="card-value"),
                    Static("", classes="card-sub"),
                    classes="card"
                ),
                classes="grid-container"
            ),
            Container(
                Static("Recent Scans", classes="card-title"),
                DataTable(id="recent_scans_table"),
                classes="card"
            ),
            Container(
                Static("Notification Center", classes="card-title"),
                Static(id="notification_messages"),
                classes="card"
            ),
            id="dashboard-content"
        )
    
    async def on_mount(self):
        await self._update_stats()
        self.set_interval(3.0, self._update_stats)
        await self._load_recent_scans()
    
    async def _update_stats(self):
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        self.query_one("#cpu_value").update(f"{cpu}%")
        self.query_one("#ram_value").update(f"{ram.percent}% ({ram.used // (1024**3)}GB / {ram.total // (1024**3)}GB)")
        self.query_one("#storage_value").update(f"{disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)")
        
        # Battery (Android)
        battery_status = await self._get_battery()
        self.query_one("#battery_value").update(battery_status)
        
        # Internet
        internet = await check_internet()
        self.query_one("#internet_status").update("✅ Connected" if internet else "❌ Disconnected")
        
        # IP
        public_ip = await get_public_ip()
        local_ip = get_local_ip()
        self.query_one("#public_ip").update(public_ip or "N/A")
        self.query_one("#local_ip").update(local_ip or "N/A")
        
        # Tasks
        tasks = len(asyncio.all_tasks())
        self.query_one("#running_tasks").update(str(tasks))
    
    async def _get_battery(self):
        try:
            result = subprocess.run(
                ["dumpsys", "battery"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "level" in line:
                        level = line.split(":")[1].strip()
                        return f"{level}%"
        except:
            pass
        return "N/A"
    
    async def _load_recent_scans(self):
        table = self.query_one("#recent_scans_table")
        table.clear()
        table.add_columns("ID", "Type", "Target", "Status", "Timestamp")
        
        history = db.get_scan_history(limit=10)
        for record in history:
            table.add_row(
                str(record["id"]),
                record["scan_type"],
                record["target"],
                record["status"],
                record["timestamp"][:19]
            )
