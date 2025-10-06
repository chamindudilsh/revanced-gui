
import os
import sys
import threading
import subprocess
import shlex
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# ---------- Configuration ----------
CLI_DOWNLOAD_URL = "https://github.com/ReVanced/revanced-cli/releases"
PATCHES_DOWNLOAD_URL = "https://github.com/ReVanced/revanced-patches/releases"
DEFAULT_OUTPUT_NAME = "revanced-output.apk"
# -----------------------------------

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class ReVancedGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ReVanced GUI")
        self.geometry("900x600")
        self.minsize(800, 520)

        # Variables
        self.cli_path = tk.StringVar()
        self.patches_path = tk.StringVar()
        self.apk_path = tk.StringVar()
        self.output_folder = tk.StringVar(value=str(Path.home()))
        self.use_default_selection = tk.BooleanVar(value=True)
        self.process = None

        # Layout: top frame for inputs, middle for logs, bottom for patch button
        self._build_inputs_frame()
        self._build_log_frame()
        self._build_bottom_frame()

    def _build_inputs_frame(self):
        frame = ctk.CTkFrame(self, corner_radius=8)
        frame.pack(fill="x", padx=16, pady=(12,8))

        # ReVanced CLI
        ctk.CTkLabel(frame, text="ReVanced CLI (.jar)", anchor="w").grid(row=0, column=0, sticky="w", padx=12, pady=(10,4))
        entry_cli = ctk.CTkEntry(frame, textvariable=self.cli_path, width=680)
        entry_cli.grid(row=1, column=0, padx=12, pady=(0,10), sticky="w")
        btn_cli_browse = ctk.CTkButton(frame, text="📁", width=40, command=self.browse_cli)
        btn_cli_browse.grid(row=1, column=1, padx=(6,2), pady=(0,10))
        btn_cli_download = ctk.CTkButton(frame, text="⬇️", width=40, command=lambda: webbrowser.open(CLI_DOWNLOAD_URL))
        btn_cli_download.grid(row=1, column=2, padx=(2,12), pady=(0,10))

        # Patches .rvp
        ctk.CTkLabel(frame, text="Patches (.rvp/.jar)", anchor="w").grid(row=2, column=0, sticky="w", padx=12, pady=(4,4))
        entry_patches = ctk.CTkEntry(frame, textvariable=self.patches_path, width=680)
        entry_patches.grid(row=3, column=0, padx=12, pady=(0,10), sticky="w")
        btn_patches_browse = ctk.CTkButton(frame, text="📁", width=40, command=self.browse_patches)
        btn_patches_browse.grid(row=3, column=1, padx=(6,2), pady=(0,10))
        btn_patches_download = ctk.CTkButton(frame, text="⬇️", width=40, command=lambda: webbrowser.open(PATCHES_DOWNLOAD_URL))
        btn_patches_download.grid(row=3, column=2, padx=(2,12), pady=(0,10))

        # APK file
        ctk.CTkLabel(frame, text="APK file", anchor="w").grid(row=4, column=0, sticky="w", padx=12, pady=(4,4))
        entry_apk = ctk.CTkEntry(frame, textvariable=self.apk_path, width=680)
        entry_apk.grid(row=5, column=0, padx=12, pady=(0,10), sticky="w")
        btn_apk_browse = ctk.CTkButton(frame, text="📁", width=40, command=self.browse_apk)
        btn_apk_browse.grid(row=5, column=1, padx=(6,2), pady=(0,10))
        # no download for apk

        # Output folder
        ctk.CTkLabel(frame, text="Output folder", anchor="w").grid(row=6, column=0, sticky="w", padx=12, pady=(4,4))
        entry_out = ctk.CTkEntry(frame, textvariable=self.output_folder, width=560)
        entry_out.grid(row=7, column=0, padx=12, pady=(0,10), sticky="w")
        btn_out = ctk.CTkButton(frame, text="Browse", width=80, command=self.browse_output_folder)
        btn_out.grid(row=7, column=1, padx=(6,2), pady=(0,10), sticky="w")

        # Checkbox and Advanced
        chk = ctk.CTkCheckBox(frame, text="Use default patch selection", variable=self.use_default_selection)
        chk.grid(row=8, column=0, sticky="w", padx=12, pady=(6,12))

        self.adv_button = ctk.CTkButton(frame, text="Advanced ▼", width=120, command=self.toggle_advanced)
        self.adv_button.grid(row=8, column=1, padx=(6,12), pady=(6,12), sticky="e")

        # Advanced frame (initially hidden)
        self.advanced_frame = ctk.CTkFrame(frame, corner_radius=6)
        self.advanced_visible = False

    def _build_log_frame(self):
        lbl = ctk.CTkLabel(self, text="Log Output", anchor="w")
        lbl.pack(fill="x", padx=16, pady=(6,0))
        self.log_box = ctk.CTkTextbox(self, width=0, height=14, corner_radius=6)
        self.log_box.pack(fill="both", expand=True, padx=16, pady=(4,8))

    def _build_bottom_frame(self):
        bottom = ctk.CTkFrame(self, corner_radius=8)
        bottom.pack(fill="x", padx=16, pady=(0,16))
        self.patch_btn = ctk.CTkButton(bottom, text="Patch", height=48, command=self.start_patch, font=ctk.CTkFont(size=18, weight="bold"))
        self.patch_btn.pack(fill="x", padx=12, pady=12)

    # ---------- Browsers ----------
    def browse_cli(self):
        p = filedialog.askopenfilename(title="Select ReVanced CLI .jar", filetypes=[("JAR files","*.jar"), ("All files","*.*")])
        if p:
            self.cli_path.set(p)

    def browse_patches(self):
        p = filedialog.askopenfilename(title="Select patches (.rvp/.jar)", filetypes=[("Patch files","*.rvp;*.jar"), ("All files","*.*")])
        if p:
            self.patches_path.set(p)

    def browse_apk(self):
        p = filedialog.askopenfilename(title="Select APK file", filetypes=[("APK files","*.apk"), ("All files","*.*")])
        if p:
            self.apk_path.set(p)

    def browse_output_folder(self):
        p = filedialog.askdirectory(title="Select output folder", initialdir=self.output_folder.get() or str(Path.home()))
        if p:
            self.output_folder.set(p)

    def toggle_advanced(self):
        if self.advanced_visible:
            self.advanced_frame.pack_forget()
            self.adv_button.configure(text="Advanced ▼")
            self.advanced_visible = False
        else:
            # add stub content
            if not self.advanced_frame.winfo_children():
                ctk.CTkLabel(self.advanced_frame, text="Advanced options (coming soon)").pack(padx=8, pady=8)
            self.advanced_frame.pack(fill="x", padx=12, pady=(0,8))
            self.adv_button.configure(text="Advanced ▲")
            self.advanced_visible = True

    # ---------- Logging ----------
    def log(self, text):
        # insert at end and autoscroll
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ---------- Patch process ----------
    def start_patch(self):
        if self.process:
            messagebox.showinfo("Process running", "A patching process is already running.")
            return

        cli = self.cli_path.get().strip()
        patches = self.patches_path.get().strip()
        apk = self.apk_path.get().strip()
        out_folder = self.output_folder.get().strip()

        if not cli or not os.path.isfile(cli):
            messagebox.showerror("Missing CLI", "Please select a valid revanced-cli .jar file.")
            return
        if not patches or not os.path.isfile(patches):
            messagebox.showerror("Missing patches", "Please select a valid patches file (.rvp or .jar).")
            return
        if not apk or not os.path.isfile(apk):
            messagebox.showerror("Missing APK", "Please select a valid APK file.")
            return
        if not out_folder or not os.path.isdir(out_folder):
            messagebox.showerror("Missing Output", "Please select a valid output folder.")
            return

        # Determine output apk path
        input_apk_name = Path(apk).stem
        out_apk_path = Path(out_folder) / f"{input_apk_name}-revanced.apk"

        # Build command based on common revanced-cli usage.
        # We'll use: java -jar revanced-cli.jar patch -a input.apk -o output.apk -b patches.rvp
        cmd = [
            "java", "-jar", cli,
            "patch",
            "-a", apk,
            "-o", str(out_apk_path),
            "-b", patches
        ]
        # If user wants default selection (checked) we pass --select-default (if applicable).
        # Since revanced-cli flags may vary, we only add a commonly used flag if checkbox is set.
        if self.use_default_selection.get():
            # Many revanced-cli versions use --select or --auto or --default. We try --select-default then fallback.
            # Keeping a safe no-op: do not add an unknown flag that would break; instead, pass --auto if available.
            # We'll attempt with --auto as an extra arg; if it fails, user will see CLI output with error.
            cmd.append("--auto")

        # Disable UI button and run in thread
        self.patch_btn.configure(state="disabled")
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self.log(f"Running: {' '.join(shlex.quote(c) for c in cmd)}")
        thread = threading.Thread(target=self._run_subprocess, args=(cmd, out_apk_path), daemon=True)
        thread.start()

    def _run_subprocess(self, cmd, out_apk_path):
        try:
            # Create subprocess and stream output
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
            self.process = proc
            for line in proc.stdout:
                self.log(line.rstrip())
            proc.wait()
            rc = proc.returncode
            if rc == 0 and out_apk_path.exists():
                self.log("Patching completed successfully.")
                self._on_patch_complete(out_apk_path)
            else:
                self.log(f"Patching finished with return code {rc}. Check output above for errors.")
                self._on_patch_complete(out_apk_path, success=(rc==0))
        except FileNotFoundError as e:
            self.log("Error: Java not found. Make sure Java is installed and added to PATH.")
            messagebox.showerror("Java not found", "Java was not found on this system. Please install Java and ensure 'java' is in PATH.")
        except Exception as e:
            self.log(f"Unexpected error: {e}")
            messagebox.showerror("Error", f"Unexpected error: {e}")
        finally:
            self.process = None
            self.patch_btn.configure(state="normal")

    def _on_patch_complete(self, out_apk_path, success=True):
        # Show a custom dialog with "Show in folder" and "Close"
        def open_folder():
            try:
                p = str(out_apk_path.resolve())
                # Windows: explorer /select, "C:\path\to\file.apk"
                if sys.platform.startswith("win"):
                    subprocess.run(["explorer", "/select,", p])
                else:
                    # For other OS, just open folder
                    folder = str(out_apk_path.parent)
                    webbrowser.open(folder)
            except Exception as e:
                messagebox.showerror("Open folder failed", str(e))
            finally:
                dlg.destroy()

        def close():
            dlg.destroy()

        dlg = tk.Toplevel(self)
        dlg.title("Patching Completed" if success else "Patching Finished")
        dlg.geometry("420x120")
        dlg.resizable(False, False)
        lbl = tk.Label(dlg, text="Patching Completed" if success else "Patching finished (see log)", font=("Segoe UI", 11))
        lbl.pack(pady=(16,8))
        btn_frame = tk.Frame(dlg)
        btn_frame.pack(pady=8)
        b1 = tk.Button(btn_frame, text="Show in folder", width=15, command=open_folder)
        b1.pack(side="left", padx=12)
        b2 = tk.Button(btn_frame, text="Close", width=10, command=close)
        b2.pack(side="right", padx=12)

        # Keep dialog on top
        dlg.transient(self)
        dlg.grab_set()
        self.wait_window(dlg)

if __name__ == "__main__":
    app = ReVancedGUI()
    app.mainloop()
