# ToolHub

ToolHub is a desktop app (Python + Tkinter) to manage web tools in one place.

It helps you store and operate:
- Tool name
- Owner email
- Website URL
- GitHub URL
- Firebase Console URL
- Project path on local PC
- Run file for each project

## Main features

- Add, edit, delete tool rows
- Search by tool name
- Filter by email (dropdown)
- Open Website / GitHub / Firebase from selected row
- Open local project folder
- Run project file from selected row
- SEO check: open Google search `site:<website_url>`
- Quick MoneTag button (header)

## Requirements

- Windows
- Python 3.10+ (recommended)

## Run the app

From `ToolHub` folder:

```bat
run_hub.cmd
```

Or directly:

```bat
python hub.py
```

## Create shortcuts (Desktop + Start Menu)

Use:

```bat
create_shortcut.cmd
```

Notes:
- Script uses dynamic paths (`%~dp0`), so it works after cloning to another machine/location.
- Shortcut icon is loaded from `toolhub.ico` in the same folder.

## Data file

Data is stored in:

- `tools_data.json`

Each item format:

```json
{
  "name": "Example Tool",
  "email": "owner@example.com",
  "website_url": "https://example.com",
  "github_url": "https://github.com/example/repo",
  "firebase_console_url": "https://console.firebase.google.com",
  "project_path": "D:\\Projects\\ExampleTool",
  "run_file": "run_hub.cmd"
}
```

## UI shortcuts

- `Ctrl+F`: focus search box
- `F5`: reload data
- Double-click table row: edit

## SEO check behavior

`SEO` button in Actions opens:

- `https://www.google.com/search?q=site:<website_url>`

based on selected row.

## Troubleshooting

- If taskbar grouping/icon looks wrong:
  - close all ToolHub windows
  - open again from shortcut
  - unpin old icon and pin the running ToolHub icon again

- If Run does not work:
  - verify `project_path` and `run_file`
  - if `run_file` is relative, it is resolved from `project_path`

## Key files

- `hub.py`: main desktop app
- `run_hub.cmd`: app launcher
- `create_shortcut.cmd`: create shortcuts
- `toolhub.ico`: app icon
- `tools_data.json`: saved tools
