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

# Import our automation functions
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
        self.root.title("SAP Automation Suite - Get Links & Send Invites")
        self.root.geometry("900x750")
        self.root.minsize(800, 650)

        # Threading and Queues
        self.log_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.running_thread = None
        self.current_task = None  # 'get_links' or 'send_invites'

        # Settings
        self.settings = self.load_settings()

        # Build UI
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
                    # Merge loaded data with defaults in case new fields were added
                    merged = DEFAULT_SETTINGS.copy()
                    merged.update(data)
                    return merged
            except Exception as e:
                print(f"Error loading settings file: {e}")
        return DEFAULT_SETTINGS.copy()

    def save_settings(self, show_alert=False):
        """Save current form state and settings to JSON file."""
        # Update settings dict from GUI fields
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
                messagebox.showinfo("Success", "Settings and details saved successfully for future use!")
        except Exception as e:
            if show_alert:
                messagebox.showerror("Error", f"Could not save settings: {e}")

    def apply_theme(self):
        """Configure ttk styles for a modern aesthetic."""
        style = ttk.Style()
        style.theme_use("clam")

        # Color palette
        bg_dark = "#2b2b2b"
        card_bg = "#3c3f41"
        fg_white = "#ffffff"
        accent_blue = "#2196F3"
        accent_green = "#4CAF50"
        accent_red = "#F44336"

        self.root.configure(bg=bg_dark)

        # Style configurations
        style.configure("TFrame", background=bg_dark)
        style.configure("Card.TFrame", background=card_bg, relief="flat", padding=10)
        
        style.configure("TNotebook", background=bg_dark, borderwidth=0)
        style.configure("TNotebook.Tab", background="#505050", foreground="#ffffff", padding=[15, 8], font=("Helvetica", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", accent_blue)], foreground=[("selected", "#ffffff")])

        style.configure("TLabel", background=bg_dark, foreground="#e0e0e0", font=("Helvetica", 10))
        style.configure("Card.TLabel", background=card_bg, foreground="#ffffff", font=("Helvetica", 10))
        style.configure("Header.TLabel", background=card_bg, foreground="#ffffff", font=("Helvetica", 12, "bold"))
        style.configure("Title.TLabel", background=bg_dark, foreground="#ffffff", font=("Helvetica", 14, "bold"))

        style.configure("Accent.TButton", background=accent_green, foreground="#ffffff", font=("Helvetica", 10, "bold"), padding=6)
        style.map("Accent.TButton", background=[("active", "#45a049"), ("disabled", "#7d7d7d")])

        style.configure("Blue.TButton", background=accent_blue, foreground="#ffffff", font=("Helvetica", 10, "bold"), padding=6)
        style.map("Blue.TButton", background=[("active", "#1e88e5"), ("disabled", "#7d7d7d")])

        style.configure("Stop.TButton", background=accent_red, foreground="#ffffff", font=("Helvetica", 10, "bold"), padding=6)
        style.map("Stop.TButton", background=[("active", "#d32f2f"), ("disabled", "#7d7d7d")])

        style.configure("TButton", padding=6)

    def create_widgets(self):
        # Top Title Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=15, pady=10)
        ttk.Label(header_frame, text="SAP Partner Finder Automation Suite", style="Title.TLabel").pack(side="left")

        # Notebook Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=5)

        # Tab 1: Get Links
        self.tab_get_links = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_get_links, text=" Get Links ")

        # Tab 2: Sending Invite
        self.tab_send_invite = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_send_invite, text=" Sending Invite ")

        self.build_get_links_tab()
        self.build_send_invite_tab()

    # ================= TAB 1: GET LINKS =================
    def build_get_links_tab(self):
        main_frame = ttk.Frame(self.tab_get_links)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Card: Controls
        ctrl_card = ttk.Frame(main_frame, style="Card.TFrame")
        ctrl_card.pack(fill="x", pady=5)

        ttk.Label(ctrl_card, text="1. Extract Links Settings", style="Header.TLabel").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        ttk.Label(ctrl_card, text="From Page:", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_get_from = ttk.Entry(ctrl_card, width=10)
        self.entry_get_from.insert(0, str(self.settings.get("get_links_from", 158)))
        self.entry_get_from.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(ctrl_card, text="To Page:", style="Card.TLabel").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.entry_get_to = ttk.Entry(ctrl_card, width=10)
        self.entry_get_to.insert(0, str(self.settings.get("get_links_to", 159)))
        self.entry_get_to.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Expected file label
        self.lbl_get_file = ttk.Label(ctrl_card, text="", style="Card.TLabel", foreground="#64b5f6")
        self.lbl_get_file.grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=5)
        self.update_get_filename_label()

        self.entry_get_from.bind("<KeyRelease>", lambda e: self.update_get_filename_label())
        self.entry_get_to.bind("<KeyRelease>", lambda e: self.update_get_filename_label())

        # Buttons bar
        btn_frame = ttk.Frame(ctrl_card, style="Card.TFrame")
        btn_frame.grid(row=3, column=0, columnspan=4, sticky="w", pady=10)

        self.btn_get_start = ttk.Button(btn_frame, text="Get Links", style="Accent.TButton", command=self.start_get_links)
        self.btn_get_start.pack(side="left", padx=5)

        self.btn_get_stop = ttk.Button(btn_frame, text="Stop", style="Stop.TButton", command=self.stop_task, state="disabled")
        self.btn_get_stop.pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Clear Log", command=lambda: self.clear_log(self.log_get_links)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Open Folder", command=self.open_output_dir).pack(side="left", padx=5)

        # Progress bar
        self.progress_get = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress_get.pack(fill="x", pady=5)

        # Log Console
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill="both", expand=True, pady=5)

        ttk.Label(log_frame, text="Live Progress Log:").pack(anchor="w")
        self.log_get_links = ScrolledText(log_frame, bg="#1e1e1e", fg="#d4d4d4", font=("Monospace", 9), insertbackground="white")
        self.log_get_links.pack(fill="both", expand=True)

    def update_get_filename_label(self):
        f = self.entry_get_from.get().strip()
        t = self.entry_get_to.get().strip()
        self.lbl_get_file.config(text=f"Output Excel File: profile_cards_pages_{f}_to_{t}.xlsx")

    # ================= TAB 2: SENDING INVITE =================
    def build_send_invite_tab(self):
        # Create a container canvas + scrollbar if window size is small
        container = ttk.Frame(self.tab_send_invite)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Left Column: Form & Settings / Right Column: Log
        paned = ttk.PanedWindow(container, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left_frame = ttk.Frame(paned)
        right_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        paned.add(right_frame, weight=1)

        # --- LEFT SIDE: CONFIG & DETAILS FORM ---
        # Card 1: Page Range & Excel Source
        page_card = ttk.Frame(left_frame, style="Card.TFrame")
        page_card.pack(fill="x", pady=5)

        ttk.Label(page_card, text="1. Target Excel File Selection", style="Header.TLabel").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 5))

        ttk.Label(page_card, text="From Page:", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_send_from = ttk.Entry(page_card, width=8)
        self.entry_send_from.insert(0, str(self.settings.get("send_invite_from", 158)))
        self.entry_send_from.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(page_card, text="To Page:", style="Card.TLabel").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.entry_send_to = ttk.Entry(page_card, width=8)
        self.entry_send_to.insert(0, str(self.settings.get("send_invite_to", 159)))
        self.entry_send_to.grid(row=1, column=3, sticky="w", padx=5, pady=2)

        # Custom Excel Override option
        ttk.Label(page_card, text="Custom Excel File (Optional):", style="Card.TLabel").grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        self.custom_excel_var = tk.StringVar(value=self.settings.get("custom_excel", ""))
        entry_custom_excel = ttk.Entry(page_card, textvariable=self.custom_excel_var, width=25)
        entry_custom_excel.grid(row=2, column=2, columnspan=2, sticky="w", padx=5, pady=2)

        self.lbl_send_file = ttk.Label(page_card, text="", style="Card.TLabel", foreground="#64b5f6")
        self.lbl_send_file.grid(row=3, column=0, columnspan=4, sticky="w", padx=5, pady=4)
        self.update_send_filename_label()

        self.entry_send_from.bind("<KeyRelease>", lambda e: self.update_send_filename_label())
        self.entry_send_to.bind("<KeyRelease>", lambda e: self.update_send_filename_label())
        self.custom_excel_var.trace_add("write", lambda *args: self.update_send_filename_label())

        # Card 2: Form Details
        form_card = ttk.Frame(left_frame, style="Card.TFrame")
        form_card.pack(fill="both", expand=True, pady=5)

        ttk.Label(form_card, text="2. Contact Details & Message", style="Header.TLabel").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 5))

        # Fields
        ttk.Label(form_card, text="First Name:", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_fn = ttk.Entry(form_card, width=18)
        self.entry_fn.insert(0, self.settings.get("firstName", "Kiran"))
        self.entry_fn.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(form_card, text="Last Name:", style="Card.TLabel").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.entry_ln = ttk.Entry(form_card, width=18)
        self.entry_ln.insert(0, self.settings.get("lastName", "K"))
        self.entry_ln.grid(row=1, column=3, sticky="w", padx=5, pady=2)

        ttk.Label(form_card, text="Email:", style="Card.TLabel").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.entry_email = ttk.Entry(form_card, width=18)
        self.entry_email.insert(0, self.settings.get("email", "kiran@gesoftech.com"))
        self.entry_email.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(form_card, text="Phone:", style="Card.TLabel").grid(row=2, column=2, sticky="w", padx=5, pady=2)
        self.entry_phone = ttk.Entry(form_card, width=18)
        self.entry_phone.insert(0, self.settings.get("phone", " 4"))
        self.entry_phone.grid(row=2, column=3, sticky="w", padx=5, pady=2)

        ttk.Label(form_card, text="Company:", style="Card.TLabel").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.entry_company = ttk.Entry(form_card, width=18)
        self.entry_company.insert(0, self.settings.get("company", " Softech"))
        self.entry_company.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(form_card, text="Country:", style="Card.TLabel").grid(row=3, column=2, sticky="w", padx=5, pady=2)
        self.combo_country = ttk.Combobox(form_card, values=["India", "United States", "Germany", "United Kingdom", "Canada", "Australia"], width=16)
        self.combo_country.set(self.settings.get("country", "India"))
        self.combo_country.grid(row=3, column=3, sticky="w", padx=5, pady=2)

        ttk.Label(form_card, text="Relationship:", style="Card.TLabel").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.combo_rel = ttk.Combobox(form_card, values=["Prospective Customer", "Customer", "Partner", "Other"], width=16)
        self.combo_rel.set(self.settings.get("relationship", "Prospective Customer"))
        self.combo_rel.grid(row=4, column=1, sticky="w", padx=5, pady=2)

        # Message Text Box
        ttk.Label(form_card, text="Message Body:", style="Card.TLabel").grid(row=5, column=0, columnspan=4, sticky="w", padx=5, pady=(5, 2))
        self.txt_msg = ScrolledText(form_card, height=8, width=45, font=("Helvetica", 9))
        self.txt_msg.insert("1.0", self.settings.get("message", DEFAULT_SETTINGS["message"]))
        self.txt_msg.grid(row=6, column=0, columnspan=4, sticky="nsew", padx=5, pady=2)

        # Action Buttons
        btn_bar = ttk.Frame(form_card, style="Card.TFrame")
        btn_bar.grid(row=7, column=0, columnspan=4, sticky="w", pady=10)

        ttk.Button(btn_bar, text="Save Details", command=lambda: self.save_settings(show_alert=True)).pack(side="left", padx=4)
        
        self.btn_send_start = ttk.Button(btn_bar, text="Send Invites", style="Accent.TButton", command=self.start_send_invites)
        self.btn_send_start.pack(side="left", padx=4)

        self.btn_send_stop = ttk.Button(btn_bar, text="Stop", style="Stop.TButton", command=self.stop_task, state="disabled")
        self.btn_send_stop.pack(side="left", padx=4)

        # --- RIGHT SIDE: LOG CONSOLE ---
        right_box = ttk.Frame(right_frame)
        right_box.pack(fill="both", expand=True, padx=5)

        ttk.Label(right_box, text="Live Invites Output Log:").pack(anchor="w", pady=(0, 2))
        
        self.progress_send = ttk.Progressbar(right_box, mode="indeterminate")
        self.progress_send.pack(fill="x", pady=2)

        self.log_send_invite = ScrolledText(right_box, bg="#1e1e1e", fg="#d4d4d4", font=("Monospace", 9), insertbackground="white")
        self.log_send_invite.pack(fill="both", expand=True, pady=2)

        ttk.Button(right_box, text="Clear Log", command=lambda: self.clear_log(self.log_send_invite)).pack(anchor="e", pady=5)

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
        """Poll the queue for log messages and update Tkinter widgets in main thread."""
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

        # Launch thread
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

        # Prepare details dictionary
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

        # Check required fields
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

        # Launch thread
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
