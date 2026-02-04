
from fasthtml.common import *
import json

# ============================================
# Tabulator Component for FastHTML
# ============================================

def TabulatorHeaders():
    """Include these in your app's hdrs"""
    return (
        Link(rel="stylesheet", href="https://unpkg.com/tabulator-tables@6.2.1/dist/css/tabulator.min.css"),
        Script(src="https://unpkg.com/tabulator-tables@6.2.1/dist/js/tabulator.min.js"),
    )

def TabulatorCol(field, title=None, width=None, min_width=None, max_width=None,
                 sorter=None, formatter=None, formatter_params=None,
                 editor=None, editor_params=None, header_filter=None,
                 hozAlign=None, vertAlign=None, frozen=None, visible=True,
                 css_class=None, tooltip=None, resizable=True):
    """
    Define a Tabulator column.

    Args:
        field: Data field name
        title: Column header title (defaults to field.title())
        width: Fixed column width in px
        min_width: Minimum column width in px
        max_width: Maximum column width in px
        sorter: Sort type - "string", "number", "alphanum", "boolean", "date", "time", "datetime", "array"
        formatter: Display formatter - "plaintext", "textarea", "html", "money", "image", "link",
                   "datetime", "datetimediff", "tickCross", "star", "progress", "color",
                   "buttonTick", "buttonCross", "rownum", "handle"
        formatter_params: Dict of params for formatter (e.g., {"thousand": ",", "precision": 2} for money)
        editor: Editor type - "input", "textarea", "number", "range", "tickCross", "star",
                "list", "date", "time", "datetime"
        editor_params: Dict of params for editor (e.g., {"values": ["a", "b", "c"]} for list)
        header_filter: Enable header filtering - True, "input", "number", "list", "tickCross"
        hozAlign: Horizontal align - "left", "center", "right"
        vertAlign: Vertical align - "top", "middle", "bottom"
        frozen: Freeze column - "left" or "right"
        visible: Column visibility (default True)
        css_class: CSS class for column cells
        tooltip: Show tooltip on hover - True or custom string
        resizable: Allow column resize (default True)
    """
    col = {"field": field, "title": title or field.title()}
    if width: col["width"] = width
    if min_width: col["minWidth"] = min_width
    if max_width: col["maxWidth"] = max_width
    if sorter: col["sorter"] = sorter
    if formatter: col["formatter"] = formatter
    if formatter_params: col["formatterParams"] = formatter_params
    if editor: col["editor"] = editor
    if editor_params: col["editorParams"] = editor_params
    if header_filter: col["headerFilter"] = header_filter
    if hozAlign: col["hozAlign"] = hozAlign
    if vertAlign: col["vertAlign"] = vertAlign
    if frozen: col["frozen"] = frozen
    if not visible: col["visible"] = False
    if css_class: col["cssClass"] = css_class
    if tooltip: col["tooltip"] = tooltip
    if not resizable: col["resizable"] = False
    return col

def Tabulator(id, columns, ajax_url=None, data=None, height="500px", pagination=True,
              page_size=25, sort_by=None, sort_dir="desc", auto_refresh=None):
    """
    Create a Tabulator table component.

    Args:
        id: Element ID for the table
        columns: List of TabulatorCol definitions
        ajax_url: URL to fetch data from
        data: Inline data (if not using ajax_url)
        height: Table height
        pagination: Enable pagination
        page_size: Rows per page
        sort_by: Column field to sort by initially
        sort_dir: Sort direction ("asc" or "desc")
        auto_refresh: Auto-refresh interval in ms (None to disable)
    """
    config = {
        "layout": "fitDataStretch",
        "height": height,
        "columns": columns,
        "movableColumns": True,
    }

    if ajax_url:
        config["ajaxURL"] = ajax_url
    if data:
        config["data"] = data
    if pagination:
        config["pagination"] = "local"
        config["paginationSize"] = page_size
    if sort_by:
        config["initialSort"] = [{"column": sort_by, "dir": sort_dir}]

    var_name = f"tabulator_{id}"

    init_js = f"""
    var {var_name};
    var {var_name}_interval = null;

    document.addEventListener('DOMContentLoaded', function() {{
        {var_name} = new Tabulator("#{id}", {json.dumps(config)});
        {"startAutoRefresh_" + id + f"({auto_refresh});" if auto_refresh else ""}
    }});

    function refreshData_{id}() {{
        fetch("{ajax_url}")
            .then(response => response.json())
            .then(data => {var_name}.replaceData(data));
    }}

    function startAutoRefresh_{id}(interval) {{
        stopAutoRefresh_{id}();
        {var_name}_interval = setInterval(refreshData_{id}, interval);
        var status = document.getElementById('{id}-auto-status');
        if (status) status.textContent = 'Auto-refresh: ON (' + (interval/1000) + 's)';
    }}

    function stopAutoRefresh_{id}() {{
        if ({var_name}_interval) {{
            clearInterval({var_name}_interval);
            {var_name}_interval = null;
        }}
        var status = document.getElementById('{id}-auto-status');
        if (status) status.textContent = 'Auto-refresh: OFF';
    }}

    function toggleAutoRefresh_{id}(interval) {{
        if ({var_name}_interval) {{
            stopAutoRefresh_{id}();
        }} else {{
            startAutoRefresh_{id}(interval || 2000);
        }}
    }}
    """

    return Div(id=id), Script(init_js)


def TabulatorControls(id, intervals=[1, 2, 5, 10], default=2):
    """Auto-refresh controls for a Tabulator table"""
    return Div(
        Button("Refresh Now", onclick=f"refreshData_{id}()"),
        Button("Toggle Auto", onclick=f"toggleAutoRefresh_{id}(document.getElementById('{id}-interval').value * 1000)"),
        Select(
            *[Option(f"{i} second{'s' if i > 1 else ''}", value=str(i), selected=(i == default)) for i in intervals],
            id=f"{id}-interval",
            onchange=f"if({id}_interval) startAutoRefresh_{id}(this.value * 1000)"
        ),
        Span(id=f"{id}-auto-status", style="margin-left: 10px; font-weight: bold;"),
        style="margin-bottom: 10px; display: flex; gap: 10px; align-items: center;"
    )