from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Button, Input, TextArea, DataTable
from textual import on
import asyncio
import aiohttp
import dns.resolver
import dns.reversename
from database.db import db

class DNSScreen(Screen):
    CSS = """
    DNSScreen {
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
            Static("🔍 DNS Toolkit", classes="title"),
            Container(
                Label("Enter Domain:"),
                Input(placeholder="example.com", id="dns_input"),
                Horizontal(
                    Button("A Record", id="dns_a"),
                    Button("AAAA Record", id="dns_aaaa"),
                    Button("MX Record", id="dns_mx"),
                    Button("NS Record", id="dns_ns"),
                    Button("CNAME", id="dns_cname"),
                    Button("TXT", id="dns_txt"),
                    Button("Reverse DNS", id="dns_reverse"),
                    Button("All Records", id="dns_all"),
                ),
                TextArea(id="dns_result", classes="result-box", read_only=True),
                id="dns-container"
            ),
            DataTable(id="dns_history_table")
        )
    
    async def on_mount(self):
        await self._load_history()
    
    async def _load_history(self):
        table = self.query_one("#dns_history_table")
        table.clear()
        table.add_columns("ID", "Target", "Type", "Result", "Timestamp")
        history = db.get_scan_history(limit=10)
        for record in history:
            if record["scan_type"] == "dns":
                table.add_row(
                    str(record["id"]),
                    record["target"],
                    "DNS",
                    record["result"][:50] if record["result"] else "N/A",
                    record["timestamp"][:19]
                )
    
    @on(Button.Pressed, "#dns_a")
    async def on_dns_a(self):
        domain = self.query_one("#dns_input").value.strip()
        if not domain:
            return
        result = await self._resolve_dns(domain, "A")
        self.query_one("#dns_result").text = result
    
    @on(Button.Pressed, "#dns_aaaa")
    async def on_dns_aaaa(self):
        domain = self.query_one("#dns_input").value.strip()
        if not domain:
            return
        result = await self._resolve_dns(domain, "AAAA")
        self.query_one("#dns_result").text = result
    
    @on(Button.Pressed, "#dns_mx")
    async def on_dns_mx(self):
        domain = self.query_one("#dns_input").value.strip()
        if not domain:
            return
        result = await self._resolve_dns(domain, "MX")
        self.query_one("#dns_result").text = result
    
    @on(Button.Pressed, "#dns_ns")
    async def on_dns_ns(self):
        domain = self.query_one("#dns_input").value.strip()
        if not domain:
            return
        result = await self._resolve_dns(domain, "NS")
        self.query_one("#dns_result").text = result
    
    @on(Button.Pressed, "#dns_cname")
    async def on_dns_cname(self):
        domain = self.query_one("#dns_input").value.strip()
        if not domain:
            return
        result = await self._resolve_dns(domain, "CNAME")
        self.query_one("#dns_result").text = result
    
    @on(Button.Pressed, "#dns_txt")
    async def on_dns_txt(self):
        domain = self.query_one("#dns_input").value.strip()
        if not domain:
            return
        result = await self._resolve_dns(domain, "TXT")
        self.query_one("#dns_result").text = result
    
    @on(Button.Pressed, "#dns_reverse")
    async def on_dns_reverse(self):
        domain = self.query_one("#dns_input").value.strip()
        if not domain:
            return
        result = await self._reverse_dns(domain)
        self.query_one("#dns_result").text = result
    
    @on(Button.Pressed, "#dns_all")
    async def on_dns_all(self):
        domain = self.query_one("#dns_input").value.strip()
        if not domain:
            return
        result = ""
        for record in ["A", "AAAA", "MX", "NS", "CNAME", "TXT"]:
            r = await self._resolve_dns(domain, record)
            result += f"=== {record} ===\n{r}\n\n"
        self.query_one("#dns_result").text = result
    
    async def _resolve_dns(self, domain: str, record_type: str) -> str:
        try:
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(domain, record_type)
            result = f"DNS {record_type} records for {domain}:\n"
            for answer in answers:
                result += f"  - {answer}\n"
            db.add_scan_history("dns", domain, {"type": record_type, "result": result})
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _reverse_dns(self, domain: str) -> str:
        try:
            ip = socket.gethostbyname(domain)
            reverse = dns.reversename.from_address(ip)
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(reverse, "PTR")
            result = f"Reverse DNS for {ip}:\n"
            for answer in answers:
                result += f"  - {answer}\n"
            return result
        except Exception as e:
            return f"Error: {str(e)}"
