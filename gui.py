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

APP_VERSION = "2.0.0"

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
        self.root.title(f"SAP Partner Finder Suite v{APP_VERSION}")
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
        """Configure TTK styles for Modern White 3D Tactile SaaS Theme."""
        style = ttk.Style()
        style.theme_use("clam")

        # Color Palette - Modern White & Indigo 3D Tactile
        self.c_bg_main = "#f1f5f9"        # Clean Crisp Light Slate/White Canvas
        self.c_card_bg = "#ffffff"        # Pure White Elevated 3D Card Surface
        self.c_fg_primary = "#0f172a"     # Dark Charcoal Text
        self.c_fg_subtle = "#64748b"      # Muted Slate Text
        self.c_input_bg = "#f8fafc"       # Soft White Inset Input Box
        self.c_border = "#cbd5e1"         # Crisp Slate Border

        # Vibrant Accent Palette
        self.c_indigo_btn = "#4f46e5"     # Vivid Indigo (Primary Action)
        self.c_emerald_btn = "#0d9488"    # Emerald Teal (Save Action)
        self.c_rose_btn = "#e11d48"       # Rose Crimson (Stop Action)
        self.c_slate_btn = "#e2e8f0"      # Light Slate (Secondary Utility)

        self.root.configure(bg=self.c_bg_main)

        # Base frame
        style.configure("TFrame", background=self.c_bg_main)

        # Elevated 3D White Card Container Styles
        style.configure("SaaSCard.TFrame", 
                        background=self.c_card_bg, 
                        relief="raised", 
                        borderwidth=2, 
                        lightcolor="#ffffff",
                        darkcolor="#cbd5e1",
                        bordercolor="#cbd5e1",
                        padding=16)

        style.configure("CardInner.TFrame", 
                        background=self.c_card_bg, 
                        relief="flat", 
                        borderwidth=0, 
                        padding=0)

        # Label styles
        style.configure("TLabel", background=self.c_bg_main, foreground=self.c_fg_primary, font=("DejaVu Sans", 10))
        style.configure("Card.TLabel", background=self.c_card_bg, foreground=self.c_fg_primary, font=("DejaVu Sans", 10, "bold"))
        style.configure("Sub.TLabel", background=self.c_card_bg, foreground=self.c_fg_subtle, font=("DejaVu Sans", 9))
        style.configure("Header.TLabel", background=self.c_card_bg, foreground=self.c_fg_primary, font=("DejaVu Sans", 12, "bold"))
        style.configure("Title.TLabel", background=self.c_bg_main, foreground=self.c_fg_primary, font=("DejaVu Sans", 17, "bold"))

        # Inset 3D Entry and Combobox styling
        style.configure("TEntry", 
                        fieldbackground=self.c_input_bg, 
                        foreground=self.c_fg_primary, 
                        bordercolor=self.c_border,
                        lightcolor="#94a3b8",
                        darkcolor="#e2e8f0",
                        relief="sunken",
                        padding=6)
        
        style.configure("TCombobox", 
                        fieldbackground=self.c_input_bg, 
                        background=self.c_card_bg,
                        foreground=self.c_fg_primary, 
                        bordercolor=self.c_border,
                        padding=6)
        style.map("TCombobox", fieldbackground=[("readonly", self.c_input_bg)], foreground=[("readonly", self.c_fg_primary)])

        # Progressbar
        style.configure("Horizontal.TProgressbar", 
                        troughcolor="#e2e8f0", 
                        background=self.c_indigo_btn, 
                        bordercolor=self.c_border,
                        lightcolor=self.c_indigo_btn,
                        darkcolor=self.c_indigo_btn)

        # Button Styles (3D Tactile Felt Buttons)
        style.configure("Indigo.TButton", 
                        background=self.c_indigo_btn, 
                        foreground="#ffffff", 
                        font=("DejaVu Sans", 10, "bold"), 
                        relief="raised", 
                        borderwidth=2,
                        lightcolor="#818cf8",
                        darkcolor="#3730a3",
                        padding=[14, 7])
        style.map("Indigo.TButton", background=[("active", "#4338ca"), ("disabled", "#cbd5e1")])

        style.configure("Emerald.TButton", 
                        background=self.c_emerald_btn, 
                        foreground="#ffffff", 
                        font=("DejaVu Sans", 10, "bold"), 
                        relief="raised", 
                        borderwidth=2,
                        lightcolor="#2dd4bf",
                        darkcolor="#115e59",
                        padding=[14, 7])
        style.map("Emerald.TButton", background=[("active", "#0f766e"), ("disabled", "#cbd5e1")])

        style.configure("Rose.TButton", 
                        background=self.c_rose_btn, 
                        foreground="#ffffff", 
                        font=("DejaVu Sans", 10, "bold"), 
                        relief="raised", 
                        borderwidth=2,
                        lightcolor="#fb7185",
                        darkcolor="#9f1239",
                        padding=[14, 7])
        style.map("Rose.TButton", background=[("active", "#be123c"), ("disabled", "#cbd5e1")])

        style.configure("Slate.TButton", 
                        background=self.c_slate_btn, 
                        foreground="#334155", 
                        font=("DejaVu Sans", 9, "bold"), 
                        relief="raised", 
                        borderwidth=2,
                        lightcolor="#ffffff",
                        darkcolor="#94a3b8",
                        padding=[10, 6])
        style.map("Slate.TButton", background=[("active", "#cbd5e1")])

        style.configure("TButton", 
                        background="#f1f5f9", 
                        foreground="#334155", 
                        font=("DejaVu Sans", 9, "bold"), 
                        padding=5)
        style.map("TButton", background=[("active", "#e2e8f0")])

    def create_widgets(self):
        # Top Header Banner Frame (Tighter top padding to move elements UP)
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=24, pady=(10, 2))

        title_box = ttk.Frame(header_frame)
        title_box.pack(side="left")

        ttk.Label(title_box, text=f"SAP Partner Finder Suite v{APP_VERSION}", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_box, text="Extract target profile links and dispatch message invites seamlessly.", style="TLabel", foreground="#64748b").pack(anchor="w")

        # --- 3D SEGMENTED TAB SWITCHER ---
        nav_bar_frame = ttk.Frame(self.root)
        nav_bar_frame.pack(fill="x", padx=24, pady=(6, 2))

        # Sunken 3D segment track container
        nav_track = tk.Frame(nav_bar_frame, bg="#e2e8f0", padx=4, pady=4, relief="sunken", bd=2)
        nav_track.pack(side="left")

        self.tab_btn_get_links = tk.Button(
            nav_track, 
            text="Get Links", 
            font=("DejaVu Sans", 10, "bold"),
            bd=2, 
            relief="raised", 
            padx=22, 
            pady=7,
            cursor="hand2",
            command=lambda: self.switch_tab("get_links")
        )
        self.tab_btn_get_links.pack(side="left", padx=2)

        self.tab_btn_send_invite = tk.Button(
            nav_track, 
            text="Sending Invite", 
            font=("DejaVu Sans", 10, "bold"),
            bd=2, 
            relief="raised", 
            padx=22, 
            pady=7,
            cursor="hand2",
            command=lambda: self.switch_tab("send_invite")
        )
        self.tab_btn_send_invite.pack(side="left", padx=2)

        # Content Container Frame
        self.content_container = ttk.Frame(self.root)
        self.content_container.pack(fill="both", expand=True, padx=24, pady=(4, 12))

        self.tab_get_links = ttk.Frame(self.content_container)
        self.tab_send_invite = ttk.Frame(self.content_container)

        self.build_get_links_tab()
        self.build_send_invite_tab()

        # Default Active Tab
        self.switch_tab("get_links")

    def switch_tab(self, tab_name):
        """Switch active tab content and update 3D Pill Segmented Switcher styling."""
        self.tab_get_links.pack_forget()
        self.tab_send_invite.pack_forget()

        active_bg = "#4f46e5"   # Vivid Indigo 3D Active Pill
        active_fg = "#ffffff"   # White Text
        inactive_bg = "#ffffff" # Elevated White Inactive Pill
        inactive_fg = "#475569" # Slate Text

        if tab_name == "get_links":
            self.tab_btn_get_links.config(bg=active_bg, fg=active_fg, relief="raised", bd=2, activebackground=active_bg, activeforeground=active_fg)
            self.tab_btn_send_invite.config(bg=inactive_bg, fg=inactive_fg, relief="flat", bd=0, activebackground="#f1f5f9", activeforeground="#0f172a")
            self.tab_get_links.pack(fill="both", expand=True)
        else:
            self.tab_btn_send_invite.config(bg=active_bg, fg=active_fg, relief="raised", bd=2, activebackground=active_bg, activeforeground=active_fg)
            self.tab_btn_get_links.config(bg=inactive_bg, fg=inactive_fg, relief="flat", bd=0, activebackground="#f1f5f9", activeforeground="#0f172a")
            self.tab_send_invite.pack(fill="both", expand=True)

    # ================= TAB 1: GET LINKS =================
    def build_get_links_tab(self):
        main_frame = ttk.Frame(self.tab_get_links)
        main_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # 3D Elevated White Card: Controls
        ctrl_card = ttk.Frame(main_frame, style="SaaSCard.TFrame")
        ctrl_card.pack(fill="x", pady=6)

        ttk.Label(ctrl_card, text="Link Extraction Parameters", style="Header.TLabel").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 2))
        ttk.Label(ctrl_card, text="Configure target search page range to extract profile cards into Excel.", style="Sub.TLabel").grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 10))

        ttk.Label(ctrl_card, text="From Page:", style="Card.TLabel").grid(row=2, column=0, sticky="w", padx=6, pady=5)
        self.entry_get_from = ttk.Entry(ctrl_card, width=10)
        self.entry_get_from.insert(0, str(self.settings.get("get_links_from", 158)))
        self.entry_get_from.grid(row=2, column=1, sticky="w", padx=6, pady=5)

        ttk.Label(ctrl_card, text="To Page:", style="Card.TLabel").grid(row=2, column=2, sticky="w", padx=6, pady=5)
        self.entry_get_to = ttk.Entry(ctrl_card, width=10)
        self.entry_get_to.insert(0, str(self.settings.get("get_links_to", 159)))
        self.entry_get_to.grid(row=2, column=3, sticky="w", padx=6, pady=5)

        # Target Excel Output Display
        self.lbl_get_file = ttk.Label(ctrl_card, text="", style="Sub.TLabel", foreground="#4f46e5")
        self.lbl_get_file.grid(row=3, column=0, columnspan=4, sticky="w", padx=6, pady=5)
        self.update_get_filename_label()

        self.entry_get_from.bind("<KeyRelease>", lambda e: self.update_get_filename_label())
        self.entry_get_to.bind("<KeyRelease>", lambda e: self.update_get_filename_label())

        # Action Buttons Bar
        btn_frame = ttk.Frame(ctrl_card, style="CardInner.TFrame")
        btn_frame.grid(row=4, column=0, columnspan=4, sticky="w", pady=(10, 0))

        self.btn_get_start = ttk.Button(btn_frame, text="Start Get Links", style="Indigo.TButton", command=self.start_get_links)
        self.btn_get_start.pack(side="left", padx=(0, 6))

        self.btn_get_stop = ttk.Button(btn_frame, text="Stop Process", style="Rose.TButton", command=self.stop_task, state="disabled")
        self.btn_get_stop.pack(side="left", padx=6)

        ttk.Button(btn_frame, text="Clear Log", style="Slate.TButton", command=lambda: self.clear_log(self.log_get_links)).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Open Folder", style="Slate.TButton", command=self.open_output_dir).pack(side="left", padx=6)

        # Progress bar
        self.progress_get = ttk.Progressbar(main_frame, mode="indeterminate", style="Horizontal.TProgressbar")
        self.progress_get.pack(fill="x", pady=6)

        # Log Console Container with 3D Bevel and macOS Terminal Bar Header
        log_card = tk.Frame(main_frame, bg="#0f172a", relief="sunken", bd=3)
        log_card.pack(fill="both", expand=True, pady=4)

        term_bar = tk.Frame(log_card, bg="#1e293b", padx=10, pady=5)
        term_bar.pack(fill="x")
        
        dots_frame = tk.Frame(term_bar, bg="#1e293b")
        dots_frame.pack(side="left")
        tk.Label(dots_frame, text="●", fg="#ef4444", bg="#1e293b", font=("DejaVu Sans", 10)).pack(side="left", padx=2)
        tk.Label(dots_frame, text="●", fg="#f59e0b", bg="#1e293b", font=("DejaVu Sans", 10)).pack(side="left", padx=2)
        tk.Label(dots_frame, text="●", fg="#10b981", bg="#1e293b", font=("DejaVu Sans", 10)).pack(side="left", padx=2)

        tk.Label(term_bar, text="LIVE EXTRACTION TERMINAL LOG", bg="#1e293b", fg="#94a3b8", font=("DejaVu Sans", 8, "bold")).pack(side="left", padx=10)

        self.log_get_links = ScrolledText(
            log_card, 
            bg="#020617", 
            fg="#38bdf8", 
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
        main_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # Card 1: Page Range & Excel Source
        page_card = ttk.Frame(main_frame, style="SaaSCard.TFrame")
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

        self.lbl_send_file = ttk.Label(page_card, text="", style="Sub.TLabel", foreground="#4f46e5")
        self.lbl_send_file.grid(row=4, column=0, columnspan=4, sticky="w", padx=6, pady=4)
        self.update_send_filename_label()

        self.entry_send_from.bind("<KeyRelease>", lambda e: self.update_send_filename_label())
        self.entry_send_to.bind("<KeyRelease>", lambda e: self.update_send_filename_label())
        self.custom_excel_var.trace_add("write", lambda *args: self.update_send_filename_label())

        # Card 2: Contact Form Details & Message Payload
        form_card = ttk.Frame(main_frame, style="SaaSCard.TFrame")
        form_card.pack(fill="x", pady=4)

        ttk.Label(form_card, text="Contact Details & Message Payload", style="Header.TLabel").pack(anchor="w", pady=(0, 2))
        ttk.Label(form_card, text="Fill out recipient details and save for future runs.", style="Sub.TLabel").pack(anchor="w", pady=(0, 6))

        # Horizontal Body Container
        body_frame = ttk.Frame(form_card, style="CardInner.TFrame")
        body_frame.pack(fill="x", expand=True, pady=4)

        # LEFT SIDE: Input Fields
        left_frame = ttk.Frame(body_frame, style="CardInner.TFrame")
        left_frame.pack(side="left", fill="y", anchor="n", padx=(0, 24))

        ttk.Label(left_frame, text="First Name:", style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=4, pady=3)
        self.entry_fn = ttk.Entry(left_frame, width=20)
        self.entry_fn.insert(0, self.settings.get("firstName", ""))
        self.entry_fn.grid(row=0, column=1, sticky="w", padx=4, pady=3)

        ttk.Label(left_frame, text="Last Name:", style="Card.TLabel").grid(row=0, column=2, sticky="w", padx=4, pady=3)
        self.entry_ln = ttk.Entry(left_frame, width=20)
        self.entry_ln.insert(0, self.settings.get("lastName", ""))
        self.entry_ln.grid(row=0, column=3, sticky="w", padx=4, pady=3)

        ttk.Label(left_frame, text="Email:", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=4, pady=3)
        self.entry_email = ttk.Entry(left_frame, width=20)
        self.entry_email.insert(0, self.settings.get("email", ""))
        self.entry_email.grid(row=1, column=1, sticky="w", padx=4, pady=3)

        ttk.Label(left_frame, text="Phone:", style="Card.TLabel").grid(row=1, column=2, sticky="w", padx=4, pady=3)
        self.entry_phone = ttk.Entry(left_frame, width=20)
        self.entry_phone.insert(0, self.settings.get("phone", ""))
        self.entry_phone.grid(row=1, column=3, sticky="w", padx=4, pady=3)

        ttk.Label(left_frame, text="Company:", style="Card.TLabel").grid(row=2, column=0, sticky="w", padx=4, pady=3)
        self.entry_company = ttk.Entry(left_frame, width=20)
        self.entry_company.insert(0, self.settings.get("company", ""))
        self.entry_company.grid(row=2, column=1, sticky="w", padx=4, pady=3)

        ttk.Label(left_frame, text="Country:", style="Card.TLabel").grid(row=2, column=2, sticky="w", padx=4, pady=3)
        self.combo_country = ttk.Combobox(left_frame, values=["India", "United States", "Germany", "United Kingdom", "Canada", "Australia"], width=18)
        self.combo_country.set(self.settings.get("country", "India"))
        self.combo_country.grid(row=2, column=3, sticky="w", padx=4, pady=3)

        ttk.Label(left_frame, text="Relationship:", style="Card.TLabel").grid(row=3, column=0, sticky="w", padx=4, pady=3)
        self.combo_rel = ttk.Combobox(left_frame, values=["Prospective Customer", "Customer", "Partner", "Other"], width=18)
        self.combo_rel.set(self.settings.get("relationship", "Prospective Customer"))
        self.combo_rel.grid(row=3, column=1, sticky="w", padx=4, pady=3)

        # RIGHT SIDE: Message Body Textarea (3D Sunken Box)
        right_frame = ttk.Frame(body_frame, style="CardInner.TFrame")
        right_frame.pack(side="left", fill="both", expand=True)

        ttk.Label(right_frame, text="Message Body:", style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        self.txt_msg = ScrolledText(
            right_frame, 
            height=7, 
            bg=self.c_input_bg, 
            fg=self.c_fg_primary, 
            font=("DejaVu Sans", 9), 
            insertbackground="black",
            relief="sunken",
            bd=2
        )
        self.txt_msg.insert("1.0", self.settings.get("message", ""))
        self.txt_msg.pack(fill="both", expand=True)

        # Action Buttons
        btn_bar = ttk.Frame(form_card, style="CardInner.TFrame")
        btn_bar.pack(fill="x", pady=(10, 0))

        ttk.Button(btn_bar, text="Save Details", style="Emerald.TButton", command=lambda: self.save_settings(show_alert=True)).pack(side="left", padx=(0, 6))
        
        self.btn_send_start = ttk.Button(btn_bar, text="Send Invites", style="Indigo.TButton", command=self.start_send_invites)
        self.btn_send_start.pack(side="left", padx=6)

        self.btn_send_stop = ttk.Button(btn_bar, text="Stop Process", style="Rose.TButton", command=self.stop_task, state="disabled")
        self.btn_send_stop.pack(side="left", padx=6)

        ttk.Button(btn_bar, text="Clear Log", style="Slate.TButton", command=lambda: self.clear_log(self.log_send_invite)).pack(side="left", padx=6)

        # Progress bar
        self.progress_send = ttk.Progressbar(main_frame, mode="indeterminate", style="Horizontal.TProgressbar")
        self.progress_send.pack(fill="x", pady=(6, 2))

        # --- LOG CONSOLE SPANNING FULL WIDTH (Pushed further down) ---
        log_card = tk.Frame(main_frame, bg="#0f172a", relief="sunken", bd=3)
        log_card.pack(fill="both", expand=True, pady=(16, 6))

        term_bar = tk.Frame(log_card, bg="#1e293b", padx=10, pady=5)
        term_bar.pack(fill="x")
        
        dots_frame = tk.Frame(term_bar, bg="#1e293b")
        dots_frame.pack(side="left")
        tk.Label(dots_frame, text="●", fg="#ef4444", bg="#1e293b", font=("DejaVu Sans", 10)).pack(side="left", padx=2)
        tk.Label(dots_frame, text="●", fg="#f59e0b", bg="#1e293b", font=("DejaVu Sans", 10)).pack(side="left", padx=2)
        tk.Label(dots_frame, text="●", fg="#10b981", bg="#1e293b", font=("DejaVu Sans", 10)).pack(side="left", padx=2)

        tk.Label(term_bar, text="LIVE INVITES AUTOMATION LOG", bg="#1e293b", fg="#94a3b8", font=("DejaVu Sans", 8, "bold")).pack(side="left", padx=10)

        self.log_send_invite = ScrolledText(
            log_card, 
            bg="#020617", 
            fg="#22c55e", 
            font=("Consolas", 10), 
            insertbackground="white",
            relief="flat",
            bd=0
        )
        self.log_send_invite.pack(fill="both", expand=True)

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
