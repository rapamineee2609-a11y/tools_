from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Button, Input, TextArea, DataTable, ProgressBar
from textual import on
import hashlib
import base64
import urllib.parse
import binascii
import json
import jwt
import os
import re
from pathlib import Path
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
    .card {
        background: #111927;
        border: solid #00ffcc 50%;
        padding: 1;
        margin: 1;
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
    """

    def compose(self):
        yield Container(
            Static("🔐 Crypto Toolkit Pro", classes="title"),
            
            # ===== HASH GENERATOR =====
            Container(
                Label("📌 Hash Generator", classes="card-title"),
                Label("Input:"),
                Input(placeholder="Enter text or file path", id="hash_input"),
                Horizontal(
                    Button("MD5", id="hash_md5"),
                    Button("SHA1", id="hash_sha1"),
                    Button("SHA256", id="hash_sha256"),
                    Button("SHA512", id="hash_sha512"),
                    Button("File Hash", id="hash_file"),
                ),
                TextArea(id="hash_result", classes="result-box", read_only=True),
                classes="card"
            ),
            
            # ===== ENCODER / DECODER =====
            Container(
                Label("📌 Encoder / Decoder", classes="card-title"),
                Label("Input:"),
                Input(placeholder="Enter text or encoded data", id="encode_input"),
                Horizontal(
                    Button("Base64 Encode", id="b64_encode"),
                    Button("Base64 Decode", id="b64_decode"),
                    Button("URL Encode", id="url_encode"),
                    Button("URL Decode", id="url_decode"),
                    Button("Hex Encode", id="hex_encode"),
                    Button("Hex Decode", id="hex_decode"),
                ),
                TextArea(id="encode_result", classes="result-box", read_only=True),
                classes="card"
            ),
            
            # ===== JWT DECODER =====
            Container(
                Label("📌 JWT Decoder", classes="card-title"),
                Input(placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", id="jwt_input"),
                Button("Decode JWT", id="jwt_decode"),
                TextArea(id="jwt_result", classes="result-box", read_only=True),
                classes="card"
            ),
            
            # ===== PASSWORD STRENGTH =====
            Container(
                Label("📌 Password Strength Analyzer", classes="card-title"),
                Input(placeholder="Enter password to test", id="password_input"),
                Button("Analyze", id="password_analyze"),
                TextArea(id="password_result", classes="result-box", read_only=True),
                classes="card"
            ),
            
            # ===== INTEGRITY CHECKER =====
            Container(
                Label("📌 File Integrity Checker", classes="card-title"),
                Label("File Path:"),
                Input(placeholder="/path/to/file", id="integrity_file"),
                Label("Expected Hash:"),
                Input(placeholder="hash_value", id="integrity_hash"),
                Horizontal(
                    Button("Check MD5", id="integrity_md5"),
                    Button("Check SHA256", id="integrity_sha256"),
                ),
                TextArea(id="integrity_result", classes="result-box", read_only=True),
                classes="card"
            ),
            
            # ===== HISTORY =====
            Container(
                Label("📌 Scan History", classes="card-title"),
                DataTable(id="crypto_history_table"),
                classes="card"
            ),
        )
    
    async def on_mount(self):
        await self._load_history()
    
    async def _load_history(self):
        table = self.query_one("#crypto_history_table")
        table.clear()
        table.add_columns("ID", "Type", "Result", "Timestamp")
        history = db.get_scan_history(limit=20)
        for record in history:
            if record.get("scan_type") in ["hash", "base64", "url", "hex", "jwt", "password", "integrity"]:
                table.add_row(
                    str(record["id"]),
                    record.get("scan_type", ""),
                    str(record.get("result", ""))[:50],
                    record.get("timestamp", "")[:19]
                )
    
    # ===== HASH GENERATOR =====
    def _get_hash_input(self):
        return self.query_one("#hash_input").value.strip()
    
    def _set_hash_result(self, text):
        self.query_one("#hash_result").text = text
    
    @on(Button.Pressed, "#hash_md5")
    def on_hash_md5(self):
        text = self._get_hash_input()
        if text:
            result = hashlib.md5(text.encode()).hexdigest()
            self._set_hash_result(f"MD5: {result}")
            db.add_scan_history("hash", "md5", {"input": text, "result": result})
    
    @on(Button.Pressed, "#hash_sha1")
    def on_hash_sha1(self):
        text = self._get_hash_input()
        if text:
            result = hashlib.sha1(text.encode()).hexdigest()
            self._set_hash_result(f"SHA1: {result}")
            db.add_scan_history("hash", "sha1", {"input": text, "result": result})
    
    @on(Button.Pressed, "#hash_sha256")
    def on_hash_sha256(self):
        text = self._get_hash_input()
        if text:
            result = hashlib.sha256(text.encode()).hexdigest()
            self._set_hash_result(f"SHA256: {result}")
            db.add_scan_history("hash", "sha256", {"input": text, "result": result})
    
    @on(Button.Pressed, "#hash_sha512")
    def on_hash_sha512(self):
        text = self._get_hash_input()
        if text:
            result = hashlib.sha512(text.encode()).hexdigest()
            self._set_hash_result(f"SHA512: {result}")
            db.add_scan_history("hash", "sha512", {"input": text, "result": result})
    
    @on(Button.Pressed, "#hash_file")
    def on_hash_file(self):
        path = self._get_hash_input()
        if path and os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    data = f.read()
                    md5 = hashlib.md5(data).hexdigest()
                    sha1 = hashlib.sha1(data).hexdigest()
                    sha256 = hashlib.sha256(data).hexdigest()
                    sha512 = hashlib.sha512(data).hexdigest()
                result = f"File: {path}\nMD5: {md5}\nSHA1: {sha1}\nSHA256: {sha256}\nSHA512: {sha512}"
                self._set_hash_result(result)
                db.add_scan_history("hash", "file", {"path": path, "result": result})
            except Exception as e:
                self._set_hash_result(f"Error: {str(e)}")
        else:
            self._set_hash_result("File not found or invalid path.")
    
    # ===== ENCODER / DECODER =====
    def _get_encode_input(self):
        return self.query_one("#encode_input").value.strip()
    
    def _set_encode_result(self, text):
        self.query_one("#encode_result").text = text
    
    @on(Button.Pressed, "#b64_encode")
    def on_b64_encode(self):
        text = self._get_encode_input()
        if text:
            result = base64.b64encode(text.encode()).decode()
            self._set_encode_result(f"Base64 Encode: {result}")
            db.add_scan_history("base64", "encode", {"input": text, "result": result})
    
    @on(Button.Pressed, "#b64_decode")
    def on_b64_decode(self):
        text = self._get_encode_input()
        if text:
            try:
                result = base64.b64decode(text).decode()
                self._set_encode_result(f"Base64 Decode: {result}")
                db.add_scan_history("base64", "decode", {"input": text, "result": result})
            except Exception as e:
                self._set_encode_result(f"Error: {str(e)}")
    
    @on(Button.Pressed, "#url_encode")
    def on_url_encode(self):
        text = self._get_encode_input()
        if text:
            result = urllib.parse.quote(text)
            self._set_encode_result(f"URL Encode: {result}")
            db.add_scan_history("url", "encode", {"input": text, "result": result})
    
    @on(Button.Pressed, "#url_decode")
    def on_url_decode(self):
        text = self._get_encode_input()
        if text:
            try:
                result = urllib.parse.unquote(text)
                self._set_encode_result(f"URL Decode: {result}")
                db.add_scan_history("url", "decode", {"input": text, "result": result})
            except Exception as e:
                self._set_encode_result(f"Error: {str(e)}")
    
    @on(Button.Pressed, "#hex_encode")
    def on_hex_encode(self):
        text = self._get_encode_input()
        if text:
            result = binascii.hexlify(text.encode()).decode()
            self._set_encode_result(f"Hex Encode: {result}")
            db.add_scan_history("hex", "encode", {"input": text, "result": result})
    
    @on(Button.Pressed, "#hex_decode")
    def on_hex_decode(self):
        text = self._get_encode_input()
        if text:
            try:
                result = binascii.unhexlify(text).decode()
                self._set_encode_result(f"Hex Decode: {result}")
                db.add_scan_history("hex", "decode", {"input": text, "result": result})
            except Exception as e:
                self._set_encode_result(f"Error: {str(e)}")
    
    # ===== JWT DECODER =====
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
    
    # ===== PASSWORD STRENGTH =====
    @on(Button.Pressed, "#password_analyze")
    def on_password_analyze(self):
        password = self.query_one("#password_input").value.strip()
        if not password:
            self.query_one("#password_result").text = "Please enter a password."
            return
        
        score = 0
        feedback = []
        if len(password) < 8:
            feedback.append("Too short (min 8 chars)")
        elif len(password) >= 12:
            score += 2
        else:
            score += 1
        if re.search(r"[a-z]", password):
            score += 1
        else:
            feedback.append("Add lowercase")
        if re.search(r"[A-Z]", password):
            score += 1
        else:
            feedback.append("Add uppercase")
        if re.search(r"\d", password):
            score += 1
        else:
            feedback.append("Add numbers")
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 2
        else:
            feedback.append("Add special chars")
        if password.lower() in ["password", "123456", "qwerty", "admin", "letmein", "welcome"]:
            score -= 3
            feedback.append("Very common password")
        
        if score <= 2:
            strength = "Weak 🔴"
        elif score <= 4:
            strength = "Moderate 🟡"
        elif score <= 6:
            strength = "Strong 🟢"
        else:
            strength = "Excellent 💪"
        
        result = f"Password Strength: {strength}\nScore: {score}/8\nFeedback:\n- " + "\n- ".join(feedback) if feedback else "Good password!"
        self.query_one("#password_result").text = result
        db.add_scan_history("password", "analyze", {"password": password[:5]+"***", "result": result})
    
    # ===== INTEGRITY CHECKER =====
    def _get_integrity_file(self):
        return self.query_one("#integrity_file").value.strip()
    
    def _get_integrity_hash(self):
        return self.query_one("#integrity_hash").value.strip()
    
    def _set_integrity_result(self, text):
        self.query_one("#integrity_result").text = text
    
    @on(Button.Pressed, "#integrity_md5")
    def on_integrity_md5(self):
        file_path = self._get_integrity_file()
        expected = self._get_integrity_hash()
        if not file_path or not expected:
            self._set_integrity_result("Please provide file path and expected hash.")
            return
        if not os.path.exists(file_path):
            self._set_integrity_result("File not found.")
            return
        try:
            with open(file_path, "rb") as f:
                actual = hashlib.md5(f.read()).hexdigest()
            status = "✅ MATCH" if actual == expected else "❌ MISMATCH"
            result = f"File: {file_path}\nExpected MD5: {expected}\nActual MD5:   {actual}\nStatus: {status}"
            self._set_integrity_result(result)
            db.add_scan_history("integrity", "md5", {"file": file_path, "result": result})
        except Exception as e:
            self._set_integrity_result(f"Error: {str(e)}")
    
    @on(Button.Pressed, "#integrity_sha256")
    def on_integrity_sha256(self):
        file_path = self._get_integrity_file()
        expected = self._get_integrity_hash()
        if not file_path or not expected:
            self._set_integrity_result("Please provide file path and expected hash.")
            return
        if not os.path.exists(file_path):
            self._set_integrity_result("File not found.")
            return
        try:
            with open(file_path, "rb") as f:
                actual = hashlib.sha256(f.read()).hexdigest()
            status = "✅ MATCH" if actual == expected else "❌ MISMATCH"
            result = f"File: {file_path}\nExpected SHA256: {expected}\nActual SHA256:   {actual}\nStatus: {status}"
            self._set_integrity_result(result)
            db.add_scan_history("integrity", "sha256", {"file": file_path, "result": result})
        except Exception as e:
            self._set_integrity_result(f"Error: {str(e)}")
