from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Button, Input, TextArea, DataTable, ProgressBar
from textual import on
import asyncio
import socket
import aiohttp
from bs4 import BeautifulSoup
from database.db import db

class ScannerScreen(Screen):
    CSS = """
    ScannerScreen {
        background: #0a0e17;
    }
    
    .input-field {
        margin: 1;
        background: #111927;
        border: solid #00ffcc;
    }
    
    .result-box {
        background: #111927;
        border: solid #00ffcc;
        margin: 1;
        padding: 1;
    }
    
    ProgressBar {
        margin: 1;
    }
    """
    
    def compose(self):
        yield Container(
            Static("📡 Advanced Scanner", classes="title"),
            Container(
                Label("Enter Target:"),
                Input(placeholder="example.com", id="scanner_input"),
                Horizontal(
                    Button("Port Scan", id="scan_ports"),
                    Button("Tech Detector", id="scan_tech"),
                    Button("HTTP Headers", id="scan_headers"),
                ),
                ProgressBar(id="scan_progress"),
                TextArea(id="scanner_result", classes="result-box", read_only=True),
                id="scanner-container"
            ),
            DataTable(id="scanner_history_table")
        )
    
    async def on_mount(self):
        await self._load_history()
    
    async def _load_history(self):
        table = self.query_one("#scanner_history_table")
        table.clear()
        table.add_columns("ID", "Target", "Type", "Result", "Timestamp")
        history = db.get_scan_history(limit=10)
        for record in history:
            if record["scan_type"] in ["port_scan", "tech_detect", "http_headers"]:
                table.add_row(
                    str(record["id"]),
                    record["target"],
                    record["scan_type"],
                    record["result"][:50] if record["result"] else "N/A",
                    record["timestamp"][:19]
                )
    
    @on(Button.Pressed, "#scan_ports")
    async def on_port_scan(self):
        target = self.query_one("#scanner_input").value.strip()
        if not target:
            return
        result = await self._scan_ports(target)
        self.query_one("#scanner_result").text = result
        db.add_scan_history("port_scan", target, {"result": result})
    
    @on(Button.Pressed, "#scan_tech")
    async def on_tech_detect(self):
        target = self.query_one("#scanner_input").value.strip()
        if not target:
            return
        result = await self._detect_tech(target)
        self.query_one("#scanner_result").text = result
        db.add_scan_history("tech_detect", target, {"result": result})
    
    @on(Button.Pressed, "#scan_headers")
    async def on_http_headers(self):
        target = self.query_one("#scanner_input").value.strip()
        if not target:
            return
        result = await self._get_headers(target)
        self.query_one("#scanner_result").text = result
        db.add_scan_history("http_headers", target, {"result": result})
    
    async def _scan_ports(self, target: str, ports: list = None) -> str:
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5432, 5900, 8080, 8443]
        
        result = f"Port Scan for {target}\n"
        result += "=" * 40 + "\n"
        progress = self.query_one("#scan_progress")
        total = len(ports)
        open_ports = []
        
        for i, port in enumerate(ports):
            progress.progress = (i + 1) / total * 100
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                if sock.connect_ex((target, port)) == 0:
                    open_ports.append(port)
                    result += f"  ✅ Port {port} - OPEN\n"
                sock.close()
            except:
                pass
        
        result += f"\nFound {len(open_ports)} open ports."
        return result
    
    async def _detect_tech(self, target: str) -> str:
        try:
            url = f"https://{target}" if not target.startswith("http") else target
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5, ssl=False) as resp:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    result = f"Technology Detection for {target}\n"
                    result += "=" * 40 + "\n"
                    result += f"  - Status: {resp.status}\n"
                    result += f"  - Server: {resp.headers.get('Server', 'Unknown')}\n"
                    result += f"  - Content-Type: {resp.headers.get('Content-Type', 'Unknown')}\n"
                    result += f"  - X-Powered-By: {resp.headers.get('X-Powered-By', 'Not Detected')}\n"
                    
                    # Detect frameworks
                    frameworks = []
                    if soup.find("script", src=lambda x: x and "react" in x.lower()):
                        frameworks.append("React")
                    if soup.find("script", src=lambda x: x and "vue" in x.lower()):
                        frameworks.append("Vue.js")
                    if soup.find("script", src=lambda x: x and "angular" in x.lower()):
                        frameworks.append("Angular")
                    
                    if frameworks:
                        result += f"  - Frameworks: {', '.join(frameworks)}\n"
                    
                    return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _get_headers(self, target: str) -> str:
        try:
            url = f"https://{target}" if not target.startswith("http") else target
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5, ssl=False) as resp:
                    result = f"HTTP Headers for {target}\n"
                    result += "=" * 40 + "\n"
                    result += f"  - Status: {resp.status} {resp.reason}\n"
                    result += f"  - Version: {resp.version}\n"
                    result += "\nHeaders:\n"
                    for key, value in resp.headers.items():
                        result += f"  - {key}: {value}\n"
                    return result
        except Exception as e:
            return f"Error: {str(e)}"
