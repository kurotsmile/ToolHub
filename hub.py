import argparse
import ctypes
import json
import os
import socket
import subprocess
import tkinter as tk
import webbrowser
from dataclasses import asdict, dataclass
from tkinter import filedialog, messagebox, ttk
from typing import List
from urllib.parse import quote_plus


DEFAULT_DATA_FILE = "tools_data.json"
APP_USER_MODEL_ID = "ToolHub.DesktopApp"


@dataclass
class ToolEntry:
    name: str
    email: str = ""
    website_url: str = ""
    github_url: str = ""
    firebase_console_url: str = ""
    project_path: str = ""


class ToolHubApp:
    def __init__(self, root: tk.Tk, data_file: str):
        self.root = root
        self.data_file = data_file
        self.entries: List[ToolEntry] = []
        self.visible_indices: List[int] = []
        self.search_var = tk.StringVar(value="")
        self.email_filter_var = tk.StringVar(value="All emails")
        self.status_var = tk.StringVar(value="Ready")

        self.root.title("ToolHub")
        self.root.geometry("1260x720")
        self.root.minsize(980, 580)

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toolhub.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        self._apply_theme()
        self._build_ui()
        self.load_entries()
        self.refresh_table()

        self.root.bind("<Control-f>", self._focus_search)
        self.root.bind("<F5>", lambda _event: self.reload_entries())

    def _apply_theme(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self.root.configure(bg="#EEF4FB")
        self.tree_header_bg = "#EAF2FC"
        self.tree_header_border = "#C9D9EC"
        self.card_border = "#D6E3F2"
        self.scroll_trough = "#ECF3FB"
        self.scroll_thumb = "#C4D7EE"
        self.scroll_thumb_active = "#AFC9E7"
        self.button_bg = "#EAF2FC"
        self.button_hover = "#DDEAFB"
        self.button_border = "#C4D7EE"
        self.combo_bg = "#F8FBFF"
        self.combo_border = "#C4D7EE"
        self.entry_bg = "#F8FBFF"
        style.configure("App.TFrame", background="#EEF4FB")
        style.configure(
            "Card.TFrame",
            background="#FFFFFF",
            relief="solid",
            borderwidth=1,
            bordercolor=self.card_border,
            lightcolor=self.card_border,
            darkcolor=self.card_border,
        )
        style.configure(
            "Toolbar.TLabelframe",
            background="#F7FAFE",
            borderwidth=1,
            relief="solid",
            bordercolor=self.card_border,
            lightcolor=self.card_border,
            darkcolor=self.card_border,
        )
        style.configure("Toolbar.TLabelframe.Label", background="#F7FAFE", foreground="#4F6480", font=("Segoe UI Semibold", 8))
        style.configure("Toolbar.TLabel", background="#F7FAFE", foreground="#244161", font=("Segoe UI", 9))
        style.configure("Dialog.TLabel", background="#FFFFFF", foreground="#28415F", font=("Segoe UI", 9))
        style.configure("DialogTitle.TLabel", background="#FFFFFF", foreground="#183A63", font=("Segoe UI Semibold", 11))
        style.configure("HeaderTitle.TLabel", background="#DCEBFA", foreground="#183A63", font=("Georgia", 16, "bold"))
        style.configure("HeaderSub.TLabel", background="#DCEBFA", foreground="#4D6787", font=("Segoe UI", 9))
        style.configure("Hint.TLabel", background="#EEF4FB", foreground="#667B95", font=("Segoe UI", 9))
        style.configure("CardTitle.TLabel", background="#FFFFFF", foreground="#183A63", font=("Segoe UI Semibold", 10))
        style.configure(
            "TButton",
            font=("Segoe UI", 9),
            padding=(9, 5),
            background=self.button_bg,
            foreground="#244161",
            bordercolor=self.button_border,
            lightcolor=self.button_border,
            darkcolor=self.button_border,
        )
        style.map("TButton", background=[("active", self.button_hover)])
        style.configure("Accent.TButton", font=("Segoe UI Semibold", 9), padding=(10, 5), foreground="#FFFFFF", background="#2F7BD9", bordercolor="#2A6FC3")
        style.map("Accent.TButton", background=[("active", "#286EC4")])
        style.configure("Success.TButton", font=("Segoe UI Semibold", 9), padding=(10, 5), foreground="#FFFFFF", background="#1FA971", bordercolor="#198B5D")
        style.map("Success.TButton", background=[("active", "#189A66")])
        style.configure("Danger.TButton", font=("Segoe UI Semibold", 9), padding=(10, 5), foreground="#FFFFFF", background="#D9534F", bordercolor="#C84642")
        style.map("Danger.TButton", background=[("active", "#C94744")])
        style.configure("Header.TButton", font=("Segoe UI Semibold", 9), padding=(10, 5), foreground="#183A63", background="#D5E5F8", bordercolor="#BDD2EC")
        style.map("Header.TButton", background=[("active", "#C7DCF5")])
        style.configure(
            "TEntry",
            font=("Segoe UI", 9),
            padding=6,
            fieldbackground=self.entry_bg,
            foreground="#244161",
            bordercolor=self.combo_border,
            lightcolor=self.combo_border,
            darkcolor=self.combo_border,
        )
        style.configure(
            "TCombobox",
            font=("Segoe UI", 9),
            padding=4,
            fieldbackground=self.combo_bg,
            background=self.combo_bg,
            foreground="#244161",
            bordercolor=self.combo_border,
            lightcolor=self.combo_border,
            darkcolor=self.combo_border,
            arrowcolor="#56718F",
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.combo_bg), ("focus", "#FFFFFF")],
            background=[("readonly", self.combo_bg), ("focus", "#FFFFFF")],
            bordercolor=[("focus", "#AFC9E7")],
            lightcolor=[("focus", "#AFC9E7")],
            darkcolor=[("focus", "#AFC9E7")],
            arrowcolor=[("active", "#3E5D80")],
        )
        style.configure(
            "Treeview",
            rowheight=28,
            font=("Segoe UI", 9),
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            bordercolor=self.card_border,
            lightcolor=self.card_border,
            darkcolor=self.card_border,
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI Semibold", 8),
            padding=(8, 6),
            background=self.tree_header_bg,
            foreground="#244161",
            bordercolor=self.tree_header_border,
            lightcolor=self.tree_header_border,
            darkcolor=self.tree_header_border,
            relief="flat",
        )
        style.map("Treeview", background=[("selected", "#DCEBFA")], foreground=[("selected", "#183A63")])
        style.map("Treeview.Heading", background=[("active", "#E2ECF9")])
        style.configure(
            "App.Vertical.TScrollbar",
            background=self.scroll_thumb,
            troughcolor=self.scroll_trough,
            bordercolor=self.scroll_trough,
            arrowcolor="#56718F",
            width=14,
        )
        style.configure(
            "App.Horizontal.TScrollbar",
            background=self.scroll_thumb,
            troughcolor=self.scroll_trough,
            bordercolor=self.scroll_trough,
            arrowcolor="#56718F",
        )
        style.map("App.Vertical.TScrollbar", background=[("active", self.scroll_thumb_active)])
        style.map("App.Horizontal.TScrollbar", background=[("active", self.scroll_thumb_active)])

    def _build_ui(self) -> None:
        root = ttk.Frame(self.root, style="App.TFrame", padding=14)
        root.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(root, style="Card.TFrame", padding=14)
        header.pack(fill=tk.X)
        header_inner = tk.Frame(header, bg="#DCEBFA", padx=16, pady=14)
        header_inner.pack(fill=tk.X)
        ttk.Label(header_inner, text="ToolHub", style="HeaderTitle.TLabel").pack(side=tk.LEFT)
        ttk.Button(header_inner, text="MoneTag", style="Header.TButton", command=self.open_monetag_statistics).pack(side=tk.RIGHT)
        ttk.Label(
            header_inner,
            text="Manage project links, local paths, quick SEO checks, and local preview runs from one place.",
            style="HeaderSub.TLabel",
        ).pack(anchor=tk.W, side=tk.LEFT, padx=(18, 0))

        top = ttk.Frame(root, style="App.TFrame", padding=(0, 12, 0, 0))
        top.pack(fill=tk.X)

        manage = ttk.LabelFrame(top, text="Manage", style="Toolbar.TLabelframe", padding=(12, 10))
        manage.pack(side=tk.LEFT)
        ttk.Button(manage, text="Add", style="Accent.TButton", command=self.add_entry).pack(side=tk.LEFT, padx=3)
        ttk.Button(manage, text="Edit", command=self.edit_entry).pack(side=tk.LEFT, padx=3)
        ttk.Button(manage, text="Delete", style="Danger.TButton", command=self.delete_entry).pack(side=tk.LEFT, padx=3)
        ttk.Button(manage, text="Reload", command=self.reload_entries).pack(side=tk.LEFT, padx=3)

        actions = ttk.LabelFrame(top, text="Actions", style="Toolbar.TLabelframe", padding=(12, 10))
        actions.pack(side=tk.RIGHT)
        ttk.Button(actions, text="Run", style="Success.TButton", command=self.run_selected_tool).pack(side=tk.LEFT, padx=3)
        ttk.Button(actions, text="Open Folder", command=self.open_selected_project_folder).pack(side=tk.LEFT, padx=3)
        ttk.Button(actions, text="Website", command=self.open_selected_website).pack(side=tk.LEFT, padx=3)
        ttk.Button(actions, text="SEO", command=self.open_selected_seo_check).pack(side=tk.LEFT, padx=3)
        ttk.Button(actions, text="GitHub", command=self.open_selected_github).pack(side=tk.LEFT, padx=3)
        ttk.Button(actions, text="Firebase", command=self.open_selected_firebase).pack(side=tk.LEFT, padx=3)

        search = ttk.LabelFrame(root, text="Search", style="Toolbar.TLabelframe", padding=(12, 10))
        search.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(search, text="Tool Name:", style="Toolbar.TLabel").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search, textvariable=self.search_var, width=32)
        self.search_entry.pack(side=tk.LEFT, padx=(6, 10), fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", lambda _event: self.refresh_table())
        ttk.Label(search, text="Email:", style="Toolbar.TLabel").pack(side=tk.LEFT)
        self.email_filter_combo = ttk.Combobox(search, textvariable=self.email_filter_var, state="readonly", width=24, values=["All emails"])
        self.email_filter_combo.pack(side=tk.LEFT, padx=(6, 10))
        self.email_filter_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_table())
        ttk.Button(search, text="Clear", command=self.clear_search).pack(side=tk.LEFT)

        table_card = ttk.Frame(root, style="Card.TFrame", padding=(14, 12))
        table_card.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
        ttk.Label(table_card, text="Project List", style="CardTitle.TLabel").pack(anchor=tk.W, pady=(0, 10))

        table_wrap = ttk.Frame(table_card, style="Card.TFrame")
        table_wrap.pack(fill=tk.BOTH, expand=True)
        columns = ("name", "email", "website_url", "github_url", "firebase_console_url", "project_path")
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings", selectmode="browse")
        for column, heading, width in (
            ("name", "Tool Name", 180),
            ("email", "Email", 220),
            ("website_url", "Website URL", 220),
            ("github_url", "GitHub URL", 220),
            ("firebase_console_url", "Firebase Console URL", 240),
            ("project_path", "Project Path", 360),
        ):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor=tk.W)
        y_scroll = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, style="App.Vertical.TScrollbar", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_wrap, orient=tk.HORIZONTAL, style="App.Horizontal.TScrollbar", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)
        self.tree.bind("<Double-1>", lambda _event: self.edit_entry())
        self.tree.bind("<<TreeviewSelect>>", lambda _event: self._update_status())

        footer = ttk.Frame(root, style="App.TFrame", padding=(0, 10, 0, 0))
        footer.pack(fill=tk.X)
        ttk.Label(footer, text="Ctrl+F search | F5 reload", style="Hint.TLabel").pack(side=tk.LEFT)
        ttk.Label(footer, textvariable=self.status_var, style="Hint.TLabel").pack(side=tk.RIGHT)

    def load_entries(self) -> None:
        if not os.path.exists(self.data_file):
            self.entries = []
            self.save_entries()
            return
        with open(self.data_file, "r", encoding="utf-8-sig") as f:
            raw = json.load(f)
        self.entries = []
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    self.entries.append(
                        ToolEntry(
                            name=str(item.get("name", "")).strip(),
                            email=str(item.get("email", "")).strip(),
                            website_url=str(item.get("website_url", "")).strip(),
                            github_url=str(item.get("github_url", "")).strip(),
                            firebase_console_url=str(item.get("firebase_console_url", "")).strip(),
                            project_path=str(item.get("project_path", "")).strip(),
                        )
                    )

    def save_entries(self) -> None:
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump([asdict(entry) for entry in self.entries], f, ensure_ascii=False, indent=2)

    def refresh_table(self) -> None:
        selected_before = self._selected_index()
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._refresh_email_filter_options()
        keyword = self.search_var.get().strip().lower()
        email_filter = self.email_filter_var.get().strip().lower()
        self.visible_indices = []
        for idx, entry in enumerate(self.entries):
            if keyword and keyword not in entry.name.lower():
                continue
            if email_filter != "all emails" and email_filter and entry.email.lower() != email_filter:
                continue
            self.visible_indices.append(idx)
        for view_idx, idx in enumerate(self.visible_indices):
            entry = self.entries[idx]
            self.tree.insert("", tk.END, iid=str(view_idx), values=(entry.name, entry.email, entry.website_url, entry.github_url, entry.firebase_console_url, entry.project_path))
        if selected_before is not None and selected_before in self.visible_indices:
            self.tree.selection_set(str(self.visible_indices.index(selected_before)))
        self._update_status()

    def reload_entries(self) -> None:
        self.load_entries()
        self.refresh_table()
        self.status_var.set("Reloaded data")

    def _selected_index(self):
        selected = self.tree.selection()
        if not selected:
            return None
        try:
            view_idx = int(selected[0])
        except ValueError:
            return None
        if view_idx < 0 or view_idx >= len(self.visible_indices):
            return None
        return self.visible_indices[view_idx]

    def _selected_entry(self) -> ToolEntry | None:
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Select row", "Please select a row first.")
            return None
        return self.entries[idx]

    def _focus_search(self, _event=None):
        self.search_entry.focus_set()
        self.search_entry.selection_range(0, tk.END)
        return "break"

    def clear_search(self) -> None:
        self.search_var.set("")
        self.email_filter_var.set("All emails")
        self.refresh_table()

    def _refresh_email_filter_options(self) -> None:
        current = self.email_filter_var.get().strip() or "All emails"
        options = ["All emails"] + sorted({entry.email.strip() for entry in self.entries if entry.email.strip()}, key=str.lower)
        self.email_filter_combo["values"] = options
        self.email_filter_var.set(current if current in options else "All emails")

    def _update_status(self) -> None:
        total = len(self.entries)
        visible = len(self.visible_indices)
        idx = self._selected_index()
        self.status_var.set(f"Showing {visible}/{total} tool(s)" if idx is None else f"Showing {visible}/{total} tool(s) | Selected: {self.entries[idx].name}")

    def _entry_dialog(self, title: str, default: ToolEntry | None = None) -> ToolEntry | None:
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.configure(bg="#EEF4FB")
        dialog.transient(self.root)
        dialog.grab_set()
        vars_map = {
            "name": tk.StringVar(value=(default.name if default else "")),
            "email": tk.StringVar(value=(default.email if default else "")),
            "website_url": tk.StringVar(value=(default.website_url if default else "")),
            "github_url": tk.StringVar(value=(default.github_url if default else "")),
            "firebase_console_url": tk.StringVar(value=(default.firebase_console_url if default else "")),
            "project_path": tk.StringVar(value=(default.project_path if default else "")),
        }
        outer = ttk.Frame(dialog, style="App.TFrame", padding=12)
        outer.grid(row=0, column=0, sticky="nsew")
        form = ttk.Frame(outer, style="Card.TFrame", padding=14)
        form.grid(row=0, column=0, sticky="nsew")
        ttk.Label(form, text=title, style="DialogTitle.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        email_values = sorted({entry.email.strip() for entry in self.entries if entry.email.strip()}, key=str.lower)
        labels = [("Tool Name*", "name"), ("Email", "email"), ("Website URL", "website_url"), ("GitHub URL", "github_url"), ("Firebase Console URL", "firebase_console_url"), ("Project Path", "project_path")]
        for row_idx, (label, key) in enumerate(labels, start=1):
            ttk.Label(form, text=label, style="Dialog.TLabel").grid(row=row_idx, column=0, sticky="w", pady=5)
            widget = ttk.Combobox(form, textvariable=vars_map[key], values=email_values, width=76) if key == "email" else ttk.Entry(form, textvariable=vars_map[key], width=78)
            widget.grid(row=row_idx, column=1, sticky="ew", padx=(8, 0), pady=5)
            if key == "project_path":
                ttk.Button(form, text="Browse Folder", command=lambda v=vars_map["project_path"]: self._browse_folder(v, dialog)).grid(row=row_idx, column=2, padx=(8, 0), pady=5)
            if row_idx == 0:
                widget.focus_set()
        form.columnconfigure(1, weight=1)
        result = {"value": None}

        def on_ok() -> None:
            name = vars_map["name"].get().strip()
            if not name:
                messagebox.showwarning("Validation", "Tool name is required.", parent=dialog)
                return
            result["value"] = ToolEntry(
                name=name,
                email=vars_map["email"].get().strip(),
                website_url=vars_map["website_url"].get().strip(),
                github_url=vars_map["github_url"].get().strip(),
                firebase_console_url=vars_map["firebase_console_url"].get().strip(),
                project_path=vars_map["project_path"].get().strip(),
            )
            dialog.destroy()

        buttons = ttk.Frame(form, style="Card.TFrame")
        buttons.grid(row=len(labels) + 1, column=1, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(buttons, text="Save", command=on_ok).pack(side=tk.RIGHT)
        dialog.wait_window()
        return result["value"]

    def _browse_folder(self, target_var: tk.StringVar, parent: tk.Toplevel) -> None:
        selected = filedialog.askdirectory(parent=parent, title="Select project folder")
        if selected:
            target_var.set(selected)

    def add_entry(self) -> None:
        created = self._entry_dialog("Add Tool")
        if created:
            self.entries.append(created)
            self.save_entries()
            self.refresh_table()

    def edit_entry(self) -> None:
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Select row", "Please select a row to edit.")
            return
        updated = self._entry_dialog("Edit Tool", self.entries[idx])
        if updated:
            self.entries[idx] = updated
            self.save_entries()
            self.refresh_table()

    def delete_entry(self) -> None:
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Select row", "Please select a row to delete.")
            return
        entry = self.entries[idx]
        if messagebox.askyesno("Confirm delete", f"Delete '{entry.name}'?"):
            del self.entries[idx]
            self.save_entries()
            self.refresh_table()

    def _open_url(self, label: str, url: str) -> None:
        url = (url or "").strip()
        if not url:
            messagebox.showinfo("Missing URL", f"Selected tool has no {label} URL.")
            return
        webbrowser.open_new_tab(url)
        self.status_var.set(f"Opened {label}")

    def open_selected_website(self) -> None:
        entry = self._selected_entry()
        if entry:
            self._open_url("website", entry.website_url)

    def open_selected_github(self) -> None:
        entry = self._selected_entry()
        if entry:
            self._open_url("GitHub", entry.github_url)

    def open_selected_firebase(self) -> None:
        entry = self._selected_entry()
        if entry:
            self._open_url("Firebase Console", entry.firebase_console_url)

    def open_selected_seo_check(self) -> None:
        entry = self._selected_entry()
        if not entry:
            return
        website_url = (entry.website_url or "").strip()
        if not website_url:
            messagebox.showinfo("Missing URL", "Selected tool has no Website URL.")
            return
        webbrowser.open_new_tab(f"https://www.google.com/search?q={quote_plus(f'site:{website_url}')}")
        self.status_var.set("Opened SEO check")

    def open_monetag_statistics(self) -> None:
        self._open_url("MoneTag Statistics", "https://publishers.monetag.com/statistics")

    def open_selected_project_folder(self) -> None:
        entry = self._selected_entry()
        if not entry:
            return
        target = self._normalize_project_path(entry.project_path)
        if not target:
            return
        try:
            os.startfile(target)  # type: ignore[attr-defined]
            self.status_var.set(f"Opened folder: {os.path.basename(target) or target}")
        except Exception as exc:
            messagebox.showerror("Open folder error", f"Cannot open folder:\n{target}\n\n{exc}")

    def _normalize_project_path(self, project_path: str) -> str | None:
        target = (project_path or "").strip()
        if not target:
            messagebox.showinfo("Missing project path", "Selected tool has no Project Path.")
            return None
        target = os.path.normpath(target)
        if not os.path.exists(target):
            messagebox.showerror("Path error", f"Project path not found:\n{target}")
            return None
        if os.path.isfile(target):
            target = os.path.dirname(target)
        return target

    def _find_available_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    def _resolve_python_command(self) -> List[str] | None:
        for command in (["python"], ["py", "-3"], ["py"]):
            try:
                result = subprocess.run(command + ["--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            except FileNotFoundError:
                continue
            if result.returncode == 0:
                return command
        return None

    def run_selected_tool(self) -> None:
        entry = self._selected_entry()
        if not entry:
            return
        project_root = self._normalize_project_path(entry.project_path)
        if not project_root:
            return
        index_file = os.path.join(project_root, "index.html")
        if not os.path.exists(index_file):
            messagebox.showerror("Run error", f"Cannot find index.html in:\n{project_root}")
            return
        python_command = self._resolve_python_command()
        if not python_command:
            messagebox.showerror("Run error", "Cannot find Python launcher (python or py).")
            return
        port = self._find_available_port()
        try:
            subprocess.Popen(
                python_command + ["-m", "http.server", str(port)],
                cwd=project_root,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except Exception as exc:
            messagebox.showerror("Run error", f"Cannot start http server in:\n{project_root}\n\n{exc}")
            return
        webbrowser.open_new_tab(f"http://127.0.0.1:{port}/index.html")
        self.status_var.set(f"Running local server on port {port}")


def ensure_data_file(path: str) -> None:
    if os.path.exists(path):
        return
    sample = [{
        "name": "Example Tool",
        "email": "owner@example.com",
        "website_url": "https://example.com",
        "github_url": "https://github.com/example/repo",
        "firebase_console_url": "https://console.firebase.google.com",
        "project_path": "D:\\Projects\\ExampleTool",
    }]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)


def set_windows_app_id() -> None:
    if os.name != "nt":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description="ToolHub - manage website/GitHub/Firebase links")
    parser.add_argument("--data", default=DEFAULT_DATA_FILE, help="Path to JSON data file")
    parser.add_argument("--check", action="store_true", help="Validate app dependencies and data file")
    args = parser.parse_args()
    data_file = os.path.abspath(args.data)
    ensure_data_file(data_file)
    if args.check:
        with open(data_file, "r", encoding="utf-8-sig") as f:
            loaded = json.load(f)
        if not isinstance(loaded, list):
            print("CHECK FAILED: Data file must contain a list")
            return 1
        print(f"CHECK OK: {data_file}")
        return 0
    set_windows_app_id()
    root = tk.Tk()
    app = ToolHubApp(root, data_file=data_file)
    root.mainloop()
    _ = app
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
