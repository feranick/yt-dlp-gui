#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
*****************************************************
* YT-DLP GUI
* version: 2026.05.29.1
* Uses: yt-dlp
* By: Nicola Ferralis <feranick@hotmail.com>
*****************************************************
'''

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import subprocess
import threading
import re
import os
import shlex

class YTDLPGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced yt-dlp Graphical Interface (v.2026.0529.1)")
        self.root.geometry("800x670")
        self.root.minsize(700, 570)
        
        self.download_thread = None
        self.process = None

        self.create_widgets()
        
    def create_widgets(self):
        # ------------------ TOP URL & DESTINATION BANNER ------------------
        top_frame = ttk.LabelFrame(self.root, text=" Target & Destination ", padding=10)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(top_frame, text="URL / Link:").grid(row=0, column=0, sticky="w", pady=2)
        self.url_entry = ttk.Entry(top_frame, width=65)
        self.url_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(top_frame, text="Save Folder:").grid(row=1, column=0, sticky="w", pady=2)
        self.output_dir_var = tk.StringVar(value=os.getcwd())
        self.output_entry = ttk.Entry(top_frame, textvariable=self.output_dir_var, width=65)
        self.output_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        browse_btn = ttk.Button(top_frame, text="Browse...", command=self.browse_directory)
        browse_btn.grid(row=1, column=2, padx=2, pady=2)
        
        top_frame.columnconfigure(1, weight=1)

        # ------------------ TABBED OPTIONS NOTEBOOK ------------------
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_format = ttk.Frame(self.notebook, padding=10)
        self.tab_metadata = ttk.Frame(self.notebook, padding=10)
        self.tab_playlist = ttk.Frame(self.notebook, padding=10)
        self.tab_advanced = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.tab_format, text="Quality & Format")
        self.notebook.add(self.tab_metadata, text="Subs & Thumbnails")
        self.notebook.add(self.tab_playlist, text="Playlists & Limits")
        self.notebook.add(self.tab_advanced, text="Network & Custom")
        
        self.setup_format_tab()
        self.setup_metadata_tab()
        self.setup_playlist_tab()
        self.setup_advanced_tab()

        # ------------------ PROGRESS & EXECUTION AREA ------------------
        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(fill="x", side="bottom")
        
        progress_layout = ttk.Frame(bottom_frame)
        progress_layout.pack(fill="x", pady=2)
        
        self.progress_bar = ttk.Progressbar(progress_layout, orient="horizontal", mode="determinate")
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.status_label = ttk.Label(progress_layout, text="Ready", width=15, anchor="e")
        self.status_label.pack(side="right")
        
        btn_layout = ttk.Frame(bottom_frame)
        btn_layout.pack(fill="x", pady=5)
        
        self.start_btn = ttk.Button(btn_layout, text="START DOWNLOAD", command=self.start_download)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=2)
        
        self.stop_btn = ttk.Button(btn_layout, text="STOP", width=12, command=self.stop_download, state="disabled")
        self.stop_btn.pack(side="right", padx=2)

        footer_layout = ttk.Frame(bottom_frame)
        footer_layout.pack(fill="x", pady=(2, 0))
        version_label = ttk.Label(footer_layout, text="v.2026.0529.1", font=("Arial", 8), foreground="gray")
        version_label.pack(side="right")

        # ------------------ LIVE CONSOLE LOG SCREEN ------------------
        log_frame = ttk.LabelFrame(self.root, text=" Live Execution Output Log ", padding=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        
        self.log_text = ScrolledText(log_frame, height=8, bg="#1e1e1e", fg="#ffffff", font=("Courier", 9))
        self.log_text.pack(fill="both", expand=True)

    def setup_format_tab(self):
        self.download_mode = tk.StringVar(value="video")
        
        vid_rb = ttk.Radiobutton(self.tab_format, text="Video + Audio (Merged)", variable=self.download_mode, value="video", command=self.toggle_format_options)
        vid_rb.grid(row=0, column=0, sticky="w", pady=5)
        
        aud_rb = ttk.Radiobutton(self.tab_format, text="Audio Only (Extraction)", variable=self.download_mode, value="audio", command=self.toggle_format_options)
        aud_rb.grid(row=0, column=1, sticky="w", pady=5)
        
        self.video_frame = ttk.LabelFrame(self.tab_format, text=" Video Options ", padding=10)
        self.video_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Label(self.video_frame, text="Max Resolution Quality:").grid(row=0, column=0, sticky="w")
        self.video_res = ttk.Combobox(self.video_frame, values=["Best Available", "2160p (4K)", "1440p (2K)", "1080p", "720p", "480p", "360p"], state="readonly")
        self.video_res.current(0)
        self.video_res.grid(row=0, column=1, padx=5, sticky="w")
        
        ttk.Label(self.video_frame, text="Container Format:").grid(row=1, column=0, sticky="w", pady=5)
        self.video_ext = ttk.Combobox(self.video_frame, values=["Default/Best", "mp4", "mkv", "webm"], state="readonly")
        self.video_ext.current(0)
        self.video_ext.grid(row=1, column=1, padx=5, sticky="w")

        self.audio_frame = ttk.LabelFrame(self.tab_format, text=" Audio Extract Options ", padding=10)
        self.audio_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Label(self.audio_frame, text="Audio Extension Profile:").grid(row=0, column=0, sticky="w")
        self.audio_ext = ttk.Combobox(self.audio_frame, values=["best", "mp3", "m4a", "flac", "wav", "opus"], state="readonly")
        self.audio_ext.current(0)
        self.audio_ext.grid(row=0, column=1, padx=5, sticky="w")
        
        ttk.Label(self.audio_frame, text="Audio Bitrate Quality:").grid(row=1, column=0, sticky="w", pady=5)
        self.audio_quality = ttk.Combobox(self.audio_frame, values=["best (Global)", "320k", "256k", "192k", "128k"], state="readonly")
        self.audio_quality.current(0)
        self.audio_quality.grid(row=1, column=1, padx=5, sticky="w")
        
        self.toggle_format_options()

    def setup_metadata_tab(self):
        self.embed_subs = tk.BooleanVar()
        self.write_auto_subs = tk.BooleanVar()
        self.embed_thumb = tk.BooleanVar()
        self.write_thumb = tk.BooleanVar()
        self.embed_meta = tk.BooleanVar()
        self.embed_chapters = tk.BooleanVar()
        
        ttk.Checkbutton(self.tab_metadata, text="Write Subtitle Track to Disk", variable=self.embed_subs).grid(row=0, column=0, sticky="w", pady=4)
        ttk.Checkbutton(self.tab_metadata, text="Include AI-Generated Auto-Subtitles", variable=self.write_auto_subs).grid(row=1, column=0, sticky="w", pady=4)
        ttk.Checkbutton(self.tab_metadata, text="Embed Subtitles Directly Into Video File", variable=self.embed_subs).grid(row=2, column=0, sticky="w", pady=4)
        
        ttk.Label(self.tab_metadata, text="Languages (e.g., 'en,es' or 'all'):").grid(row=3, column=0, sticky="w", padx=20)
        self.sub_langs = ttk.Entry(self.tab_metadata, width=20)
        self.sub_langs.insert(0, "en")
        self.sub_langs.grid(row=3, column=1, sticky="w")
        
        ttk.Separator(self.tab_metadata, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        
        ttk.Checkbutton(self.tab_metadata, text="Save Artwork Thumbnail Image Separately", variable=self.write_thumb).grid(row=5, column=0, sticky="w", pady=4)
        ttk.Checkbutton(self.tab_metadata, text="Embed Artwork Thumbnail directly into Media file", variable=self.embed_thumb).grid(row=6, column=0, sticky="w", pady=4)
        ttk.Checkbutton(self.tab_metadata, text="Inject Metadata Information (Tags, Description)", variable=self.embed_meta).grid(row=7, column=0, sticky="w", pady=4)
        ttk.Checkbutton(self.tab_metadata, text="Split & Inject Internal Video Chapters", variable=self.embed_chapters).grid(row=8, column=0, sticky="w", pady=4)

    def setup_playlist_tab(self):
        self.playlist_choice = tk.StringVar(value="auto")
        
        ttk.Radiobutton(self.tab_playlist, text="Parse Links Normally", variable=self.playlist_choice, value="auto").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Radiobutton(self.tab_playlist, text="Force Download Full Playlist", variable=self.playlist_choice, value="yes").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Radiobutton(self.tab_playlist, text="Ignore Playlist (Download Single Target)", variable=self.playlist_choice, value="no").grid(row=2, column=0, sticky="w", pady=2)
        
        ttk.Separator(self.tab_playlist, orient="horizontal").grid(row=3, column=0, columnspan=2, sticky="ew", pady=8)
        
        ttk.Label(self.tab_playlist, text="Playlist Start Item Index:").grid(row=4, column=0, sticky="w", pady=2)
        self.play_start = ttk.Entry(self.tab_playlist, width=10)
        self.play_start.grid(row=4, column=1, sticky="w")
        
        ttk.Label(self.tab_playlist, text="Playlist End Item Index:").grid(row=5, column=0, sticky="w", pady=2)
        self.play_end = ttk.Entry(self.tab_playlist, width=10)
        self.play_end.grid(row=5, column=1, sticky="w")
        
        ttk.Label(self.tab_playlist, text="Download Target Range Specific Items (e.g., 1-3,5,7):").grid(row=6, column=0, sticky="w", pady=2)
        self.play_items = ttk.Entry(self.tab_playlist, width=25)
        self.play_items.grid(row=6, column=1, sticky="w")
        
        ttk.Separator(self.tab_playlist, orient="horizontal").grid(row=7, column=0, columnspan=2, sticky="ew", pady=8)
        
        ttk.Label(self.tab_playlist, text="Global Speed Rate Limit (e.g., 50K or 10M):").grid(row=8, column=0, sticky="w", pady=2)
        self.rate_limit = ttk.Entry(self.tab_playlist, width=15)
        self.rate_limit.grid(row=8, column=1, sticky="w")

    def setup_advanced_tab(self):
        ttk.Label(self.tab_advanced, text="Network Proxy Address (URL:PORT):").grid(row=0, column=0, sticky="w", pady=2)
        self.proxy_entry = ttk.Entry(self.tab_advanced, width=40)
        self.proxy_entry.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(self.tab_advanced, text="Path to Cookie File (.txt):").grid(row=1, column=0, sticky="w", pady=4)
        self.cookies_entry = ttk.Entry(self.tab_advanced, width=40)
        self.cookies_entry.grid(row=1, column=1, sticky="w", padx=5)
        
        self.geo_bypass = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.tab_advanced, text="Enable Target Country Geo-Bypass Spoofing", variable=self.geo_bypass).grid(row=2, column=0, columnspan=2, sticky="w", pady=6)
        
        self.ignore_errors = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.tab_advanced, text="Ignore Parse Errors (Keep downloading items in queue)", variable=self.ignore_errors).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)

        ttk.Label(self.tab_advanced, text="Additional Arbitrary Arguments CLI Flags:").grid(row=4, column=0, sticky="w", pady=(15, 2))
        self.custom_args = ttk.Entry(self.tab_advanced, width=65)
        self.custom_args.grid(row=5, column=0, columnspan=2, sticky="ew", pady=2)
        ttk.Label(self.tab_advanced, text="Example: --no-mtime --restrict-filenames", font=("Arial", 8), foreground="gray").grid(row=6, column=0, columnspan=2, sticky="w")

    def browse_directory(self):
        dir_selected = filedialog.askdirectory()
        if dir_selected:
            self.output_dir_var.set(dir_selected)
            
    def toggle_format_options(self):
        mode = self.download_mode.get()
        if mode == "video":
            for child in self.video_frame.winfo_children():
                child.configure(state="normal")
            for child in self.audio_frame.winfo_children():
                child.configure(state="disabled")
        else:
            for child in self.video_frame.winfo_children():
                child.configure(state="disabled")
            for child in self.audio_frame.winfo_children():
                child.configure(state="normal")

    def build_command(self):
        url = self.url_entry.get().strip()
        if not url:
            return None
            
        cmd = ["yt-dlp", "--newline", "--progress"]
        out_template = os.path.join(self.output_dir_var.get(), "%(title)s.%(ext)s")
        cmd.extend(["-o", out_template])
        
        if self.download_mode.get() == "video":
            res_map = {
                "Best Available": "bv*+ba/b",
                "2160p (4K)": "bv*[height<=2160]+ba/b",
                "1440p (2K)": "bv*[height<=1440]+ba/b",
                "1080p": "bv*[height<=1080]+ba/b",
                "720p": "bv*[height<=720]+ba/b",
                "480p": "bv*[height<=480]+ba/b",
                "360p": "bv*[height<=360]+ba/b"
            }
            cmd.extend(["-f", res_map[self.video_res.get()]])
            
            video_format = self.video_ext.get()
            if video_format != "Default/Best":
                cmd.extend(["--merge-output-format", video_format])
        else:
            cmd.append("-x")
            cmd.extend(["--audio-format", self.audio_ext.get()])
            aq = self.audio_quality.get()
            if "best" not in aq:
                cmd.extend(["--audio-quality", aq.replace("k", "")])
                
        if self.embed_subs.get():
            cmd.append("--embed-subs")
        if self.write_auto_subs.get():
            cmd.append("--write-auto-subs")
        if self.embed_subs.get() or self.write_auto_subs.get():
            cmd.append("--write-subs")
            if self.sub_langs.get().strip():
                cmd.extend(["--sub-langs", self.sub_langs.get().strip()])
                
        if self.write_thumb.get():
            cmd.append("--write-thumbnail")
        if self.embed_thumb.get():
            cmd.append("--embed-thumbnail")
        if self.embed_meta.get():
            cmd.append("--embed-metadata")
        if self.embed_chapters.get():
            cmd.append("--embed-chapters")
            
        p_choice = self.playlist_choice.get()
        if p_choice == "yes":
            cmd.append("--yes-playlist")
        elif p_choice == "no":
            cmd.append("--no-playlist")
            
        if self.play_start.get().strip():
            cmd.extend(["--playlist-start", self.play_start.get().strip()])
        if self.play_end.get().strip():
            cmd.extend(["--playlist-end", self.play_end.get().strip()])
        if self.play_items.get().strip():
            cmd.extend(["--playlist-items", self.play_items.get().strip()])
            
        if self.rate_limit.get().strip():
            cmd.extend(["-r", self.rate_limit.get().strip()])
        if self.proxy_entry.get().strip():
            cmd.extend(["--proxy", self.proxy_entry.get().strip()])
        if self.cookies_entry.get().strip():
            cmd.extend(["--cookies", self.cookies_entry.get().strip()])
        if self.geo_bypass.get():
            cmd.append("--geo-bypass")
        if self.ignore_errors.get():
            cmd.append("--ignore-errors")
            
        if self.custom_args.get().strip():
            extra_flags = shlex.split(self.custom_args.get().strip())
            cmd.extend(extra_flags)
            
        cmd.append(url)
        return cmd

    def start_download(self):
        cmd = self.build_command()
        if not cmd:
            messagebox.showwarning("Missing Information", "Please enter a valid Target Media Link / URL.")
            return
            
        self.log_text.delete("1.0", tk.END)
        self.append_log(f"Assembled Command String:\n{' '.join(cmd)}\n\n")
        
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="Downloading...")
        self.progress_bar["value"] = 0
        
        self.download_thread = threading.Thread(target=self.run_process_loop, args=(cmd,), daemon=True)
        self.download_thread.start()

    def run_process_loop(self, cmd):
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                startupinfo=startupinfo
            )
            
            progress_regex = re.compile(r"\[download\]\s+(\d+\.\d+)%")
            
            while True:
                line = self.process.stdout.readline()
                if not line and self.process.poll() is not None:
                    break
                if line:
                    self.append_log(line)
                    match = progress_regex.search(line)
                    if match:
                        percentage = float(match.group(1))
                        self.root.after(0, self.update_progress, percentage)
                        
            return_code = self.process.wait()
            self.root.after(0, self.download_finished, return_code)
            
        except Exception as err:
            self.root.after(0, self.download_finished, -1, str(err))

    def stop_download(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.append_log("\n[Process Termination Requested by User]\n")

    def update_progress(self, val):
        self.progress_bar["value"] = val
        self.status_label.configure(text=f"Downloading {val}%")

    def append_log(self, txt):
        self.log_text.insert(tk.END, txt)
        self.log_text.see(tk.END)

    def download_finished(self, code, error_msg=None):
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        if code == 0:
            self.status_label.configure(text="Finished Successfully")
            self.progress_bar["value"] = 100
            messagebox.showinfo("Success", "Media downloaded successfully!")
        elif code == -1:
            self.status_label.configure(text="Internal Error")
            messagebox.showerror("Error Encountered", f"Failed to run process command loop:\n{error_msg}")
        else:
            self.status_label.configure(text=f"Exit Code: {code}")
            messagebox.showwarning("Incomplete", f"Process stopped or threw an exception code: {code}")

# Entry point callable wrapper
def main():
    window = tk.Tk()
    app = YTDLPGUI(window)
    window.mainloop()

if __name__ == "__main__":
    main()
