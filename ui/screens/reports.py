from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Button, Input, TextArea, DataTable, ProgressBar
from textual import on
import json
import csv
import yaml
import jinja2
from datetime import datetime
from pathlib import Path
import os
from database.db import db
from config.settings import settings

class ReportsScreen(Screen):
    CSS = """
    ReportsScreen {
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
        height: 20;
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
    .button-success {
        background: #00ffcc;
        color: #0a0e17;
        border: none;
    }
    .button-success:hover {
        background: #00ddbb;
    }
    """

    def compose(self):
        yield Container(
            Static("📄 Report Generator Pro", classes="title"),
            
            # ===== REPORT CONFIG =====
            Container(
                Label("📌 Report Configuration", classes="card-title"),
                Label("Report Name:"),
                Input(placeholder="my_security_report", id="report_name"),
                Label("Format:"),
                Horizontal(
                    Button("JSON", id="format_json", classes="button-success"),
                    Button("CSV", id="format_csv", classes="button-success"),
                    Button("HTML", id="format_html", classes="button-success"),
                    Button("Markdown", id="format_md", classes="button-success"),
                    Button("YAML", id="format_yaml", classes="button-success"),
                    Button("All Formats", id="format_all", classes="button-success"),
                ),
                Label("Include Data:"),
                Horizontal(
                    Button("Scan History", id="include_history"),
                    Button("Configuration", id="include_config"),
                    Button("Logs", id="include_logs"),
                    Button("All Data", id="include_all"),
                ),
                Button("Generate Report", id="generate_report", classes="button-success"),
                classes="card"
            ),
            
            # ===== PREVIEW =====
            Container(
                Label("📌 Report Preview", classes="card-title"),
                TextArea(id="preview_result", classes="result-box", read_only=True),
                classes="card"
            ),
            
            # ===== HISTORY =====
            Container(
                Label("📌 Report History", classes="card-title"),
                DataTable(id="report_history_table"),
                classes="card"
            ),
            
            # ===== EXPORT =====
            Container(
                Label("📌 Export / Share", classes="card-title"),
                Horizontal(
                    Button("Export PDF", id="export_pdf"),
                    Button("Export HTML", id="export_html"),
                    Button("Export JSON", id="export_json"),
                ),
                classes="card"
            ),
        )
    
    async def on_mount(self):
        await self._load_history()
    
    async def _load_history(self):
        table = self.query_one("#report_history_table")
        table.clear()
        table.add_columns("ID", "Name", "Format", "Created", "Status")
        history = db.get_scan_history(limit=20)
        for record in history:
            if record.get("scan_type") == "report":
                table.add_row(
                    str(record["id"]),
                    record.get("target", "N/A"),
                    record.get("scan_type", "report"),
                    record.get("timestamp", "")[:19],
                    "Completed"
                )
    
    def _get_report_name(self):
        name = self.query_one("#report_name").value.strip()
        if not name:
            name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return name
    
    def _set_preview(self, text):
        self.query_one("#preview_result").text = text
    
    # ===== FORMAT SELECTION =====
    selected_formats = []
    
    @on(Button.Pressed, "#format_json")
    def on_format_json(self):
        if "json" not in self.selected_formats:
            self.selected_formats.append("json")
            self._set_preview(f"[+] JSON format added.\nCurrent formats: {', '.join(self.selected_formats)}")
        else:
            self.selected_formats.remove("json")
            self._set_preview(f"[-] JSON format removed.\nCurrent formats: {', '.join(self.selected_formats)}")
    
    @on(Button.Pressed, "#format_csv")
    def on_format_csv(self):
        if "csv" not in self.selected_formats:
            self.selected_formats.append("csv")
            self._set_preview(f"[+] CSV format added.\nCurrent formats: {', '.join(self.selected_formats)}")
        else:
            self.selected_formats.remove("csv")
            self._set_preview(f"[-] CSV format removed.\nCurrent formats: {', '.join(self.selected_formats)}")
    
    @on(Button.Pressed, "#format_html")
    def on_format_html(self):
        if "html" not in self.selected_formats:
            self.selected_formats.append("html")
            self._set_preview(f"[+] HTML format added.\nCurrent formats: {', '.join(self.selected_formats)}")
        else:
            self.selected_formats.remove("html")
            self._set_preview(f"[-] HTML format removed.\nCurrent formats: {', '.join(self.selected_formats)}")
    
    @on(Button.Pressed, "#format_md")
    def on_format_md(self):
        if "md" not in self.selected_formats:
            self.selected_formats.append("md")
            self._set_preview(f"[+] Markdown format added.\nCurrent formats: {', '.join(self.selected_formats)}")
        else:
            self.selected_formats.remove("md")
            self._set_preview(f"[-] Markdown format removed.\nCurrent formats: {', '.join(self.selected_formats)}")
    
    @on(Button.Pressed, "#format_yaml")
    def on_format_yaml(self):
        if "yaml" not in self.selected_formats:
            self.selected_formats.append("yaml")
            self._set_preview(f"[+] YAML format added.\nCurrent formats: {', '.join(self.selected_formats)}")
        else:
            self.selected_formats.remove("yaml")
            self._set_preview(f"[-] YAML format removed.\nCurrent formats: {', '.join(self.selected_formats)}")
    
    @on(Button.Pressed, "#format_all")
    def on_format_all(self):
        self.selected_formats = ["json", "csv", "html", "md", "yaml"]
        self._set_preview(f"[+] All formats selected.\nCurrent formats: {', '.join(self.selected_formats)}")
    
    # ===== INCLUDE DATA =====
    include_data = {"history": True, "config": False, "logs": False}
    
    @on(Button.Pressed, "#include_history")
    def on_include_history(self):
        self.include_data["history"] = not self.include_data["history"]
        status = "✅" if self.include_data["history"] else "❌"
        self._set_preview(f"{status} Scan History: {self.include_data['history']}")
    
    @on(Button.Pressed, "#include_config")
    def on_include_config(self):
        self.include_data["config"] = not self.include_data["config"]
        status = "✅" if self.include_data["config"] else "❌"
        self._set_preview(f"{status} Configuration: {self.include_data['config']}")
    
    @on(Button.Pressed, "#include_logs")
    def on_include_logs(self):
        self.include_data["logs"] = not self.include_data["logs"]
        status = "✅" if self.include_data["logs"] else "❌"
        self._set_preview(f"{status} Logs: {self.include_data['logs']}")
    
    @on(Button.Pressed, "#include_all")
    def on_include_all(self):
        self.include_data = {"history": True, "config": True, "logs": True}
        self._set_preview("✅ All data included: History, Config, Logs")
    
    # ===== GENERATE REPORT =====
    @on(Button.Pressed, "#generate_report")
    async def on_generate_report(self):
        name = self._get_report_name()
        if not self.selected_formats:
            self._set_preview("⚠️ Please select at least one format.")
            return
        
        # Collect data
        data = {
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "report_version": "1.0",
            "generated_by": "Cyber Security Suite Pro 2026",
        }
        
        if self.include_data.get("history", True):
            data["history"] = db.get_scan_history(limit=500)
        if self.include_data.get("config", False):
            data["configs"] = db.get_config("all", {})
        if self.include_data.get("logs", False):
            data["logs"] = db.get_logs(limit=200)
        
        report_path = settings.REPORT_PATH / name
        report_path.mkdir(exist_ok=True)
        
        result = f"📊 Report Generated: {name}\n"
        result += "=" * 50 + "\n\n"
        
        # Generate each format
        for fmt in self.selected_formats:
            try:
                if fmt == "json":
                    path = report_path / f"{name}.json"
                    with open(path, "w") as f:
                        json.dump(data, f, indent=2, default=str)
                    result += f"✅ JSON: {path}\n"
                
                elif fmt == "csv":
                    path = report_path / f"{name}.csv"
                    with open(path, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(["ID", "Type", "Target", "Result", "Status", "Timestamp"])
                        for record in data.get("history", []):
                            writer.writerow([
                                record.get("id", ""),
                                record.get("scan_type", ""),
                                record.get("target", ""),
                                str(record.get("result", ""))[:100],
                                record.get("status", ""),
                                record.get("timestamp", "")
                            ])
                    result += f"✅ CSV: {path}\n"
                
                elif fmt == "html":
                    path = report_path / f"{name}.html"
                    template_str = """
                    <!DOCTYPE html>
                    <html>
                    <head><title>{{ name }}</title>
                    <style>
                        body { font-family: Arial; background: #0a0e17; color: #00ffcc; padding: 20px; }
                        h1 { color: #00ffcc; }
                        table { border-collapse: collapse; width: 100%; }
                        th, td { border: 1px solid #00ffcc; padding: 8px; text-align: left; }
                        th { background: #00ffcc; color: #0a0e17; }
                    </style>
                    </head>
                    <body>
                        <h1>📄 {{ name }}</h1>
                        <p>Generated: {{ timestamp }}</p>
                        <p>Version: {{ report_version }}</p>
                        <h2>Scan History</h2>
                        <table>
                        <tr><th>ID</th><th>Type</th><th>Target</th><th>Status</th><th>Timestamp</th></tr>
                        {% for record in history %}
                        <tr><td>{{ record.id }}</td><td>{{ record.scan_type }}</td><td>{{ record.target }}</td><td>{{ record.status }}</td><td>{{ record.timestamp }}</td></tr>
                        {% endfor %}
                        </table>
                    </body>
                    </html>
                    """
                    template = jinja2.Template(template_str)
                    with open(path, "w") as f:
                        f.write(template.render(data))
                    result += f"✅ HTML: {path}\n"
                
                elif fmt == "md":
                    path = report_path / f"{name}.md"
                    with open(path, "w") as f:
                        f.write(f"# {name}\n\n")
                        f.write(f"**Generated:** {data['timestamp']}\n\n")
                        f.write(f"**Version:** {data['report_version']}\n\n")
                        f.write("## Scan History\n\n")
                        f.write("| ID | Type | Target | Status | Timestamp |\n")
                        f.write("|----|------|--------|--------|-----------|\n")
                        for record in data.get("history", []):
                            f.write(f"| {record.get('id','')} | {record.get('scan_type','')} | {record.get('target','')} | {record.get('status','')} | {record.get('timestamp','')} |\n")
                    result += f"✅ Markdown: {path}\n"
                
                elif fmt == "yaml":
                    path = report_path / f"{name}.yaml"
                    with open(path, "w") as f:
                        yaml.dump(data, f, default_flow_style=False)
                    result += f"✅ YAML: {path}\n"
            
            except Exception as e:
                result += f"❌ {fmt.upper()} error: {str(e)}\n"
        
        # Save to database
        db.add_scan_history("report", name, {"formats": self.selected_formats, "path": str(report_path)})
        
        self._set_preview(result)
        await self._load_history()
    
    # ===== EXPORT FUNCTIONS =====
    @on(Button.Pressed, "#export_pdf")
    def on_export_pdf(self):
        self._set_preview("⚠️ PDF export requires additional libraries (weasyprint). Feature coming soon.")
    
    @on(Button.Pressed, "#export_html")
    def on_export_html(self):
        self._set_preview("📤 Exporting HTML report... Check reports folder.")
    
    @on(Button.Pressed, "#export_json")
    def on_export_json(self):
        self._set_preview("📤 Exporting JSON report... Check reports folder.")
