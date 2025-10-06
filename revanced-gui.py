import os
import threading
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import subprocess
import json
from datetime import datetime
import webbrowser

from CTkMessagebox import CTkMessagebox

SETTINGS_FILE = "settings.json"

ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"


class CTkToolTip:
    def __init__(self, widget, text, delay=300):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.delay = delay  # delay in ms before showing tooltip
        self.after_id = None
        widget.bind("<Enter>", self.schedule_tip)
        widget.bind("<Leave>", self.hide_tip)
        widget.bind("<ButtonPress>", self.hide_tip)  # hide on click

    def schedule_tip(self, event=None):
        self.after_id = self.widget.after(self.delay, self.show_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        # Detect CTk appearance mode
        appearance = ctk.get_appearance_mode()
        bg_color = "#2b2b2b" if appearance == "Dark" else "#f0f0f0"
        fg_color = "#ffffff" if appearance == "Dark" else "#000000"

        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background=bg_color,
            foreground=fg_color,
            relief=tk.SOLID,
            borderwidth=1,
            font=("Arial", 10),
            padx=5,
            pady=2
        )
        label.pack()

    def hide_tip(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)


def get_unique_filename(filepath):
    if not os.path.exists(filepath):
        return filepath
    base, ext = os.path.splitext(filepath)
    i = 1
    while os.path.exists(f"{base} ({i}){ext}"):
        i += 1
    return f"{base} ({i}){ext}"


def select_cli_path():
    path = filedialog.askopenfilename(filetypes=[("ReVanced CLI", "*.jar"), ("All files", "*.*")])
    if path:
        cli_var.set(path)
        if settings.get("remember_paths", True):
            settings["cli_path"] = path
            save_settings()


def select_rvp_path():
    path = filedialog.askopenfilename(filetypes=[("ReVanced Patch File", "*.rvp"), ("All files", "*.*")])
    if path:
        rvp_var.set(path)
        if settings.get("remember_paths", True):
            settings["rvp_path"] = path
            save_settings()


def select_apk_path():
    path = filedialog.askopenfilename(filetypes=[("APK Files", "*.apk"), ("All files", "*.*")])
    if path:
        apk_var.set(path)


def select_output_folder():
    path = filedialog.askdirectory()
    if path:
        output_var.set(path)
        if settings.get("remember_paths", True):
            settings["output_folder"] = path
            save_settings()


def open_revanced_downloads(url):
    webbrowser.open(url)


