#!/bin/env -S pyboots --http http://PVE/fasthtml/requirements.txt  --require 3.12 --rebuild-on-changes

from fasthtml.common import *
from fastapi import FastAPI
from pathlib import Path
import subprocess

from fabkit.fk_tabulator import TabulatorHeaders, TabulatorCol, Tabulator, TabulatorControls


def MarkdownHeaders():
    """Headers for markdown rendering with GitHub styling"""
    return (
        Script(src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"),
        Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown.min.css"),
        Style("""
            .markdown-body {
                box-sizing: border-box;
                min-width: 200px;
                max-width: 980px;
                margin: 0 auto;
                padding: 45px;
            }
            @media (max-width: 767px) {
                .markdown-body { padding: 15px; }
            }
        """),
        Script("""
            document.addEventListener('DOMContentLoaded', function() {
                document.querySelectorAll('.marked').forEach(el => {
                    el.innerHTML = marked.parse(el.textContent);
                    el.classList.add('markdown-body');
                });
            });
        """),
    )


# ============================================
# App
# ============================================

app, rt = fast_app(hdrs=(*TabulatorHeaders(), *MarkdownHeaders()))

api = FastAPI()

def get_process_list():
    result = subprocess.run(["ps", "aux", "--no-headers"], capture_output=True, text=True)
    processes = []
    for line in result.stdout.strip().split('\n'):
        parts = line.split(None, 10)
        if len(parts) >= 11:
            processes.append({
                "user": parts[0],
                "pid": int(parts[1]),
                "cpu": float(parts[2]),
                "mem": float(parts[3]),
                "vsz": int(parts[4]),
                "rss": int(parts[5]),
                "tty": parts[6],
                "stat": parts[7],
                "start": parts[8],
                "time": parts[9],
                "command": parts[10],
            })
    return processes

@api.get("/processes")
def api_processes():
    return get_process_list()

app.mount("/api", api)

STATIC_DIR = Path(__file__).parent / "static"

@rt("/md/{fname:path}")
def get(fname: str):
    """Serve markdown files as rendered HTML"""
    md_path = STATIC_DIR / fname
    if not md_path.suffix:
        md_path = md_path.with_suffix(".md")
    if not md_path.exists() or not md_path.is_file():
        return Titled("Not Found", P(f"File not found: {fname}"))
    content = md_path.read_text()
    return Titled(fname, Div(content, cls="marked"))

@rt
def index():
    columns = [
        TabulatorCol("pid", "PID", width=80, sorter="number"),
        TabulatorCol("user", "User", width=100, sorter="string"),
        TabulatorCol("cpu", "CPU %", width=80, sorter="number"),
        TabulatorCol("mem", "Mem %", width=80, sorter="number"),
        TabulatorCol("vsz", "VSZ", width=90, sorter="number"),
        TabulatorCol("rss", "RSS", width=90, sorter="number"),
        TabulatorCol("tty", "TTY", width=80),
        TabulatorCol("stat", "Stat", width=60),
        TabulatorCol("start", "Start", width=80),
        TabulatorCol("time", "Time", width=80),
        TabulatorCol("command", "Command", min_width=200),
    ]

    return Titled("Process Monitor",
        H2("System Process List",  A(" see info..", href='/md/py-tabulator.md'),),
        P("Click column headers to sort. Drag to reorder columns."),
        TabulatorControls("procs"),
        Tabulator("procs", columns, ajax_url="/api/processes", sort_by="cpu", auto_refresh=2000),
    )

serve()
