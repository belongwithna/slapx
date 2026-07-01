import os
import time
import queue
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import deque
from .constants import MAX_SLOTS

class SlapDetectorGUI:
    def __init__(self, config_manager, detector, audio_queue, trigger_queue, default_sounds):
        self.config_manager = config_manager
        self.detector = detector
        self.audio_queue = audio_queue
        self.trigger_queue = trigger_queue
        self.default_sounds = default_sounds
        
        self.slap_count = self.config_manager.config.get("total_slaps", 0)
        self.audio_history = deque([0] * 100, maxlen=100)
        self.slap_flash_ticks = 0
        
        self.init_gui()
        
    def init_gui(self):
        """Initializes the Tkinter interface with a premium dark styling."""
        self.root = tk.Tk()
        self.root.title("Slapx — Laptop Slap Detector")
        self.root.geometry("520x700")
        self.root.resizable(False, False)
        
        # Custom Colors (Catppuccin Mocha-inspired style)
        self.c_bg = "#1e1e2e"         # Main BG
        self.c_card = "#181825"       # Sub BG (darker cards)
        self.c_crust = "#11111b"      # Accent deep dark
        self.c_fg = "#cdd6f4"         # Text
        self.c_accent = "#cba6f7"     # Lavender/Mauve
        self.c_cyan = "#89dceb"       # Cyan
        self.c_red = "#f38ba8"        # Red/Pink
        self.c_green = "#a6e3a1"      # Green
        self.c_gray = "#6c7086"       # Dark Gray
        
        self.root.configure(bg=self.c_bg)
        
        # Title Header
        title_frame = tk.Frame(self.root, bg=self.c_bg, padx=20, pady=15)
        title_frame.pack(fill='x')
        
        # Title Icon / Text
        title_label = tk.Label(title_frame, text="⚡ SLAPX", font=("Helvetica", 24, "bold"), fg=self.c_accent, bg=self.c_bg)
        title_label.pack(anchor='w')
        
        sub_label = tk.Label(title_frame, text="Play audio effects when your laptop is physically tapped or slapped", 
                             font=("Helvetica", 9, "italic"), fg=self.c_gray, bg=self.c_bg)
        sub_label.pack(anchor='w', pady=(2, 0))
        
        # Real-time Status Area (LED)
        status_frame = tk.Frame(title_frame, bg=self.c_bg)
        status_frame.pack(anchor='w', pady=(8, 0))
        
        self.led_canvas = tk.Canvas(status_frame, width=16, height=16, bg=self.c_bg, highlightthickness=0)
        self.led_canvas.pack(side='left', padx=(0, 6))
        self.led_circle = self.led_canvas.create_oval(2, 2, 14, 14, fill=self.c_gray, outline="")
        
        self.status_label = tk.Label(status_frame, text="STATUS: INACTIVE", font=("Helvetica", 9, "bold"), fg=self.c_gray, bg=self.c_bg)
        self.status_label.pack(side='left')
        
        # 1. Main Display - Visualizer Canvas (waveform display)
        vis_frame = tk.LabelFrame(self.root, text=" Real-time Audio Level ", font=("Helvetica", 9, "bold"), 
                                  fg=self.c_accent, bg=self.c_bg, bd=1, highlightthickness=0, relief='solid', padx=10, pady=10)
        vis_frame.pack(fill='x', padx=20, pady=(5, 10))
        
        self.canvas_width = 458
        self.canvas_height = 110
        self.canvas = tk.Canvas(vis_frame, width=self.canvas_width, height=self.canvas_height, 
                                bg=self.c_crust, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Draw background grids on canvas
        for y in range(30, self.canvas_height, 30):
            self.canvas.create_line(0, y, self.canvas_width, y, fill="#242437", dash=(2, 4))
            
        # 2. Sensitivity & Delay Controls
        ctrl_frame = tk.Frame(self.root, bg=self.c_bg, padx=20)
        ctrl_frame.pack(fill='x', pady=5)
        
        # Sensitivity Slider
        sens_label_frame = tk.Frame(ctrl_frame, bg=self.c_bg)
        sens_label_frame.pack(fill='x')
        tk.Label(sens_label_frame, text="Sensitivity Threshold (Lower = More Sensitive)", font=("Helvetica", 9, "bold"), fg=self.c_fg, bg=self.c_bg).pack(side='left')
        self.sens_val_lbl = tk.Label(sens_label_frame, text=str(self.config_manager.config["sensitivity"]), font=("Helvetica", 9, "bold"), fg=self.c_cyan, bg=self.c_bg)
        self.sens_val_lbl.pack(side='right')
        
        self.sens_scale = tk.Scale(ctrl_frame, from_=500, to=30000, orient='horizontal', showvalue=False,
                                   bg=self.c_bg, fg=self.c_fg, troughcolor=self.c_card, 
                                   activebackground=self.c_accent, highlightthickness=0, bd=0,
                                   command=self.on_sensitivity_change)
        self.sens_scale.set(self.config_manager.config["sensitivity"])
        self.sens_scale.pack(fill='x', pady=(2, 10))
        
        # Delay Slider
        delay_label_frame = tk.Frame(ctrl_frame, bg=self.c_bg)
        delay_label_frame.pack(fill='x')
        tk.Label(delay_label_frame, text="Trigger Cooldown Delay (Seconds)", font=("Helvetica", 9, "bold"), fg=self.c_fg, bg=self.c_bg).pack(side='left')
        self.delay_val_lbl = tk.Label(delay_label_frame, text=f"{self.config_manager.config['cooldown']:.1f}s", font=("Helvetica", 9, "bold"), fg=self.c_cyan, bg=self.c_bg)
        self.delay_val_lbl.pack(side='right')
        
        self.delay_scale = tk.Scale(ctrl_frame, from_=0.1, to=5.0, resolution=0.1, orient='horizontal', showvalue=False,
                                    bg=self.c_bg, fg=self.c_fg, troughcolor=self.c_card, 
                                    activebackground=self.c_accent, highlightthickness=0, bd=0,
                                    command=self.on_delay_change)
        self.delay_scale.set(self.config_manager.config["cooldown"])
        self.delay_scale.pack(fill='x', pady=(2, 10))
        
        # 3. Audio Customization Slots (Max 3)
        audio_frame = tk.LabelFrame(self.root, text=" Custom Audio Files (Max 3, Randomly Played) ", font=("Helvetica", 9, "bold"),
                                    fg=self.c_accent, bg=self.c_bg, bd=1, highlightthickness=0, relief='solid', padx=15, pady=10)
        audio_frame.pack(fill='x', padx=20, pady=10)
        
        self.slot_entries = []
        for i in range(MAX_SLOTS):
            slot_row = tk.Frame(audio_frame, bg=self.c_bg)
            slot_row.pack(fill='x', pady=4)
            
            # Slot Indicator Label
            tk.Label(slot_row, text=f"Slot {i+1}:", font=("Helvetica", 9, "bold"), fg=self.c_fg, bg=self.c_bg, width=6, anchor='w').pack(side='left')
            
            # File Path Text Field (Read-only)
            path_var = tk.StringVar(value=self.get_sound_display_name(i))
            entry = tk.Entry(slot_row, textvariable=path_var, font=("Helvetica", 9), bg=self.c_card, fg=self.c_fg,
                             insertbackground=self.c_fg, bd=1, relief='solid', state='readonly')
            entry.pack(side='left', fill='x', expand=True, padx=5)
            self.slot_entries.append((path_var, entry))
            
            # Action Buttons
            btn_style = {"relief": "flat", "bd": 0, "activebackground": self.c_accent, "font": ("Helvetica", 9, "bold")}
            
            # Browse File Button
            tk.Button(slot_row, text="📂", bg=self.c_gray, fg=self.c_crust, width=3,
                      command=lambda idx=i: self.browse_audio(idx), **btn_style).pack(side='left', padx=2)
            
            # Play / Test Sound Button
            tk.Button(slot_row, text="▶", bg=self.c_green, fg=self.c_crust, width=3,
                      command=lambda idx=i: self.test_play_audio(idx), **btn_style).pack(side='left', padx=2)
                      
            # Clear / Reset Slot Button
            tk.Button(slot_row, text="✕", bg=self.c_red, fg=self.c_crust, width=3,
                      command=lambda idx=i: self.clear_audio(idx), **btn_style).pack(side='left', padx=2)
                      
        # 4. Slap Count Display Card & Main Switch Button
        bottom_frame = tk.Frame(self.root, bg=self.c_bg, padx=20)
        bottom_frame.pack(fill='both', expand=True, pady=(5, 15))
        
        # Left side: Counter Card
        counter_card = tk.Frame(bottom_frame, bg=self.c_card, bd=1, relief='solid', padx=15, pady=8)
        counter_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(counter_card, text="TOTAL SLAPS", font=("Helvetica", 8, "bold"), fg=self.c_cyan, bg=self.c_card).pack(anchor='center')
        self.count_label = tk.Label(counter_card, text=str(self.slap_count), font=("Helvetica", 36, "bold"), fg=self.c_red, bg=self.c_card)
        self.count_label.pack(anchor='center')
        
        # Right side: Control Buttons (Start/Stop + Simulate Slap)
        btn_container = tk.Frame(bottom_frame, bg=self.c_bg)
        btn_container.pack(side='right', fill='both', expand=True)
        
        self.toggle_btn = tk.Button(btn_container, text="START LISTENING", font=("Helvetica", 11, "bold"),
                                     bg=self.c_green, fg=self.c_crust, relief='flat', bd=0, height=2,
                                     command=self.toggle_listening)
        self.toggle_btn.pack(fill='x', pady=(0, 5))
        
        sim_btn = tk.Button(btn_container, text="SIMULATE SLAP", font=("Helvetica", 9, "bold"),
                            bg=self.c_card, fg=self.c_fg, relief='flat', bd=0, height=1,
                            command=self.simulate_slap)
        sim_btn.pack(fill='x')
        
        # Initialize canvas line representation
        self.redraw_threshold_line()
        
        # Register window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Start GUI polling update loop
        self.update_gui_loop()

    def get_sound_display_name(self, index):
        """Returns a clean display name for configured audio file path."""
        path = self.config_manager.config["sounds"][index]
        if not path:
            return "Empty"
        basename = os.path.basename(path)
        if basename.startswith("default_"):
            return f"Built-in: {basename.replace('default_', '').replace('.wav', '').title()}"
        return basename
        
    def browse_audio(self, index):
        """Opens a file dialog to select a custom audio track."""
        file_path = filedialog.askopenfilename(
            title=f"Select Audio for Slot {index+1}",
            filetypes=[("Audio Files", "*.wav *.mp3 *.ogg *.m4a *.flac"), ("All Files", "*.*")]
        )
        if file_path:
            self.config_manager.config["sounds"][index] = os.path.abspath(file_path)
            self.slot_entries[index][0].set(self.get_sound_display_name(index))
            self.config_manager.save_config()
            
    def test_play_audio(self, index):
        """Directly plays the selected audio file to test it."""
        path = self.config_manager.config["sounds"][index]
        if path and os.path.exists(path):
            try:
                import subprocess
                subprocess.Popen(
                    ['mpv', '--no-terminal', '--volume=100', path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception as e:
                messagebox.showerror("Error", f"Could not play sound: {e}")
        else:
            messagebox.showwarning("Warning", "Slot is empty or sound file does not exist!")
            
    def clear_audio(self, index):
        """Clears custom sound from slot and reverts it to empty/none."""
        self.config_manager.config["sounds"][index] = ""
        self.slot_entries[index][0].set("Empty")
        self.config_manager.save_config()
        
    def on_sensitivity_change(self, value):
        """Slider callback when sensitivity threshold changes."""
        val = int(value)
        self.config_manager.config["sensitivity"] = val
        self.sens_val_lbl.config(text=str(val))
        self.redraw_threshold_line()
        self.config_manager.save_config()
        
    def on_delay_change(self, value):
        """Slider callback when delay cooldown changes."""
        val = float(value)
        self.config_manager.config["cooldown"] = val
        self.delay_val_lbl.config(text=f"{val:.1f}s")
        self.config_manager.save_config()
        
    def redraw_threshold_line(self):
        """Helper to redraw horizontal red threshold bar on the rolling waveform visualizer."""
        if hasattr(self, 'canvas'):
            self.canvas.delete("thresh_line")
            thresh = self.config_manager.config["sensitivity"]
            y = self.canvas_height - (thresh / 32768.0) * self.canvas_height
            self.canvas.create_line(0, y, self.canvas_width, y, fill=self.c_red, dash=(4, 2), tags="thresh_line")
            
    def toggle_listening(self):
        """Toggles the live microphone listener between Active / Inactive states."""
        if self.detector.is_listening:
            self.detector.stop()
            self.toggle_btn.config(text="START LISTENING", bg=self.c_green)
        else:
            try:
                self.detector.start()
                self.toggle_btn.config(text="STOP LISTENING", bg=self.c_red)
            except RuntimeError as e:
                messagebox.showerror("Error", str(e))
            
    def update_status_display(self):
        """Redraws the LED status indicator dot and updates the text."""
        if not hasattr(self, 'led_canvas'):
            return
            
        self.led_canvas.delete("all")
        if self.detector.is_listening:
            current_time = time.time()
            if current_time - self.detector.last_trigger_time < self.config_manager.config["cooldown"]:
                fill_color = self.c_red
                status_text = "STATUS: COOLDOWN"
            else:
                fill_color = self.c_green
                status_text = "STATUS: ACTIVE"
        else:
            fill_color = self.c_gray
            status_text = "STATUS: INACTIVE"
            
        self.led_circle = self.led_canvas.create_oval(2, 2, 14, 14, fill=fill_color, outline="")
        self.status_label.config(text=status_text, fg=fill_color if fill_color != self.c_gray else self.c_gray)
        
    def simulate_slap(self):
        """Simulates a slap trigger manually (used for testing)."""
        self.trigger_queue.put(True)
        
    def update_gui_loop(self):
        """Ticks periodically (every 30ms) to read queues, update waveform, and handle UI flashes."""
        new_levels = []
        while True:
            try:
                new_levels.append(self.audio_queue.get_nowait())
            except queue.Empty:
                break
                
        if new_levels:
            avg_peak = sum(new_levels) / len(new_levels)
            self.audio_history.append(avg_peak)
        else:
            last_val = self.audio_history[-1] if self.audio_history else 0
            self.audio_history.append(max(0, last_val * 0.8))
            
        trigger_detected = False
        while True:
            try:
                self.trigger_queue.get_nowait()
                trigger_detected = True
            except queue.Empty:
                break
                
        if trigger_detected:
            played = self.detector.play_random_sound()
            
            self.slap_count += 1
            self.count_label.config(text=str(self.slap_count))
            self.config_manager.config["total_slaps"] = self.slap_count
            self.config_manager.save_config()
            
            self.slap_flash_ticks = 12
            
        self.canvas.delete("wave", "flash_text")
        
        if self.slap_flash_ticks > 0:
            flash_intensity = int((self.slap_flash_ticks / 12.0) * 80)
            hex_color = f"#{17 + flash_intensity:02x}111b"
            self.canvas.config(bg=hex_color)
            self.slap_flash_ticks -= 1
            
            self.canvas.create_text(
                self.canvas_width // 2, self.canvas_height // 2, 
                text="SLAP DETECTED!", font=("Helvetica", 18, "bold"), 
                fill=self.c_red, tags="flash_text"
            )
        else:
            self.canvas.config(bg=self.c_crust)
            
        points = []
        points.append(0)
        points.append(self.canvas_height)
        
        step_x = self.canvas_width / (len(self.audio_history) - 1)
        for i, val in enumerate(self.audio_history):
            x = i * step_x
            normalized_y = (val / 32768.0) * self.canvas_height
            y = self.canvas_height - normalized_y
            points.append(x)
            points.append(y)
            
        points.append(self.canvas_width)
        points.append(self.canvas_height)
        
        if len(points) >= 4:
            self.canvas.create_polygon(points, fill="#2b2d42", outline="", tags="wave")
            
            line_points = points[2:-2]
            if len(line_points) >= 4:
                self.canvas.create_line(line_points, fill=self.c_cyan, width=1.5, tags="wave")
                
        self.redraw_threshold_line()
        self.update_status_display()
        self.root.after(30, self.update_gui_loop)
        
    def on_close(self):
        """Triggered when window is closed. Cleans up threads and processes."""
        self.detector.stop()
        self.config_manager.save_config()
        self.root.destroy()
        
    def start(self):
        """Starts the Tkinter event loop."""
        self.root.mainloop()