def run_patch():
    cli_path = cli_var.get()
    rvp_path = rvp_var.get()
    apk_path = apk_var.get()
    output_dir = output_var.get().strip() or os.getcwd()

    if not all([cli_path, rvp_path, apk_path]):
        CTkMessagebox(title="Error", message="Please select CLI, RVP, and APK files first.", icon="cancel")
        return

    base_name = os.path.basename(apk_path)
    output_file = os.path.join(output_dir, base_name.replace(".apk", "-revanced.apk"))
    output_file = get_unique_filename(output_file)

    cmd_str = f'java -jar "{cli_path}" patch -p "{rvp_path}" "{apk_path}" -o "{output_file}"'

    patch_button.configure(state="disabled", text="Patching...")
    progress_bar.start()
    log_output.configure(state="normal")
    log_output.delete("1.0", "end")
    log_output.insert("end", "ReVanced GUI by chamindudilsh\n\n")
    log_output.insert("end", f"Running: {cmd_str}\n\n")
    log_output.configure(state="disabled")

    def run():
        try:
            process = subprocess.Popen(cmd_str, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
            log_text = ""
            for line in iter(process.stdout.readline, ""):
                log_text += line
                log_output.configure(state="normal")
                log_output.insert("end", line)
                log_output.see("end")
                log_output.configure(state="disabled")
            exit_code = process.wait()

            full_log_text = f"ReVanced GUI by chamindudilsh\n\nRunning: {cmd_str}\n\n{log_text}"

            if settings.get("save_logs", False):
                log_dir = settings.get("log_folder", os.getcwd())
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(full_log_text)

            if exit_code == 0:
                CTkMessagebox(title="Success", message=f"Patching completed successfully!\nSaved as:\n{output_file}", icon="check")
            else:
                CTkMessagebox(title="Error", message=f"Patching failed with exit code: {exit_code}.\nSee logs for details.", icon="cancel")

        except Exception as e:
            CTkMessagebox(title="Error", message=str(e), icon="cancel")
        finally:
            progress_bar.stop()
            progress_bar.set(0)
            patch_button.configure(state="normal", text="Patch")

    threading.Thread(target=run, daemon=True).start()


def open_settings():
    s_win = ctk.CTkToplevel(root)
    s_win.title("Settings")
    s_win.geometry("450x350")
    s_win.resizable(False, False)
    s_win.grab_set()

    tabview = ctk.CTkTabview(s_win)
    tabview.pack(pady=10, padx=10, fill="both", expand=True)
    tabview.add("Settings")
    tabview.add("About")

    # Settings Tab
    settings_frame = tabview.tab("Settings")

    def toggle_remember_paths():
        settings["remember_paths"] = remember_paths_var.get()
        save_settings()

    def toggle_save_logs():
        settings["save_logs"] = save_logs_var.get()
        save_settings()

    def set_logs_folder():
        path = filedialog.askdirectory()
        if path:
            settings["log_folder"] = path
            save_settings()
            CTkMessagebox(title="Logs Folder", message=f"Logs folder set to:\n{path}")

    def open_logs_folder():
        log_folder = settings.get("log_folder", os.getcwd())
        if os.path.exists(log_folder):
            os.startfile(log_folder)
        else:
            CTkMessagebox(title="Warning", message="Log folder not set or missing.", icon="warning")

    remember_paths_var = ctk.BooleanVar(value=settings.get("remember_paths", True))
    ctk.CTkCheckBox(settings_frame, text="Remember last used paths", variable=remember_paths_var, command=toggle_remember_paths).pack(anchor='w', pady=10, padx=10)

    save_logs_var = ctk.BooleanVar(value=settings.get("save_logs", False))
    ctk.CTkCheckBox(settings_frame, text="Save patch logs to folder", variable=save_logs_var, command=toggle_save_logs).pack(anchor='w', padx=10)

    log_folder_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
    log_folder_frame.pack(fill='x', pady=10, padx=10)
    ctk.CTkButton(log_folder_frame, text="Set Logs Folder", command=set_logs_folder).pack(side='left', expand=True, fill='x', padx=(0, 5))
    ctk.CTkButton(log_folder_frame, text="Open Logs Folder", command=open_logs_folder).pack(side='left', expand=True, fill='x', padx=(5, 0))

    theme_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
    theme_frame.pack(fill='x', pady=10, padx=10)
    ctk.CTkLabel(theme_frame, text="Theme:").pack(side='left')
    appearance_mode_menu = ctk.CTkOptionMenu(theme_frame, values=["Light", "Dark", "System"], command=ctk.set_appearance_mode)
    appearance_mode_menu.pack(side='right')
    appearance_mode_menu.set(ctk.get_appearance_mode())

    # About Tab
    about_frame = tabview.tab("About")
    ctk.CTkLabel(about_frame, text="ReVanced GUI v1.2", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
    ctk.CTkLabel(about_frame, text="A modern & clean front-end for the ReVanced CLI", justify="center").pack(pady=(0, 10), padx=10)
    ctk.CTkLabel(about_frame, text="This GUI provides a user-friendly interface for patching Android applications using ReVanced.", justify="center", wraplength=380).pack(padx=10)

    def open_url(url):
        webbrowser.open_new(url)

    link = ctk.CTkLabel(about_frame, text="GitHub Repository", text_color="#1f6aa5", cursor="hand2")
    link.pack(pady=10)
    link.bind("<Button-1>", lambda e: open_url("https://github.com/chamindudilsh/revanced-gui"))

    ctk.CTkLabel(about_frame, text="Developed with ♥ by chamindudilsh", justify="center").pack(side='bottom', pady=10)
    ctk.CTkLabel(about_frame, text="This project is not affiliated with ReVanced.", justify="center").pack(side='bottom', pady=10)


def copy_logs():
    root.clipboard_clear()
    root.clipboard_append(log_output.get("1.0", "end"))
    CTkMessagebox(title="Logs", message="Logs copied to clipboard.", icon="check")


def clear_logs():
    log_output.configure(state="normal")
    log_output.delete("1.0", "end")
    log_output.configure(state="disabled")


root = ctk.CTk()
root.title("ReVanced GUI")
# root.iconbitmap('assets/icon.ico')
root.geometry("800x600")

settings = load_settings()

cli_var = ctk.StringVar(value=settings.get("cli_path", "") if settings.get("remember_paths", True) else "")
rvp_var = ctk.StringVar(value=settings.get("rvp_path", "") if settings.get("remember_paths", True) else "")
apk_var = ctk.StringVar()
output_var = ctk.StringVar(value=settings.get("output_folder", os.getcwd()) if settings.get("remember_paths", True) else os.getcwd())

# --- Header ---
header_frame = ctk.CTkFrame(root, corner_radius=0)
header_frame.pack(fill='x')

header_label = ctk.CTkLabel(header_frame, text="ReVanced GUI", font=ctk.CTkFont(size=20, weight="bold"))
header_label.pack(side="left", padx=20, pady=10)

settings_button = ctk.CTkButton(header_frame, text="⚙️", command=open_settings, width=40, font=ctk.CTkFont(size=20))
settings_button.pack(side="right", padx=20, pady=10)
settings_tip = CTkToolTip(settings_button, "Settings")

main_frame = ctk.CTkFrame(root)
main_frame.pack(fill='both', expand=True, padx=10, pady=10)

main_frame.columnconfigure(1, weight=1)

# --- Input Fields ---
fields = [
    ("ReVanced CLI:", cli_var, select_cli_path, "https://github.com/ReVanced/revanced-cli/releases", "Download ReVanced CLI"),
    ("ReVanced Patches:", rvp_var, select_rvp_path, "https://github.com/ReVanced/revanced-patches/releases", "Download ReVanced Patches"),
    ("Target APK:", apk_var, select_apk_path, None, None),
    ("Output Folder:", output_var, select_output_folder, None, None)
]

main_frame.rowconfigure(len(fields), weight=1)  # Make log console expandable

for i, (label, var, browse_cmd, download_url, tooltip_text) in enumerate(fields):
    ctk.CTkLabel(main_frame, text=label).grid(row=i, column=0, sticky='w', padx=(0, 10), pady=10)
    entry = ctk.CTkEntry(main_frame, textvariable=var)
    entry.grid(row=i, column=1, sticky='ew', pady=10)

    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.grid(row=i, column=2, sticky='e', padx=(10, 0), pady=10)
    ctk.CTkButton(button_frame, text="Browse...", command=browse_cmd, width=100).pack(side='left')
    if download_url:
        download_button = ctk.CTkButton(button_frame, text="⬇", command=lambda u=download_url: open_revanced_downloads(u), width=40, font=ctk.CTkFont(size=20))
        download_button.pack(side='left', padx=(10, 0))
        if tooltip_text:
            CTkToolTip(download_button, tooltip_text)

# --- Log Console ---
log_output = ctk.CTkTextbox(main_frame, wrap="word", state="disabled")
log_output.grid(row=len(fields), column=0, columnspan=3, sticky='nsew', pady=(10, 0))

# --- Log Buttons ---
log_button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
log_button_frame.grid(row=len(fields) + 1, column=0, columnspan=3, sticky='ew', pady=5)
ctk.CTkButton(log_button_frame, text="Copy Logs", command=copy_logs).pack(side='left', padx=(0, 5))
ctk.CTkButton(log_button_frame, text="Clear Logs", command=clear_logs).pack(side='left')

# --- Progress Bar ---
progress_bar = ctk.CTkProgressBar(main_frame, mode="indeterminate")
progress_bar.grid(row=len(fields) + 2, column=0, columnspan=3, sticky='ew', pady=(10, 5))
progress_bar.stop()  # Stop initially

# --- Patch Button ---
patch_button = ctk.CTkButton(main_frame, text="Patch", command=run_patch, font=ctk.CTkFont(size=16, weight="bold"))
patch_button.grid(row=len(fields) + 3, column=0, columnspan=3, pady=5, ipady=10, sticky='ew')

root.mainloop()
