import argparse
import json
import os
from dataclasses import asdict, dataclass
from typing import List
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser


DEFAULT_DATA_FILE = "tools_data.json"


@dataclass
class ToolEntry:
    name: str
    email: str = ""
    website_url: str = ""
    github_url: str = ""
    firebase_console_url: str = ""
    project_path: str = ""
    run_file: str = ""


class ToolHubApp:
    def __init__(self, root: tk.Tk, data_file: str):
        self.root = root
        self.data_file = data_file
        self.entries: List[ToolEntry] = []
        self.visible_indices: List[int] = []
        self.search_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Ready")

        self.root.title("ToolHub - Project Link Manager")
        self.root.geometry("1360x760")
        self.root.minsize(1080, 620)

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
        self.colors = {
            "bg": "#F3F7FC",
            "surface": "#FFFFFF",
            "panel": "#E8EFF8",
            "table_head_bg": "#EEF4FC",
            "table_head_border": "#D6E2F0",
            "table_grid": "#E2EAF5",
            "header": "#DCE9F9",
            "header_text": "#1E3555",
            "text": "#223247",
            "muted": "#5D728A",
            "accent": "#2F7BD9",
            "success": "#1FA971",
            "danger": "#D9534F",
            "row_even": "#FFFFFF",
            "row_odd": "#F6FAFF",
            "selected": "#D9E9FB",
            "input_bg": "#FFFFFF",
            "input_fg": "#223247",
            "scroll_thumb": "#B7CAE3",
            "scroll_thumb_active": "#9FB7D7",
            "scroll_trough": "#EAF1FA",
        }

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.root.configure(bg=self.colors["bg"])

        style.configure("App.TFrame", background=self.colors["bg"])
        style.configure("Card.TFrame", background=self.colors["surface"], relief="flat")
        style.configure("Dialog.TFrame", background=self.colors["surface"])
        style.configure("App.TLabel", background=self.colors["bg"], foreground=self.colors["text"], font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=self.colors["panel"], foreground=self.colors["text"], font=("Segoe UI", 10))
        style.configure("TLabelFrame", background=self.colors["panel"], borderwidth=1, relief="groove")
        style.configure(
            "TLabelFrame.Label",
            background=self.colors["panel"],
            foreground=self.colors["muted"],
            font=("Segoe UI Semibold", 8),
        )
        style.configure("Manage.TLabelframe", background="#E6EEF9", borderwidth=1, relief="groove")
        style.configure("Manage.TLabelframe.Label", background="#E6EEF9", foreground="#436082", font=("Segoe UI Semibold", 8))
        style.configure("Search.TLabelframe", background="#EAF3FF", borderwidth=1, relief="groove")
        style.configure("Search.TLabelframe.Label", background="#EAF3FF", foreground="#436082", font=("Segoe UI Semibold", 8))
        style.configure("Action.TLabelframe", background="#EDF4FC", borderwidth=1, relief="groove")
        style.configure("Action.TLabelframe.Label", background="#EDF4FC", foreground="#436082", font=("Segoe UI Semibold", 8))
        style.configure("Manage.Panel.TLabel", background="#E6EEF9", foreground=self.colors["text"], font=("Segoe UI", 9))
        style.configure("Search.Panel.TLabel", background="#EAF3FF", foreground=self.colors["text"], font=("Segoe UI", 9))
        style.configure("Action.Panel.TLabel", background="#EDF4FC", foreground=self.colors["text"], font=("Segoe UI", 9))
        style.configure("Dialog.TLabel", background=self.colors["surface"], foreground=self.colors["text"])
        style.configure(
            "Header.TButton",
            font=("Segoe UI Semibold", 9),
            padding=(10, 5),
            borderwidth=1,
            relief="solid",
            background="#C7DAF4",
            foreground="#1B385C",
        )
        style.map("Header.TButton", background=[("active", "#B5CFEF")])
        style.configure(
            "Title.TLabel",
            background=self.colors["header"],
            foreground=self.colors["header_text"],
            font=("Segoe UI Semibold", 14),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.colors["header"],
            foreground="#4F6B8A",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Hint.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 9),
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 9),
            padding=(8, 4),
            borderwidth=1,
            relief="solid",
            background="#E1EAF6",
            foreground=self.colors["text"],
        )
        style.map("TButton", background=[("active", "#D5E3F5")], foreground=[("disabled", "#97A7B8")])
        style.configure("Primary.TButton", foreground="#FFFFFF", background=self.colors["accent"])
        style.map("Primary.TButton", background=[("active", "#2567BA")], foreground=[("active", "#FFFFFF")])
        style.configure("Danger.TButton", foreground="#FFFFFF", background=self.colors["danger"])
        style.map("Danger.TButton", background=[("active", "#DC2626")])
        style.configure("Success.TButton", foreground="#FFFFFF", background=self.colors["success"])
        style.map("Success.TButton", background=[("active", "#059669")])

        style.configure(
            "TEntry",
            padding=6,
            font=("Segoe UI", 9),
            fieldbackground=self.colors["input_bg"],
            foreground=self.colors["input_fg"],
            insertcolor=self.colors["input_fg"],
            bordercolor="#C8D7EB",
            lightcolor="#C8D7EB",
            darkcolor="#C8D7EB",
        )
        style.configure(
            "App.Vertical.TScrollbar",
            background=self.colors["scroll_thumb"],
            troughcolor=self.colors["scroll_trough"],
            bordercolor=self.colors["scroll_trough"],
            arrowcolor=self.colors["muted"],
            width=14,
        )
        style.map("App.Vertical.TScrollbar", background=[("active", self.colors["scroll_thumb_active"])])
        style.configure(
            "App.Horizontal.TScrollbar",
            background=self.colors["scroll_thumb"],
            troughcolor=self.colors["scroll_trough"],
            bordercolor=self.colors["scroll_trough"],
            arrowcolor=self.colors["muted"],
        )
        style.map("App.Horizontal.TScrollbar", background=[("active", self.colors["scroll_thumb_active"])])
        style.configure(
            "Treeview",
            rowheight=24,
            font=("Segoe UI", 9),
            fieldbackground=self.colors["surface"],
            background=self.colors["surface"],
            foreground=self.colors["text"],
            bordercolor=self.colors["table_grid"],
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI Semibold", 8),
            padding=(6, 4),
            background=self.colors["table_head_bg"],
            foreground=self.colors["text"],
            bordercolor=self.colors["table_head_border"],
            darkcolor=self.colors["table_head_border"],
            lightcolor=self.colors["table_head_border"],
            relief="flat",
        )
        style.map("Treeview.Heading", background=[("active", "#E8F1FB")])
        style.map(
            "Treeview",
            background=[("selected", self.colors["selected"])],
            foreground=[("selected", self.colors["text"])],
        )

    def _build_ui(self) -> None:
        root_container = ttk.Frame(self.root, style="App.TFrame", padding=0)
        root_container.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(root_container, bg=self.colors["header"], padx=16, pady=12)
        header.pack(fill=tk.X)
        ttk.Button(header, text="MoneTag", style="Header.TButton", command=self.open_monetag_statistics).pack(side=tk.RIGHT, padx=(12, 0))
        ttk.Label(header, text="ToolHub", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(
            header,
            text="Manage website links, source repos, Firebase console, project paths, and run files.",
            style="Subtitle.TLabel",
        ).pack(anchor=tk.W, pady=(2, 0))

        toolbar = ttk.Frame(root_container, style="App.TFrame", padding=(14, 12, 14, 10))
        toolbar.pack(fill=tk.X)

        manage_group = ttk.LabelFrame(toolbar, text="Manage", style="Manage.TLabelframe", padding=(12, 10))
        manage_group.pack(side=tk.LEFT, padx=(0, 12))
        ttk.Button(manage_group, text="Add", style="Primary.TButton", command=self.add_entry).pack(side=tk.LEFT, padx=3, pady=1)
        ttk.Button(manage_group, text="Edit", command=self.edit_entry).pack(side=tk.LEFT, padx=3, pady=1)
        ttk.Button(manage_group, text="Delete", style="Danger.TButton", command=self.delete_entry).pack(side=tk.LEFT, padx=3, pady=1)
        ttk.Button(manage_group, text="Reload", command=self.reload_entries).pack(side=tk.LEFT, padx=3, pady=1)

        search_group = ttk.LabelFrame(toolbar, text="Search", style="Search.TLabelframe", padding=(12, 10))
        search_group.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        ttk.Label(search_group, text="Tool Name:", style="Search.Panel.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        self.search_entry = ttk.Entry(search_group, textvariable=self.search_var, width=32)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True, ipady=1)
        self.search_entry.bind("<KeyRelease>", lambda _event: self.refresh_table())
        ttk.Button(search_group, text="Clear", command=self.clear_search).pack(side=tk.LEFT, pady=1)

        action_group = ttk.LabelFrame(toolbar, text="Actions", style="Action.TLabelframe", padding=(12, 10))
        action_group.pack(side=tk.RIGHT)
        ttk.Button(action_group, text="Run", style="Success.TButton", command=self.run_selected_tool).pack(side=tk.LEFT, padx=3, pady=1)
        ttk.Button(action_group, text="Open Folder", command=self.open_selected_project_folder).pack(side=tk.LEFT, padx=3, pady=1)
        ttk.Button(action_group, text="Website", command=self.open_selected_website).pack(side=tk.LEFT, padx=3, pady=1)
        ttk.Button(action_group, text="GitHub", command=self.open_selected_github).pack(side=tk.LEFT, padx=3, pady=1)
        ttk.Button(action_group, text="Firebase", command=self.open_selected_firebase).pack(side=tk.LEFT, padx=3, pady=1)

        table_card = ttk.Frame(root_container, style="Card.TFrame", padding=(14, 8, 14, 8))
        table_card.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "email", "website_url", "github_url", "firebase_console_url", "project_path", "run_file")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="Tool Name")
        self.tree.heading("email", text="Email")
        self.tree.heading("website_url", text="Website URL")
        self.tree.heading("github_url", text="GitHub URL")
        self.tree.heading("firebase_console_url", text="Firebase Console URL")
        self.tree.heading("project_path", text="Project Path")
        self.tree.heading("run_file", text="Run File")

        self.tree.column("name", width=180, anchor=tk.W)
        self.tree.column("email", width=220, anchor=tk.W)
        self.tree.column("website_url", width=220, anchor=tk.W)
        self.tree.column("github_url", width=220, anchor=tk.W)
        self.tree.column("firebase_console_url", width=240, anchor=tk.W)
        self.tree.column("project_path", width=300, anchor=tk.W)
        self.tree.column("run_file", width=220, anchor=tk.W)

        self.tree.tag_configure("even", background=self.colors["row_even"])
        self.tree.tag_configure("odd", background=self.colors["row_odd"])

        y_scroll = ttk.Scrollbar(table_card, orient=tk.VERTICAL, style="App.Vertical.TScrollbar", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_card, orient=tk.HORIZONTAL, style="App.Horizontal.TScrollbar", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(0, weight=1)

        footer = ttk.Frame(root_container, style="App.TFrame", padding=(14, 0, 14, 10))
        footer.pack(fill=tk.X)
        ttk.Label(footer, style="Hint.TLabel", text="Tips: Double-click row to edit. Ctrl+F focus search. F5 reload.").pack(side=tk.LEFT)
        ttk.Label(footer, style="Hint.TLabel", textvariable=self.status_var).pack(side=tk.RIGHT)

        self.tree.bind("<Double-1>", lambda _event: self.edit_entry())
        self.tree.bind("<<TreeviewSelect>>", lambda _event: self._update_status())

    def load_entries(self) -> None:
        if not os.path.exists(self.data_file):
            self.entries = []
            self.save_entries()
            return

        try:
            with open(self.data_file, "r", encoding="utf-8-sig") as f:
                raw = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            messagebox.showerror("Read error", f"Cannot read {self.data_file}:\n{exc}")
            self.entries = []
            return

        self.entries = []
        if isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict):
                    continue
                self.entries.append(
                    ToolEntry(
                        name=str(item.get("name", "")).strip(),
                        email=str(item.get("email", "")).strip(),
                        website_url=str(item.get("website_url", "")).strip(),
                        github_url=str(item.get("github_url", "")).strip(),
                        firebase_console_url=str(item.get("firebase_console_url", "")).strip(),
                        project_path=str(item.get("project_path", "")).strip(),
                        run_file=str(item.get("run_file", "")).strip(),
                    )
                )

    def save_entries(self) -> None:
        payload = [asdict(entry) for entry in self.entries]
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def refresh_table(self) -> None:
        selected_before = self._selected_index()
        for row in self.tree.get_children():
            self.tree.delete(row)

        keyword = self.search_var.get().strip().lower()
        self.visible_indices = []
        for idx, entry in enumerate(self.entries):
            if keyword and keyword not in entry.name.lower():
                continue
            self.visible_indices.append(idx)

        for view_idx, idx in enumerate(self.visible_indices):
            entry = self.entries[idx]
            tag = "even" if view_idx % 2 == 0 else "odd"
            self.tree.insert(
                "",
                tk.END,
                iid=str(view_idx),
                tags=(tag,),
                values=(
                    entry.name,
                    entry.email,
                    entry.website_url,
                    entry.github_url,
                    entry.firebase_console_url,
                    entry.project_path,
                    entry.run_file,
                ),
            )

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

    def _focus_search(self, _event=None):
        self.search_entry.focus_set()
        self.search_entry.selection_range(0, tk.END)
        return "break"

    def clear_search(self) -> None:
        self.search_var.set("")
        self.refresh_table()
        self.search_entry.focus_set()

    def _update_status(self) -> None:
        total = len(self.entries)
        visible = len(self.visible_indices)
        idx = self._selected_index()
        if idx is None:
            self.status_var.set(f"Showing {visible}/{total} tool(s)")
            return
        self.status_var.set(f"Showing {visible}/{total} tool(s) | Selected: {self.entries[idx].name}")

    def _entry_dialog(self, title: str, default: ToolEntry | None = None) -> ToolEntry | None:
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.configure(bg=self.colors["surface"])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        vars_map = {
            "name": tk.StringVar(value=(default.name if default else "")),
            "email": tk.StringVar(value=(default.email if default else "")),
            "website_url": tk.StringVar(value=(default.website_url if default else "")),
            "github_url": tk.StringVar(value=(default.github_url if default else "")),
            "firebase_console_url": tk.StringVar(value=(default.firebase_console_url if default else "")),
            "project_path": tk.StringVar(value=(default.project_path if default else "")),
            "run_file": tk.StringVar(value=(default.run_file if default else "")),
        }

        form = ttk.Frame(dialog, style="Dialog.TFrame", padding=14)
        form.grid(row=0, column=0, sticky="nsew")

        labels = [
            ("Tool Name*", "name"),
            ("Email", "email"),
            ("Website URL", "website_url"),
            ("GitHub URL", "github_url"),
            ("Firebase Console URL", "firebase_console_url"),
            ("Project Path", "project_path"),
            ("Run File", "run_file"),
        ]

        for row_idx, (label, key) in enumerate(labels):
            ttk.Label(form, text=label, style="Dialog.TLabel").grid(row=row_idx, column=0, sticky="w", pady=5)
            entry_widget = ttk.Entry(form, textvariable=vars_map[key], width=78)
            entry_widget.grid(row=row_idx, column=1, sticky="ew", padx=(8, 0), pady=5)

            if key == "project_path":
                ttk.Button(
                    form,
                    text="Browse Folder",
                    command=lambda v=vars_map["project_path"]: self._browse_folder(v, dialog),
                ).grid(row=row_idx, column=2, sticky="w", padx=(8, 0), pady=5)
            if key == "run_file":
                ttk.Button(
                    form,
                    text="Browse File",
                    command=lambda v=vars_map["run_file"]: self._browse_file(v, vars_map["project_path"], dialog),
                ).grid(row=row_idx, column=2, sticky="w", padx=(8, 0), pady=5)

            if row_idx == 0:
                entry_widget.focus_set()

        form.columnconfigure(1, weight=1)

        buttons = ttk.Frame(form)
        buttons.grid(row=len(labels), column=1, sticky="e", pady=(12, 0))

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
                run_file=vars_map["run_file"].get().strip(),
            )
            dialog.destroy()

        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(buttons, text="Save", style="Primary.TButton", command=on_ok).pack(side=tk.RIGHT)

        dialog.wait_window()
        return result["value"]

    def _browse_folder(self, target_var: tk.StringVar, parent: tk.Toplevel) -> None:
        selected = filedialog.askdirectory(parent=parent, title="Select project folder")
        if selected:
            target_var.set(selected)

    def _browse_file(self, target_var: tk.StringVar, project_var: tk.StringVar, parent: tk.Toplevel) -> None:
        initial_dir = project_var.get().strip() or os.path.dirname(os.path.abspath(self.data_file))
        selected = filedialog.askopenfilename(parent=parent, title="Select run file", initialdir=initial_dir)
        if not selected:
            return

        project_path = project_var.get().strip()
        if project_path:
            try:
                rel_path = os.path.relpath(selected, project_path)
                if not rel_path.startswith(".."):
                    target_var.set(rel_path)
                    return
            except ValueError:
                pass
        target_var.set(selected)

    def add_entry(self) -> None:
        created = self._entry_dialog("Add Tool")
        if not created:
            return
        self.entries.append(created)
        self.save_entries()
        self.refresh_table()
        self.status_var.set(f"Added: {created.name}")

    def edit_entry(self) -> None:
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Select row", "Please select a row to edit.")
            return

        updated = self._entry_dialog("Edit Tool", self.entries[idx])
        if not updated:
            return

        self.entries[idx] = updated
        self.save_entries()
        self.refresh_table()
        self.status_var.set(f"Updated: {updated.name}")

    def delete_entry(self) -> None:
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Select row", "Please select a row to delete.")
            return

        entry = self.entries[idx]
        confirmed = messagebox.askyesno("Confirm delete", f"Delete '{entry.name}'?")
        if not confirmed:
            return

        del self.entries[idx]
        self.save_entries()
        self.refresh_table()
        self.status_var.set(f"Deleted: {entry.name}")

    def _open_url(self, label: str, url: str) -> None:
        url = (url or "").strip()
        if not url:
            messagebox.showinfo("Missing URL", f"Selected tool has no {label} URL.")
            return
        webbrowser.open_new_tab(url)
        self.status_var.set(f"Opened {label}")

    def _selected_entry(self) -> ToolEntry | None:
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Select row", "Please select a row first.")
            return None
        return self.entries[idx]

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

    def open_monetag_statistics(self) -> None:
        self._open_url("MoneTag Statistics", "https://publishers.monetag.com/statistics")

    def open_selected_project_folder(self) -> None:
        entry = self._selected_entry()
        if not entry:
            return

        project_path = (entry.project_path or "").strip()
        if not project_path:
            messagebox.showinfo("Missing project path", "Selected tool has no Project Path.")
            return

        target = os.path.normpath(project_path)
        if not os.path.exists(target):
            messagebox.showerror("Open folder error", f"Project path not found:\n{target}")
            return

        if os.path.isfile(target):
            target = os.path.dirname(target)

        try:
            os.startfile(target)  # type: ignore[attr-defined]
            self.status_var.set(f"Opened folder: {os.path.basename(target) or target}")
        except Exception as exc:
            messagebox.showerror("Open folder error", f"Cannot open folder:\n{target}\n\n{exc}")

    def run_selected_tool(self) -> None:
        entry = self._selected_entry()
        if not entry:
            return

        run_value = (entry.run_file or "").strip()
        if not run_value:
            messagebox.showinfo("Missing run file", "Selected tool has no Run File.")
            return

        run_target = run_value
        if not os.path.isabs(run_target):
            if entry.project_path:
                run_target = os.path.join(entry.project_path, run_target)
            else:
                run_target = os.path.join(os.path.dirname(os.path.abspath(self.data_file)), run_target)

        run_target = os.path.normpath(run_target)
        if not os.path.exists(run_target):
            messagebox.showerror("Run error", f"Run file not found:\n{run_target}")
            return

        try:
            os.startfile(run_target)  # type: ignore[attr-defined]
            self.status_var.set(f"Running: {os.path.basename(run_target)}")
        except Exception as exc:
            messagebox.showerror("Run error", f"Cannot run file:\n{run_target}\n\n{exc}")


def ensure_data_file(path: str) -> None:
    if os.path.exists(path):
        return

    sample = [
        {
            "name": "Example Tool",
            "email": "owner@example.com",
            "website_url": "https://example.com",
            "github_url": "https://github.com/example/repo",
            "firebase_console_url": "https://console.firebase.google.com",
            "project_path": "D:\\Projects\\ExampleTool",
            "run_file": "run_hub.cmd",
        }
    ]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="ToolHub - manage website/GitHub/Firebase links")
    parser.add_argument("--data", default=DEFAULT_DATA_FILE, help="Path to JSON data file")
    parser.add_argument("--check", action="store_true", help="Validate app dependencies and data file")
    args = parser.parse_args()

    data_file = os.path.abspath(args.data)
    ensure_data_file(data_file)

    if args.check:
        try:
            with open(data_file, "r", encoding="utf-8-sig") as f:
                loaded = json.load(f)
            if not isinstance(loaded, list):
                raise ValueError("Data file must contain a list")
        except Exception as exc:
            print(f"CHECK FAILED: {exc}")
            return 1
        print(f"CHECK OK: {data_file}")
        return 0

    root = tk.Tk()
    app = ToolHubApp(root, data_file=data_file)
    root.mainloop()
    _ = app
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
