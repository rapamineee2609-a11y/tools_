cat > ui/screens/reports.py << 'EOF'
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Button, Input, TextArea, DataTable
from textual.widgets.dropdown import Dropdown
from textual import on
import json
import csv
import yaml
import jinja2
from datetime import datetime
from pathlib import Path
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
    }
    """
    def compose(self):
        yield Container(
            Static("📄 Report Generator", classes="title"),
            Container(
                Label("Report Name:"),
                Input(placeholder="scan_report_2026", id="report_name"),
                Label("Format:"),
                Horizontal(
                    Button("JSON", id="report_json"),
                    Button("CSV", id="report_csv"),
                    Button("HTML", id="report_html"),
                    Button("Markdown", id="report_md"),
                    Button("YAML", id="report_yaml"),
                ),
                Button("Generate Report", id="generate_report"),
                TextArea(id="report_result", classes="result-box", read_only=True),
                id="report-container"
            ),
            DataTable(id="report_history_table")
        )
    async def on_mount(self):
        await self._load_history()
    async def _load_history(self):
        table = self.query_one("#report_history_table")
        table.clear()
        table.add_columns("ID", "Name", "Format", "Created")
        reports = db.get_scan_history(limit=10)
        for record in reports:
            if record.get("scan_type") == "report":
                table.add_row(
                    str(record["id"]),
                    record["target"],
                    record["scan_type"],
                    record["timestamp"][:19]
                )
    @on(Button.Pressed, "#generate_report")
    async def on_generate_report(self):
        name = self.query_one("#report_name").value.strip()
        if not name:
            name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        data = {
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "history": db.get_scan_history(limit=100),
            "configs": db.get_config("all", {})
        }
        result = "Generated Reports:\n" + "=" * 40 + "\n"
        # JSON
        json_path = settings.REPORT_PATH / f"{name}.json"
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        result += f"✅ JSON: {json_path}\n"
        # CSV
        csv_path = settings.REPORT_PATH / f"{name}.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Type", "Target", "Result", "Status", "Timestamp"])
            for record in data["history"]:
                writer.writerow([
                    record.get("id", ""),
                    record.get("scan_type", ""),
                    record.get("target", ""),
                    str(record.get("result", ""))[:100],
                    record.get("status", ""),
                    record.get("timestamp", "")
                ])
        result += f"✅ CSV: {csv_path}\n"
        # HTML
        html_path = settings.REPORT_PATH / f"{name}.html"
        html_template = """
        <html><head><title>{{ name }}</title></head>
        <body><h1>{{ name }}</h1><p>Generated: {{ timestamp }}</p>
        <h2>Scan History</h2><table border="1">
        <tr><th>ID</th><th>Type</th><th>Target</th><th>Status</th><th>Timestamp</th></tr>
        {% for record in history %}
        <tr><td>{{ record.id }}</td><td>{{ record.scan_type }}</td><td>{{ record.target }}</td><td>{{ record.status }}</td><td>{{ record.timestamp }}</td></tr>
        {% endfor %}</table></body></html>
        """
        template = jinja2.Template(html_template)
        with open(html_path, "w") as f:
            f.write(template.render(data))
        result += f"✅ HTML: {html_path}\n"
        # Markdown
        md_path = settings.REPORT_PATH / f"{name}.md"
        with open(md_path, "w") as f:
            f.write(f"# {name}\n\nGenerated: {data['timestamp']}\n\n## Scan History\n\n| ID | Type | Target | Status | Timestamp |\n|----|------|--------|--------|-----------|\n")
            for record in data["history"]:
                f.write(f"| {record.get('id','')} | {record.get('scan_type','')} | {record.get('target','')} | {record.get('status','')} | {record.get('timestamp','')} |\n")
        result += f"✅ Markdown: {md_path}\n"
        self.query_one("#report_result").text = result
        db.add_scan_history("report", name, {"formats": ["json", "csv", "html", "md"]})
EOF
