from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Button, Input, TextArea, DataTable
from textual import on
import hashlib
import base64
import urllib.parse
import binascii
import json
import jwt
from database.db import db

class CryptoScreen(Screen):
    CSS = """
    CryptoScreen {
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
            Static("🔐 Crypto Toolkit", classes="title"),
            Container(
                Label("Input:"),
                Input(placeholder="Enter text or data", id="crypto_input"),
                Horizontal(
                    Button("MD5", id="hash_md5"),
                    Button("SHA1", id="hash_sha1"),
                    Button("SHA256", id="hash_sha256"),
                    Button("SHA512", id="hash_sha512"),
                    Button("Base64 Encode", id="b64_encode"),
                    Button("Base64 Decode", id="b64_decode"),
                    Button("URL Encode", id="url_encode"),
                    Button("URL Decode", id="url_decode"),
                    Button("Hex Encode", id="hex_encode"),
                    Button("Hex Decode", id="hex_decode"),
                ),
                TextArea(id="crypto_result", classes="result-box", read_only=True),
                id="crypto-container"
            ),
            Container(
                Label("JWT Decoder"),
                Input(placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", id="jwt_input"),
                Button("Decode JWT", id="jwt_decode"),
                TextArea(id="jwt_result", classes="result-box", read_only=True),
                id="jwt-container"
            ),
            DataTable(id="crypto_history_table")
        )
    
    async def on_mount(self):
        await self._load_history()
    
    async def _load_history(self):
        table = self.query_one("#crypto_history_table")
        table.clear()
        table.add_columns("ID", "Type", "Result", "Timestamp")
        history = db.get_scan_history(limit=10)
        for record in history:
            if record["scan_type"] in ["hash", "base64", "url", "hex", "jwt"]:
                table.add_row(
                    str(record["id"]),
                    record["scan_type"],
                    record["result"][:50] if record["result"] else "N/A",
                    record["timestamp"][:19]
                )
    
    def _get_input(self):
        return self.query_one("#crypto_input").value.strip()
    
    def _set_result(self, text):
        self.query_one("#crypto_result").text = text
    
    @on(Button.Pressed, "#hash_md5")
    def on_hash_md5(self):
        text = self._get_input()
        if text:
            result = hashlib.md5(text.encode()).hexdigest()
            self._set_result(f"MD5: {result}")
            db.add_scan_history("hash", "md5", {"input": text, "result": result})
    
    @on(Button.Pressed, "#hash_sha1")
    def on_hash_sha1(self):
        text = self._get_input()
        if text:
            result = hashlib.sha1(text.encode()).hexdigest()
            self._set_result(f"SHA1: {result}")
            db.add_scan_history("hash", "sha1", {"input": text, "result": result})
    
    @on(Button.Pressed, "#hash_sha256")
    def on_hash_sha256(self):
        text = self._get_input()
        if text:
            result = hashlib.sha256(text.encode()).hexdigest()
            self._set_result(f"SHA256: {result}")
            db.add_scan_history("hash", "sha256", {"input": text, "result": result})
    
    @on(Button.Pressed, "#hash_sha512")
    def on_hash_sha512(self):
        text = self._get_input()
        if text:
            result = hashlib.sha512(text.encode()).hexdigest()
            self._set_result(f"SHA512: {result}")
            db.add_scan_history("hash", "sha512", {"input": text, "result": result})
    
    @on(Button.Pressed, "#b64_encode")
    def on_b64_encode(self):
        text = self._get_input()
        if text:
            result = base64.b64encode(text.encode()).decode()
            self._set_result(f"Base64 Encode: {result}")
            db.add_scan_history("base64", "encode", {"input": text, "result": result})
    
    @on(Button.Pressed, "#b64_decode")
    def on_b64_decode(self):
        text = self._get_input()
        if text:
            try:
                result = base64.b64decode(text).decode()
                self._set_result(f"Base64 Decode: {result}")
                db.add_scan_history("base64", "decode", {"input": text, "result": result})
            except Exception as e:
                self._set_result(f"Error: {str(e)}")
    
    @on(Button.Pressed, "#url_encode")
    def on_url_encode(self):
        text = self._get_input()
        if text:
            result = urllib.parse.quote(text)
            self._set_result(f"URL Encode: {result}")
            db.add_scan_history("url", "encode", {"input": text, "result": result})
    
    @on(Button.Pressed, "#url_decode")
    def on_url_decode(self):
        text = self._get_input()
        if text:
            try:
                result = urllib.parse.unquote(text)
                self._set_result(f"URL Decode: {result}")
                db.add_scan_history("url", "decode", {"input": text, "result": result})
            except Exception as e:
                self._set_result(f"Error: {str(e)}")
    
    @on(Button.Pressed, "#hex_encode")
    def on_hex_encode(self):
        text = self._get_input()
        if text:
            result = binascii.hexlify(text.encode()).decode()
            self._set_result(f"Hex Encode: {result}")
            db.add_scan_history("hex", "encode", {"input": text, "result": result})
    
    @on(Button.Pressed, "#hex_decode")
    def on_hex_decode(self):
        text = self._get_input()
        if text:
            try:
                result = binascii.unhexlify(text).decode()
                self._set_result(f"Hex Decode: {result}")
                db.add_scan_history("hex", "decode", {"input": text, "result": result})
            except Exception as e:
                self._set_result(f"Error: {str(e)}")
    
    @on(Button.Pressed, "#jwt_decode")
    def on_jwt_decode(self):
        token = self.query_one("#jwt_input").value.strip()
        if token:
            try:
                decoded = jwt.decode(token, algorithms=["HS256"], verify=False)
                result = json.dumps(decoded, indent=2)
                self.query_one("#jwt_result").text = f"JWT Decoded:\n{result}"
                db.add_scan_history("jwt", "decode", {"token": token, "result": result})
            except Exception as e:
                self.query_one("#jwt_result").text = f"Error: {str(e)}"
