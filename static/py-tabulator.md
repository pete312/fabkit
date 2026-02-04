## Tabulator as a Python Component

A FastHTML wrapper for [Tabulator.js](https://tabulator.info/).

---

## Setup

Include the headers in your app:

```python
from fabkit.fk_tabulator import TabulatorHeaders, TabulatorCol, Tabulator, TabulatorControls

app, rt = fast_app(hdrs=TabulatorHeaders())
```

---

## Tabulator

Create a table component.

### Args

| Arg | Type | Description |
|-----|------|-------------|
| `id` | str | Element ID for the table |
| `columns` | list | List of TabulatorCol definitions |
| `ajax_url` | str | URL to fetch JSON data from |
| `data` | list | Inline data (if not using ajax_url) |
| `height` | str | Table height (default "500px") |
| `pagination` | bool | Enable pagination (default True) |
| `page_size` | int | Rows per page (default 25) |
| `sort_by` | str | Column field to sort by initially |
| `sort_dir` | str | Sort direction - "asc" or "desc" |
| `auto_refresh` | int | Auto-refresh interval in ms (None to disable) |

---

## TabulatorCol

Define a column.

### Args

| Arg | Type | Description |
|-----|------|-------------|
| `field` | str | Data field name |
| `title` | str | Column header (defaults to field.title()) |
| `width` | int | Fixed width in px |
| `min_width` | int | Minimum width in px |
| `max_width` | int | Maximum width in px |
| `sorter` | str | Sort type |
| `formatter` | str | Display formatter |
| `formatter_params` | dict | Formatter options |
| `editor` | str | Inline editor type |
| `editor_params` | dict | Editor options |
| `header_filter` | bool/str | Enable header filtering |
| `hozAlign` | str | Horizontal align - "left", "center", "right" |
| `vertAlign` | str | Vertical align - "top", "middle", "bottom" |
| `frozen` | str | Freeze column - "left" or "right" |
| `visible` | bool | Column visibility (default True) |
| `css_class` | str | CSS class for cells |
| `tooltip` | bool/str | Show tooltip on hover |
| `resizable` | bool | Allow resize (default True) |

### Sorters

`"string"`, `"number"`, `"alphanum"`, `"boolean"`, `"date"`, `"time"`, `"datetime"`, `"array"`

### Formatters

| Formatter | Description |
|-----------|-------------|
| `"plaintext"` | Default text |
| `"textarea"` | Multiline text |
| `"html"` | Render HTML |
| `"money"` | Currency (use `formatter_params={"symbol": "$", "precision": 2}`) |
| `"image"` | Image from URL |
| `"link"` | Clickable link |
| `"datetime"` | Formatted date/time |
| `"datetimediff"` | Relative time ("3 hours ago") |
| `"tickCross"` | Checkmark/X for booleans |
| `"star"` | Star rating |
| `"progress"` | Progress bar (use `formatter_params={"max": 100}`) |
| `"color"` | Color swatch |
| `"rownum"` | Row number |
| `"handle"` | Drag handle |

### Editors

| Editor | Description |
|--------|-------------|
| `"input"` | Text input |
| `"textarea"` | Multiline input |
| `"number"` | Number input |
| `"range"` | Slider |
| `"tickCross"` | Checkbox |
| `"star"` | Star rating |
| `"list"` | Dropdown (use `editor_params={"values": ["a", "b", "c"]}`) |
| `"date"` | Date picker |
| `"time"` | Time picker |
| `"datetime"` | DateTime picker |

---

## TabulatorControls

Add refresh controls for a table.

```python
TabulatorControls("my-table", intervals=[1, 2, 5, 10], default=2)
```

---

## Example

```python
from fasthtml.common import *
from fastapi import FastAPI
from fabkit.fk_tabulator import TabulatorHeaders, TabulatorCol, Tabulator, TabulatorControls

app, rt = fast_app(hdrs=TabulatorHeaders())
api = FastAPI()

@api.get("/data")
def get_data():
    return [
        {"id": 1, "name": "Alice", "score": 85, "active": True},
        {"id": 2, "name": "Bob", "score": 92, "active": False},
    ]

app.mount("/api", api)

@rt
def index():
    columns = [
        TabulatorCol("id", "ID", width=60, sorter="number"),
        TabulatorCol("name", "Name", sorter="string", editor="input"),
        TabulatorCol("score", "Score", sorter="number",
                     formatter="progress", formatter_params={"max": 100}),
        TabulatorCol("active", "Active", formatter="tickCross", editor="tickCross"),
    ]

    return Titled("My Table",
        TabulatorControls("data"),
        Tabulator("data", columns, ajax_url="/api/data", sort_by="score", auto_refresh=5000),
    )

serve()
```
