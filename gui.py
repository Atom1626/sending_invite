#!/usr/bin/env python3
import json
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

# Import automation functions
try:
    from test1 import run_get_links
    from send_message import run_send_messages
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import automation scripts:\n{e}")

CONFIG_SETTINGS_FILE = "gui_settings.json"

DEFAULT_SETTINGS = {
    "get_links_from": 158,
    "get_links_to": 159,
    "send_invite_from": 158,
    "send_invite_to": 159,
    "custom_excel": "",
    "firstName": "Kiran",
    "lastName": "K",
    "email": "kiran@gesoftech.com",
    "phone": " 4",
    "company": " Softech",
    "country": "India",
    "relationship": "Prospective Customer",
    "message": """Sub: SAP Services & Staffing Support - Globalwave Softech

Dear Team,

Greetings from  Softech!

We are a global SAP services and staffing company with 200+ employees across the USA and India, offering expertise across various SAP modules.

We can support your upcoming requirements through:

SAP Implementation, Support Services & Migration Projects
Contract & Contract-to-Hire Staffing
Full-Time Recruitment
Experienced and immediately available SAP resources
Competitive and flexible pricing
We would be happy to connect and understand your current or upcoming SAP requirements and explore opportunities to work together.

Please share your email address and convenient time for a quick call.


Looking forward to connecting with you.

Best Regards,
Kiran
Globalwave Softech"""
}


class AutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SAP Automation Suite — Pill Segmented Edition")
        self.root.geometry("1080x820")
        self.root.minsize(920, 720)

        # Threading and Queues
        self.log_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.running_thread = None
        self.current_task = None  # 'get_links' or 'send_invites'

        # Settings
        self.settings = self.load_settings()

        # Build UI with White Claymorphism & Pill Segmented Navigation
        self.apply_theme()
        self.create_widgets()

        # Start queue listener
        self.root.after(100, self.process_log_queue)

        # Handle window closing gracefully
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle application exit safely when thread is running."""
        if self.running_thread and self.running_thread.is_alive():
            if messagebox.askokcancel("Quit", "Automation task is currently running. Do you want to stop it and exit?"):
                self.stop_event.set()
                self.save_settings(show_alert=False)
                self.root.destroy()
        else:
            self.save_settings(show_alert=False)
            self.root.destroy()

    def load_settings(self):
        """Load saved settings from JSON file, using defaults if not found."""
        if os.path.exists(CONFIG_SETTINGS_FILE):
            try:
                with open(CONFIG_SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    merged = DEFAULT_SETTINGS.copy()
                    merged.update(data)
                    return merged
            except Exception as e:
                print(f"Error loading settings file: {e}")
        return DEFAULT_SETTINGS.copy()

    def save_settings(self, show_alert=False):
        """Save current form state and settings to JSON file."""
        try:
            self.settings["get_links_from"] = int(self.entry_get_from.get().strip())
            self.settings["get_links_to"] = int(self.entry_get_to.get().strip())
            self.settings["send_invite_from"] = int(self.entry_send_from.get().strip())
            self.settings["send_invite_to"] = int(self.entry_send_to.get().strip())
        except ValueError:
            pass

        self.settings["custom_excel"] = self.custom_excel_var.get().strip()
        self.settings["firstName"] = self.entry_fn.get().strip()
        self.settings["lastName"] = self.entry_ln.get().strip()
        self.settings["email"] = self.entry_email.get().strip()
        self.settings["phone"] = self.entry_phone.get().strip()
        self.settings["company"] = self.entry_company.get().strip()
        self.settings["country"] = self.combo_country.get().strip()
        self.settings["relationship"] = self.combo_rel.get().strip()
        self.settings["message"] = self.txt_msg.get("1.0", tk.END).strip()

        try:
            with open(CONFIG_SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f, indent=4)
            if show_alert:
                messagebox.showinfo("Success", "Settings and details saved successfully!")
        except Exception as e:
            if show_alert:
                messagebox.showerror("Error", f"Could not save settings: {e}")

    def apply_theme(self):
        """Configure TTK styles for Light Claymorphism with Purple Canvas & White Rounded Cards."""
        style = ttk.Style()
        style.theme_use("clam")

        # Color Palette
        self.c_bg_main = "#6d28d9"        # Rich Purple Canvas Background
        self.c_card_bg = "#ffffff"        # Pure White Soft Clay Card Surface
        self.c_fg_dark = "#0f172a"        # Bold Dark Charcoal Title Text
        self.c_fg_subtle = "#64748b"      # Muted Slate Text
        self.c_input_bg = "#f8fafc"      # Soft White Inset Input Box

        self.c_purple_btn = "#9333ea"    # Vibrant Purple Action Button
        self.c_dark_violet = "#1e1b4b"    # Deep Dark Violet Button
        self.c_rose_btn = "#e11d48"       # Soft Rose Crimson Button

        self.root.configure(bg=self.c_bg_main)

        # Base frames
        style.configure("TFrame", background=self.c_bg_main)

        # White Clay Card Container
        style.configure("WhiteClayCard.TFrame", 
                        background=self.c_card_bg, 
                        relief="flat", 
                        borderwidth=0, 
                        padding=14)

        # CardInner.TFrame for nested white containers without extra padding
        style.configure("CardInner.TFrame", 
                        background=self.c_card_bg, 
                        relief="flat", 
                        borderwidth=0, 
                        padding=0)

        # Label styles
        style.configure("TLabel", background=self.c_bg_main, foreground="#ffffff", font=("DejaVu Sans", 10))
        style.configure("Card.TLabel", background=self.c_card_bg, foreground=self.c_fg_dark, font=("DejaVu Sans", 10, "bold"))
        style.configure("Sub.TLabel", background=self.c_card_bg, foreground=self.c_fg_subtle, font=("DejaVu Sans", 9))
        style.configure("Header.TLabel", background=self.c_card_bg, foreground=self.c_fg_dark, font=("DejaVu Sans", 13, "bold"))
        style.configure("Title.TLabel", background=self.c_bg_main, foreground="#ffffff", font=("DejaVu Sans", 16, "bold"))

        # Entry and Combobox styling
        style.configure("TEntry", 
                        fieldbackground=self.c_input_bg, 
                        foreground=self.c_fg_dark, 
                        bordercolor="#cbd5e1",
                        lightcolor="#f1f5f9",
                        darkcolor="#cbd5e1",
                        padding=5)
        
        style.configure("TCombobox", 
                        fieldbackground=self.c_input_bg, 
                        background=self.c_card_bg,
                        foreground=self.c_fg_dark, 
                        bordercolor="#cbd5e1",
                        padding=5)
        style.map("TCombobox", fieldbackground=[("readonly", self.c_input_bg)], foreground=[("readonly", self.c_fg_dark)])

        # Button Styles (Pill Claymorphic Feel)
        style.configure("PurpleClay.TButton", 
                        background=self.c_purple_btn, 
                        foreground="#ffffff", 
                        font=("DejaVu Sans", 10, "bold"), 
                        relief="flat", 
                        borderwidth=0,
                        padding=[12, 7])
        style.map("PurpleClay.TButton", background=[("active", "#a855f7"), ("disabled", "#cbd5e1")])

        style.configure("DarkVioletClay.TButton", 
                        background=self.c_dark_violet, 
                        foreground="#ffffff", 
                        font=("DejaVu Sans", 10, "bold"), 
                        relief="flat", 
                        borderwidth=0,
                        padding=[12, 7])
        style.map("DarkVioletClay.TButton", background=[("active", "#312e81"), ("disabled", "#cbd5e1")])

        style.configure("RoseClay.TButton", 
                        background=self.c_rose_btn, 
                        foreground="#ffffff", 
                        font=("DejaVu Sans", 10, "bold"), 
                        relief="flat", 
                        borderwidth=0,
                        padding=[12, 7])
        style.map("RoseClay.TButton", background=[("active", "#f43f5e"), ("disabled", "#cbd5e1")])

        style.configure("TButton", 
                        background="#f1f5f9", 
                        foreground="#6d28d9", 
                        font=("DejaVu Sans", 9, "bold"), 
                        padding=5)
        style.map("TButton", background=[("active", "#e2e8f0")])

    def create_widgets(self):
        # Top Header Banner Frame
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=20, pady=(14, 2))

        title_box = ttk.Frame(header_frame)
        title_box.pack(side="left")
        ttk.Label(title_box, text="SAP Partner Finder Automation", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_box, text="How to extract profiles and send invites with ease.", style="TLabel", foreground="#e9d5ff").pack(anchor="w")

        # --- PILL SEGMENTED TAB SWITCHER (Tight top-left position) ---
        nav_bar_frame = ttk.Frame(self.root)
        nav_bar_frame.pack(fill="x", padx=20, pady=(4, 0))

        nav_track = tk.Frame(nav_bar_frame, bg="#5b21b6", padx=3, pady=3)
        nav_track.pack(side="left")

        self.tab_btn_get_links = tk.Button(
            nav_track, 
            text="Get Links", 
            font=("DejaVu Sans", 10, "bold"),
            bd=0, 
            relief="flat", 
            padx=20, 
            pady=7,
            cursor="hand2",
            command=lambda: self.switch_tab("get_links")
        )
        self.tab_btn_get_links.pack(side="left", padx=1)

        self.tab_btn_send_invite = tk.Button(
            nav_track, 
            text="Sending Invite", 
            font=("DejaVu Sans", 10, "bold"),
            bd=0, 
            relief="flat", 
            padx=20, 
            pady=7,
            cursor="hand2",
            command=lambda: self.switch_tab("send_invite")
        )
        self.tab_btn_send_invite.pack(side="left", padx=1)

        # Content Container Frame (Tight vertical spacing)
        self.content_container = ttk.Frame(self.root)
        self.content_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.tab_get_links = ttk.Frame(self.content_container)
        self.tab_send_invite = ttk.Frame(self.content_container)

        self.build_get_links_tab()
        self.build_send_invite_tab()

        # Default Active Tab
        self.switch_tab("get_links")

    def switch_tab(self, tab_name):
        """Switch active tab content and update Pill Segmented Switcher styling."""
        self.tab_get_links.pack_forget()
        self.tab_send_invite.pack_forget()

        active_bg = "#ddd6fe"   # Soft Lavender Capsule Highlight
        active_fg = "#2e1065"   # Deep Dark Violet Text
        inactive_bg = "#5b21b6" # Dark Purple Segment Track
        inactive_fg = "#e9d5ff" # Light Purple Text

        if tab_name == "get_links":
            self.tab_btn_get_links.config(bg=active_bg, fg=active_fg, activebackground=active_bg, activeforeground=active_fg)
            self.tab_btn_send_invite.config(bg=inactive_bg, fg=inactive_fg, activebackground=inactive_bg, activeforeground=inactive_fg)
            self.tab_get_links.pack(fill="both", expand=True)
        else:
            self.tab_btn_send_invite.config(bg=active_bg, fg=active_fg, activebackground=active_bg, activeforeground=active_fg)
            self.tab_btn_get_links.config(bg=inactive_bg, fg=inactive_fg, activebackground=inactive_bg, activeforeground=inactive_fg)
            self.tab_send_invite.pack(fill="both", expand=True)

    # ================= TAB 1: GET LINKS =================
    def build_get_links_tab(self):
        main_frame = ttk.Frame(self.tab_get_links)
        main_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # White Clay Card: Controls
        ctrl_card = ttk.Frame(main_frame, style="WhiteClayCard.TFrame")
        ctrl_card.pack(fill="x", pady=6)

        ttk.Label(ctrl_card, text="Link Extraction Parameters", style="Header.TLabel").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 2))
        ttk.Label(ctrl_card, text="Configure target search page range to extract profile cards into Excel.", style="Sub.TLabel").grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 8))

        ttk.Label(ctrl_card, text="From Page:", style="Card.TLabel").grid(row=2, column=0, sticky="w", padx=6, pady=5)
        self.entry_get_from = ttk.Entry(ctrl_card, width=10)
        self.entry_get_from.insert(0, str(self.settings.get("get_links_from", 158)))
        self.entry_get_from.grid(row=2, column=1, sticky="w", padx=6, pady=5)

        ttk.Label(ctrl_card, text="To Page:", style="Card.TLabel").grid(row=2, column=2, sticky="w", padx=6, pady=5)
        self.entry_get_to = ttk.Entry(ctrl_card, width=10)
        self.entry_get_to.insert(0, str(self.settings.get("get_links_to", 159)))
        self.entry_get_to.grid(row=2, column=3, sticky="w", padx=6, pady=5)

        # Target Excel Output Display
        self.lbl_get_file = ttk.Label(ctrl_card, text="", style="Sub.TLabel", foreground="#7c3aed")
        self.lbl_get_file.grid(row=3, column=0, columnspan=4, sticky="w", padx=6, pady=5)
        self.update_get_filename_label()

        self.entry_get_from.bind("<KeyRelease>", lambda e: self.update_get_filename_label())
        self.entry_get_to.bind("<KeyRelease>", lambda e: self.update_get_filename_label())

        # Buttons Bar (Claymorphic Pills)
        btn_frame = ttk.Frame(ctrl_card, style="WhiteClayCard.TFrame")
        btn_frame.grid(row=4, column=0, columnspan=4, sticky="w", pady=10)

        self.btn_get_start = ttk.Button(btn_frame, text="Start Get Links", style="PurpleClay.TButton", command=self.start_get_links)
        self.btn_get_start.pack(side="left", padx=5)

        self.btn_get_stop = ttk.Button(btn_frame, text="Stop Process", style="RoseClay.TButton", command=self.stop_task, state="disabled")
        self.btn_get_stop.pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Clear Log", command=lambda: self.clear_log(self.log_get_links)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Open Folder", command=self.open_output_dir).pack(side="left", padx=5)

        # Progress bar
        self.progress_get = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress_get.pack(fill="x", pady=5)

        # Log Console Container
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill="both", expand=True, pady=5)

        ttk.Label(log_frame, text="Live Extraction Terminal Log:").pack(anchor="w", pady=(0, 4))
        self.log_get_links = ScrolledText(
            log_frame, 
            bg="#1e1b4b", 
            fg="#f8fafc", 
            font=("Consolas", 10), 
            insertbackground="white",
            relief="flat",
            bd=0
        )
        self.log_get_links.pack(fill="both", expand=True)

    def update_get_filename_label(self):
        f = self.entry_get_from.get().strip()
        t = self.entry_get_to.get().strip()
        self.lbl_get_file.config(text=f"Target Output Excel: profile_cards_pages_{f}_to_{t}.xlsx")

    # ================= TAB 2: SENDING INVITE =================
    def build_send_invite_tab(self):
        main_frame = ttk.Frame(self.tab_send_invite)
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Card 1: Page Range & Excel Source
        page_card = ttk.Frame(main_frame, style="WhiteClayCard.TFrame")
        page_card.pack(fill="x", pady=4)

        ttk.Label(page_card, text="Target Excel Source", style="Header.TLabel").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 2))
        ttk.Label(page_card, text="Select pages or custom Excel file containing link records.", style="Sub.TLabel").grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 6))

        ttk.Label(page_card, text="From Page:", style="Card.TLabel").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.entry_send_from = ttk.Entry(page_card, width=10)
        self.entry_send_from.insert(0, str(self.settings.get("send_invite_from", 158)))
        self.entry_send_from.grid(row=2, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(page_card, text="To Page:", style="Card.TLabel").grid(row=2, column=2, sticky="w", padx=6, pady=4)
        self.entry_send_to = ttk.Entry(page_card, width=10)
        self.entry_send_to.insert(0, str(self.settings.get("send_invite_to", 159)))
        self.entry_send_to.grid(row=2, column=3, sticky="w", padx=6, pady=4)

        # Custom Excel Override
        ttk.Label(page_card, text="Custom Excel (Optional):", style="Card.TLabel").grid(row=3, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        self.custom_excel_var = tk.StringVar(value=self.settings.get("custom_excel", ""))
        entry_custom_excel = ttk.Entry(page_card, textvariable=self.custom_excel_var, width=24)
        entry_custom_excel.grid(row=3, column=2, columnspan=2, sticky="w", padx=6, pady=4)

        self.lbl_send_file = ttk.Label(page_card, text="", style="Sub.TLabel", foreground="#7c3aed")
        self.lbl_send_file.grid(row=4, column=0, columnspan=4, sticky="w", padx=6, pady=4)
        self.update_send_filename_label()

        self.entry_send_from.bind("<KeyRelease>", lambda e: self.update_send_filename_label())
        self.entry_send_to.bind("<KeyRelease>", lambda e: self.update_send_filename_label())
        self.custom_excel_var.trace_add("write", lambda *args: self.update_send_filename_label())

        # Card 2: Contact Form Details & Message Payload
        form_card = ttk.Frame(main_frame, style="WhiteClayCard.TFrame")
        form_card.pack(fill="x", pady=4)

        ttk.Label(form_card, text="Contact Details & Message Payload", style="Header.TLabel").pack(anchor="w", pady=(0, 2))
        ttk.Label(form_card, text="Fill out recipient details and save for future runs.", style="Sub.TLabel").pack(anchor="w", pady=(0, 6))

        # Horizontal Body Container (Left: Contact Details, Right: Message Body)
        body_frame = ttk.Frame(form_card, style="CardInner.TFrame")
        body_frame.pack(fill="x", expand=True, pady=4)

        # LEFT SIDE: Input Fields
        left_frame = ttk.Frame(body_frame, style="CardInner.TFrame")
        left_frame.pack(side="left", fill="y", anchor="n", padx=(0, 16))

        ttk.Label(left_frame, text="First Name:", style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=4, pady=3)
        self.entry_fn = ttk.Entry(left_frame, width=14)
        self.entry_fn.insert(0, self.settings.get("firstName", ""))
        self.entry_fn.grid(row=0, column=1, sticky="w", padx=4, pady=3)

        ttk.Label(left_frame, text="Last Name:", style="Card.TLabel").grid(row=0, column=2, sticky="w", padx=4, pady=3)
        self.entry_ln = ttk.Entry(left_frame, width=14)
        self.entry_ln.insert(0, self.settings.get("lastName", ""))
        self.entry_ln.grid(row=0, column=3, sticky="w", padx=4, pady=3)

        ttk.Label(left_frame, text="Email:", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=4, pady=3)
        self.entry_email = ttk.Entry(left_frame, width=14)
        self.entry_email.insert(0, self.settings.get("email", ""))
        self.entry_email.grid(row=1, column=1, sticky="w", padx=4, pady=3)

        ttk.Label(left_frame, text="Phone:", style="Card.TLabel").grid(row=1, column=2, sticky="w", padx=4, pady=3)
        self.entry_phone = ttk.Entry(left_frame, width=14)
        self.entry_phone.insert(0, self.settings.get("phone", ""))
        self.entry_phone.grid(row=1, column=3, sticky="w", padx=4, pady=3)

        ttk.Label(left_frame, text="Company:", style="Card.TLabel").grid(row=2, column=0, sticky="w", padx=4, pady=3)
        self.entry_company = ttk.Entry(left_frame, width=14)
        self.entry_company.insert(0, self.settings.get("company", ""))
        self.entry_company.grid(row=2, column=1, sticky="w", padx=4, pady=3)

        ttk.Label(left_frame, text="Country:", style="Card.TLabel").grid(row=2, column=2, sticky="w", padx=4, pady=3)
        self.combo_country = ttk.Combobox(left_frame, values=["India", "United States", "Germany", "United Kingdom", "Canada", "Australia"], width=12)
        self.combo_country.set(self.settings.get("country", "India"))
        self.combo_country.grid(row=2, column=3, sticky="w", padx=4, pady=3)

        ttk.Label(left_frame, text="Relationship:", style="Card.TLabel").grid(row=3, column=0, sticky="w", padx=4, pady=3)
        self.combo_rel = ttk.Combobox(left_frame, values=["Prospective Customer", "Customer", "Partner", "Other"], width=12)
        self.combo_rel.set(self.settings.get("relationship", "Prospective Customer"))
        self.combo_rel.grid(row=3, column=1, sticky="w", padx=4, pady=3)

        # RIGHT SIDE: Message Body Textarea (Takes up all remaining space on the right)
        right_frame = ttk.Frame(body_frame, style="CardInner.TFrame")
        right_frame.pack(side="left", fill="both", expand=True)

        ttk.Label(right_frame, text="Message Body:", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.txt_msg = ScrolledText(
            right_frame, 
            height=7, 
            bg=self.c_input_bg, 
            fg=self.c_fg_dark, 
            font=("DejaVu Sans", 9), 
            insertbackground="black",
            relief="flat",
            bd=0
        )
        self.txt_msg.insert("1.0", self.settings.get("message", ""))
        self.txt_msg.pack(fill="both", expand=True)

        # Action Buttons (Clay Pills)
        btn_bar = ttk.Frame(form_card, style="CardInner.TFrame")
        btn_bar.pack(fill="x", pady=(10, 0))

        ttk.Button(btn_bar, text="Save Details", style="DarkVioletClay.TButton", command=lambda: self.save_settings(show_alert=True)).pack(side="left", padx=(0, 5))
        
        self.btn_send_start = ttk.Button(btn_bar, text="Send Invites", style="PurpleClay.TButton", command=self.start_send_invites)
        self.btn_send_start.pack(side="left", padx=5)

        self.btn_send_stop = ttk.Button(btn_bar, text="Stop", style="RoseClay.TButton", command=self.stop_task, state="disabled")
        self.btn_send_stop.pack(side="left", padx=5)

        ttk.Button(btn_bar, text="Clear Log", command=lambda: self.clear_log(self.log_send_invite)).pack(side="left", padx=5)

        # Progress bar
        self.progress_send = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress_send.pack(fill="x", pady=4)

        # --- BOTTOM: LOG CONSOLE SPANNING FULL WIDTH ---
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill="both", expand=True, pady=4)

        ttk.Label(log_frame, text="Live Invites Automation Terminal Log:").pack(anchor="w", pady=(0, 3))
        
        self.log_send_invite = ScrolledText(
            log_frame, 
            bg="#1e1b4b", 
            fg="#f8fafc", 
            font=("Consolas", 10), 
            insertbackground="white",
            relief="flat",
            bd=0
        )
        self.log_send_invite.pack(fill="both", expand=True, pady=3)

    def update_send_filename_label(self):
        custom = self.custom_excel_var.get().strip()
        if custom:
            self.lbl_send_file.config(text=f"Using Custom File: {custom}")
        else:
            f = self.entry_send_from.get().strip()
            t = self.entry_send_to.get().strip()
            self.lbl_send_file.config(text=f"Target Excel File: profile_cards_pages_{f}_to_{t}.xlsx")

    # ================= LOGGING AND THREAD MANAGEMENT =================
    def log(self, text, widget=None):
        """Thread-safe logging helper."""
        self.log_queue.put((widget or self.log_get_links, text))

    def process_log_queue(self):
        """Poll the queue for log messages and update Tkinter widgets safely."""
        while not self.log_queue.empty():
            try:
                target_widget, msg = self.log_queue.get_nowait()
                target_widget.insert(tk.END, msg + "\n")
                target_widget.see(tk.END)
            except queue.Empty:
                break
        self.root.after(100, self.process_log_queue)

    def clear_log(self, widget):
        widget.delete("1.0", tk.END)

    def open_output_dir(self):
        cwd = os.getcwd()
        try:
            if sys.platform == "win32":
                os.startfile(cwd)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", cwd])
            else:
                subprocess.Popen(["xdg-open", cwd])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open directory: {e}")

    # ================= TASK EXECUTIONS =================
    def start_get_links(self):
        try:
            from_page = int(self.entry_get_from.get().strip())
            to_page = int(self.entry_get_to.get().strip())
            if from_page > to_page or from_page < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric page numbers (From <= To and From >= 1).")
            return

        self.save_settings(show_alert=False)
        self.stop_event.clear()
        self.current_task = "get_links"

        self.btn_get_start.config(state="disabled")
        self.btn_get_stop.config(state="normal")
        self.progress_get.start(10)
        self.log_get_links.insert(tk.END, f"=== Starting Link Extraction (Pages {from_page} to {to_page}) ===\n")

        self.running_thread = threading.Thread(
            target=self.worker_get_links,
            args=(from_page, to_page),
            daemon=True
        )
        self.running_thread.start()

    def worker_get_links(self, from_page, to_page):
        try:
            def log_callback(msg):
                self.log(msg, self.log_get_links)

            run_get_links(
                from_page=from_page,
                to_page=to_page,
                log_func=log_callback,
                stop_event=self.stop_event,
                auto_close=True
            )
        except Exception as e:
            self.log(f"\n[FATAL ERROR]: {e}", self.log_get_links)
        finally:
            self.root.after(0, self.on_task_finished, self.btn_get_start, self.btn_get_stop, self.progress_get)

    def start_send_invites(self):
        try:
            from_page = int(self.entry_send_from.get().strip())
            to_page = int(self.entry_send_to.get().strip())
            if from_page > to_page or from_page < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric page numbers (From <= To and From >= 1).")
            return

        details = {
            "firstName": self.entry_fn.get().strip(),
            "lastName": self.entry_ln.get().strip(),
            "email": self.entry_email.get().strip(),
            "phone": self.entry_phone.get().strip(),
            "company": self.entry_company.get().strip(),
            "country": self.combo_country.get().strip(),
            "relationship": self.combo_rel.get().strip(),
            "message": self.txt_msg.get("1.0", tk.END).strip()
        }

        if not details["firstName"] or not details["email"] or not details["message"]:
            messagebox.showerror("Missing Information", "Please fill in First Name, Email, and Message body before proceeding.")
            return

        self.save_settings(show_alert=False)
        self.stop_event.clear()
        self.current_task = "send_invites"

        custom_excel = self.custom_excel_var.get().strip() or None

        self.btn_send_start.config(state="disabled")
        self.btn_send_stop.config(state="normal")
        self.progress_send.start(10)
        self.log_send_invite.insert(tk.END, f"=== Starting Sending Invites (Pages {from_page} to {to_page}) ===\n")

        self.running_thread = threading.Thread(
            target=self.worker_send_invites,
            args=(from_page, to_page, details, custom_excel),
            daemon=True
        )
        self.running_thread.start()

    def worker_send_invites(self, from_page, to_page, details, custom_excel):
        try:
            def log_callback(msg):
                self.log(msg, self.log_send_invite)

            run_send_messages(
                from_page=from_page,
                to_page=to_page,
                details=details,
                log_func=log_callback,
                stop_event=self.stop_event,
                excel_override=custom_excel,
                auto_close=True
            )
        except Exception as e:
            self.log(f"\n[FATAL ERROR]: {e}", self.log_send_invite)
        finally:
            self.root.after(0, self.on_task_finished, self.btn_send_start, self.btn_send_stop, self.progress_send)

    def stop_task(self):
        if self.running_thread and self.running_thread.is_alive():
            self.stop_event.set()
            self.log("Stopping process...", self.log_get_links if self.current_task == "get_links" else self.log_send_invite)

    def on_task_finished(self, start_btn, stop_btn, pbar):
        start_btn.config(state="normal")
        stop_btn.config(state="disabled")
        pbar.stop()
        self.running_thread = None
        self.current_task = None


def main():
    root = tk.Tk()
    app = AutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
