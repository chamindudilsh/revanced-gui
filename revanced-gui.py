# Requirements: pip install customtkinter pillow

import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import json
import os

SETTINGS_FILE = "settings.json"


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)


settings = load_settings()

ctk.set_appearance_mode(settings.get("theme", "system"))
ctk.set_default_color_theme("blue")


class ReVancedGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ReVanced GUI")
        self.geometry("900x700")
        self.minsize(850, 600)
        self.iconbitmap("assets/icon.ico") if os.path.exists("assets/icon.ico") else None

        self.create_ui()
        self.load_previous()

    def create_ui(self):
        # Top Bar
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", pady=(10, 5), padx=10)
        self.title_label = ctk.CTkLabel(self.top_frame, text="🧩 ReVanced GUI", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(side="left")

        self.settings_btn = ctk.CTkButton(self.top_frame, text="⚙️", width=40, command=self.open_settings)
        self.settings_btn.pack(side="right")

        # Main Input Section
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        def labeled_entry(label, var, browse_func):
            row = ctk.CTkFrame(self.main_frame)
            row.pack(fill="x", pady=6)
            ctk.CTkLabel(row, text=label, width=130, anchor="w").pack(side="left", padx=6)
            entry = ctk.CTkEntry(row, textvariable=var)
            entry.pack(side="left", fill="x", expand=True, padx=6)
            ctk.CTkButton(row, text="📂", width=40, command=browse_func).pack(side="left", padx=4)
            return entry

        self.cli_path = ctk.StringVar()
        labeled_entry("ReVanced CLI (.jar):", self.cli_path, self.browse_cli)

        self.patches_path = ctk.StringVar()
        labeled_entry("Patches (.rvp/.jar):", self.patches_path, self.browse_patches)

        self.apk_path = ctk.StringVar()
        labeled_entry("APK file:", self.apk_path, self.browse_apk)

        self.output_dir = ctk.StringVar()
        row = ctk.CTkFrame(self.main_frame)
        row.pack(fill="x", pady=6)
        ctk.CTkLabel(row, text="Output folder:", width=130, anchor="w").pack(side="left", padx=6)
        ctk.CTkEntry(row, textvariable=self.output_dir).pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkButton(row, text="Browse", width=70, command=self.browse_output).pack(side="left", padx=4)

        # Advanced Checkbox
        self.default_patch = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.main_frame, text="Use default patch selection", variable=self.default_patch).pack(anchor="w", padx=10, pady=8)

        # Log output
        ctk.CTkLabel(self.main_frame, text="Log Output").pack(anchor="w", padx=10, pady=(10, 0))
        self.log_box = ctk.CTkTextbox(self.main_frame, height=180)
        self.log_box.pack(fill="both", expand=True, padx=10, pady=6)

        log_btns = ctk.CTkFrame(self.main_frame)
        log_btns.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(log_btns, text="Copy Log", width=120, command=self.copy_log).pack(side="left", padx=(0, 8))
        ctk.CTkButton(log_btns, text="Clear Log", width=120, command=self.clear_log).pack(side="left", padx=(0, 8))
        ctk.CTkButton(log_btns, text="Open Log Folder", width=150, command=self.open_log_folder).pack(side="left")

        # Patch Button
        self.patch_btn = ctk.CTkButton(self, text="Patch", height=50, font=ctk.CTkFont(size=18, weight="bold"), command=self.run_patch)
        self.patch_btn.pack(fill="x", padx=10, pady=10)

    # Browse functions
    def browse_cli(self):
        path = filedialog.askopenfilename(title="Select ReVanced CLI .jar", filetypes=[("JAR Files", "*.jar")])
        if path:
            self.cli_path.set(path)
            self.save_paths()

    def browse_patches(self):
        path = filedialog.askopenfilename(title="Select Patches File", filetypes=[("Patch Files", "*.rvp *.jar")])
        if path:
            self.patches_path.set(path)
            self.save_paths()

    def browse_apk(self):
        path = filedialog.askopenfilename(title="Select APK File", filetypes=[("APK Files", "*.apk")])
        if path:
            self.apk_path.set(path)
            self.save_paths()

    def browse_output(self):
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            self.output_dir.set(path)
            self.save_paths()

    def save_paths(self):
        settings.update({
            "cli_path": self.cli_path.get(),
            "patches_path": self.patches_path.get(),
            "apk_path": self.apk_path.get(),
            "output_dir": self.output_dir.get()
        })
        save_settings(settings)

    def load_previous(self):
        for k, v in settings.items():
            if hasattr(self, k):
                getattr(self, k).set(v)

    def copy_log(self):
        self.clipboard_clear()
        self.clipboard_append(self.log_box.get("1.0", "end").strip())
        messagebox.showinfo("Copied", "Log copied to clipboard.")

    def clear_log(self):
        self.log_box.delete("1.0", "end")

    def open_log_folder(self):
        folder = settings.get("log_folder")
        if folder and os.path.exists(folder):
            os.startfile(folder)
        else:
            messagebox.showwarning("Not Found", "No log folder configured.")

    def get_unique_filename(self, path):
        base, ext = os.path.splitext(path)
        counter = 1
        new_path = path
        while os.path.exists(new_path):
            new_path = f"{base} ({counter}){ext}"
            counter += 1
        return new_path

    def run_patch(self):
        cli, patches, apk, outdir = self.cli_path.get(), self.patches_path.get(), self.apk_path.get(), self.output_dir.get()
        if not all([cli, patches, apk, outdir]):
            messagebox.showerror("Error", "Please fill all paths before patching.")
            return

        apk_name = os.path.basename(apk).replace(".apk", "-revanced.apk")
        output_path = os.path.join(outdir, apk_name)
        output_path = self.get_unique_filename(output_path)

        cmd = ["java", "-jar", cli, "patch", apk, "-p", patches, "-o", output_path]
        self.log_box.insert("end", f"\nRunning: {' '.join(cmd)}\n\n")
        self.patch_btn.configure(state="disabled", text="Patching...")

        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(proc.stdout.readline, ''):
                self.log_box.insert("end", line)
                self.log_box.see("end")
                self.update_idletasks()
            proc.wait()
            self.log_box.insert("end", f"\nPatching finished with return code {proc.returncode}\n")
        except Exception as e:
            self.log_box.insert("end", f"\nError: {e}\n")

        self.patch_btn.configure(state="normal", text="Patch")

    def open_settings(self):
        SettingsWindow(self)


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("400x350")
        ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.theme_option = ctk.CTkOptionMenu(self, values=["system", "dark", "light"], command=self.change_theme)
        self.theme_option.set(settings.get("theme", "system"))
        self.theme_option.pack(pady=10)

        self.log_toggle = ctk.CTkSwitch(self, text="Enable Log Saving", command=self.toggle_logs)
        self.log_toggle.select() if settings.get("log_folder") else self.log_toggle.deselect()
        self.log_toggle.pack(pady=10)

        self.choose_log_btn = ctk.CTkButton(self, text="Select Log Folder", command=self.select_log_folder)
        self.choose_log_btn.pack(pady=5)

        self.open_log_btn = ctk.CTkButton(self, text="Open Log Folder", command=self.open_log)
        self.open_log_btn.pack(pady=5)

    def change_theme(self, value):
        settings["theme"] = value
        save_settings(settings)
        ctk.set_appearance_mode(value)

    def toggle_logs(self):
        if not self.log_toggle.get():
            settings.pop("log_folder", None)
            save_settings(settings)

    def select_log_folder(self):
        path = filedialog.askdirectory(title="Select Log Folder")
        if path:
            settings["log_folder"] = path
            save_settings(settings)

    def open_log(self):
        folder = settings.get("log_folder")
        if folder and os.path.exists(folder):
            os.startfile(folder)
        else:
            messagebox.showwarning("Not Found", "No log folder set.")


if __name__ == "__main__":
    app = ReVancedGUI()
    app.mainloop()
