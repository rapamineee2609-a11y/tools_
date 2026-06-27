from textual.screen import Screen
from textual.containers import Container, Horizontal
from textual.widgets import Static, Label, Button, Input, TextArea, DataTable
from textual import on
import ssl
import socket
import asyncio
from datetime import datetime
from OpenSSL import crypto
import aiohttp
from database.db import db

class SSLScreen(Screen):
    CSS = """
    SSLScreen {
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
            Static("🔒 SSL/TLS Checker", classes="title"),
            Container(
                Label("Enter Domain/IP:"),
                Input(placeholder="example.com:443", id="ssl_input"),
                Horizontal(
                    Button("Check SSL", id="ssl_check"),
                    Button("Check Certificate", id="ssl_cert"),
                    Button("Get Ciphers", id="ssl_ciphers"),
                ),
                TextArea(id="ssl_result", classes="result-box", read_only=True),
                id="ssl-container"
            ),
            DataTable(id="ssl_history_table")
        )
    
    async def on_mount(self):
        await self._load_history()
    
    async def _load_history(self):
        table = self.query_one("#ssl_history_table")
        table.clear()
        table.add_columns("ID", "Target", "Type", "Result", "Timestamp")
        history = db.get_scan_history(limit=10)
        for record in history:
            if record["scan_type"] in ["ssl", "certificate"]:
                table.add_row(
                    str(record["id"]),
                    record["target"],
                    record["scan_type"],
                    record["result"][:50] if record["result"] else "N/A",
                    record["timestamp"][:19]
                )
    
    @on(Button.Pressed, "#ssl_check")
    async def on_ssl_check(self):
        target = self.query_one("#ssl_input").value.strip()
        if not target:
            return
        result = await self._check_ssl(target)
        self.query_one("#ssl_result").text = result
        db.add_scan_history("ssl", target, {"result": result})
    
    @on(Button.Pressed, "#ssl_cert")
    async def on_ssl_cert(self):
        target = self.query_one("#ssl_input").value.strip()
        if not target:
            return
        result = await self._get_cert_info(target)
        self.query_one("#ssl_result").text = result
        db.add_scan_history("certificate", target, {"result": result})
    
    @on(Button.Pressed, "#ssl_ciphers")
    async def on_ssl_ciphers(self):
        target = self.query_one("#ssl_input").value.strip()
        if not target:
            return
        result = await self._get_ciphers(target)
        self.query_one("#ssl_result").text = result
    
    async def _check_ssl(self, target: str) -> str:
        try:
            host, port = target.split(":") if ":" in target else (target, 443)
            port = int(port)
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    result = f"SSL/TLS Certificate for {host}:{port}\n"
                    result += f"  - Subject: {cert.get('subject', 'N/A')}\n"
                    result += f"  - Issuer: {cert.get('issuer', 'N/A')}\n"
                    result += f"  - Valid from: {cert.get('notBefore', 'N/A')}\n"
                    result += f"  - Valid until: {cert.get('notAfter', 'N/A')}\n"
                    result += f"  - Version: {ssock.version()}\n"
                    result += f"  - Cipher: {ssock.cipher()}\n"
                    return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _get_cert_info(self, target: str) -> str:
        try:
            host, port = target.split(":") if ":" in target else (target, 443)
            port = int(port)
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssl.DER_cert_to_PEM_cert(ssock.getpeercert(True))
                    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
                    result = f"Certificate Details for {host}:{port}\n"
                    result += f"  - Subject: {x509.get_subject().get_components()}\n"
                    result += f"  - Issuer: {x509.get_issuer().get_components()}\n"
                    result += f"  - Version: {x509.get_version()}\n"
                    result += f"  - Serial: {x509.get_serial_number()}\n"
                    result += f"  - Not Before: {x509.get_notBefore().decode()}\n"
                    result += f"  - Not After: {x509.get_notAfter().decode()}\n"
                    return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _get_ciphers(self, target: str) -> str:
        try:
            host, port = target.split(":") if ":" in target else (target, 443)
            port = int(port)
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    return f"Supported cipher: {ssock.cipher()}"
        except Exception as e:
            return f"Error: {str(e)}"
