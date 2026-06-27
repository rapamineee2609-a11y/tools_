from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Button, DataTable, Input, TextArea
from textual import on
import asyncio
import socket
import aiohttp
from core.network import get_local_ip, get_public_ip, ping_host, traceroute_host

class NetworkScreen(Screen):
    CSS = """
    NetworkScreen {
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
    """
    
    def compose(self):
        yield Container(
            Static("🌐 Network Information", classes="title"),
            Horizontal(
                Container(
                    Label("Local IP:"),
                    Static(id="local_ip_result", classes="value")
                ),
                Container(
                    Label("Public IP:"),
                    Static(id="public_ip_result", classes="value")
                ),
                Container(
                    Label("Internet Status:"),
                    Static(id="internet_status_result", classes="value")
                ),
            ),
            Container(
                Label("🔍 Host Discovery"),
                Input(placeholder="Enter host or IP", id="host_input"),
                Button("Ping", id="ping_btn"),
                Button("Traceroute", id="traceroute_btn"),
                Button("Port Scan", id="portscan_btn"),
                TextArea(id="network_result", classes="result-box", read_only=True),
                id="network-container"
            ),
            DataTable(id="network_table")
        )
    
    async def on_mount(self):
        await self._update_network_info()
        self.set_interval(30.0, self._update_network_info)
    
    async def _update_network_info(self):
        local = get_local_ip()
        public = await get_public_ip()
        from core.network import check_internet
        internet = await check_internet()
        
        self.query_one("#local_ip_result").update(local or "N/A")
        self.query_one("#public_ip_result").update(public or "N/A")
        self.query_one("#internet_status_result").update("✅ Connected" if internet else "❌ Disconnected")
    
    @on(Button.Pressed, "#ping_btn")
    async def on_ping(self):
        host = self.query_one("#host_input").value.strip()
        if not host:
            return
        result = await ping_host(host)
        self.query_one("#network_result").text = result
        db.add_scan_history("ping", host, {"result": result})
    
    @on(Button.Pressed, "#traceroute_btn")
    async def on_traceroute(self):
        host = self.query_one("#host_input").value.strip()
        if not host:
            return
        result = await traceroute_host(host)
        self.query_one("#network_result").text = result
        db.add_scan_history("traceroute", host, {"result": result})
