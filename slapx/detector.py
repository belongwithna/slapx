import os
import sys
import time
import queue
import struct
import random
import subprocess
import threading
from .constants import SAMPLE_RATE, CHUNK_SIZE

class SlapDetector:
    def __init__(self, config_manager, default_sounds, audio_queue, trigger_queue, on_slap_detected_callback=None):
        self.config_manager = config_manager
        self.default_sounds = default_sounds
        self.audio_queue = audio_queue
        self.trigger_queue = trigger_queue
        self.on_slap_detected_callback = on_slap_detected_callback
        
        self.is_listening = False
        self.last_trigger_time = 0.0
        self.arecord_process = None
        self.listener_thread = None

    def start(self):
        """Starts the background listening process and thread."""
        if self.is_listening:
            return True
        
        self.is_listening = True
        
        try:
            self.arecord_process = subprocess.Popen(
                ['arecord', '-q', '-f', 'S16_LE', '-r', str(SAMPLE_RATE), '-c', '1', '-t', 'raw'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            self.is_listening = False
            raise RuntimeError(f"Failed to start arecord. Is alsa-utils installed? {e}")
                
        self.listener_thread = threading.Thread(target=self._listener_loop, daemon=True)
        self.listener_thread.start()
        return True

    def stop(self):
        """Stops the listening thread and subprocess."""
        if not self.is_listening:
            return
            
        self.is_listening = False
        
        if self.arecord_process:
            try:
                self.arecord_process.terminate()
                self.arecord_process.wait()
            except Exception:
                pass
            self.arecord_process = None
            
        if self.listener_thread:
            try:
                self.listener_thread.join(timeout=1.0)
            except Exception:
                pass
            self.listener_thread = None

    def _listener_loop(self):
        """Background thread loop that reads microphone levels and detects spikes."""
        startup_bytes_to_skip = SAMPLE_RATE * 2 * 0.5  # 16000 * 2 bytes/sample * 0.5s = 16000 bytes
        bytes_skipped = 0
        
        while self.is_listening:
            try:
                raw_data = self.arecord_process.stdout.read(CHUNK_SIZE)
                if not raw_data:
                    break
                
                num_samples = len(raw_data) // 2
                if num_samples == 0:
                    continue
                samples = [val[0] for val in struct.iter_unpack("<h", raw_data)]
                
                peak = max(abs(x) for x in samples)
                
                # Push peak value to GUI queue (non-blocking)
                try:
                    self.audio_queue.put_nowait(peak)
                except queue.Full:
                    try:
                        self.audio_queue.get_nowait()
                        self.audio_queue.put_nowait(peak)
                    except queue.Empty:
                        pass
                
                if bytes_skipped < startup_bytes_to_skip:
                    bytes_skipped += len(raw_data)
                    continue
                    
                thresh = self.config_manager.config["sensitivity"]
                cooldown = self.config_manager.config["cooldown"]
                current_time = time.time()
                
                if peak >= thresh:
                    if current_time - self.last_trigger_time >= cooldown:
                        self.last_trigger_time = current_time
                        self.trigger_queue.put(True)
                        if self.on_slap_detected_callback:
                            self.on_slap_detected_callback()
                            
            except Exception as e:
                print(f"Error in listener loop: {e}", file=sys.stderr)
                break
                
        self.is_listening = False

    def play_random_sound(self):
        """Randomly selects one of the configured/active sounds and plays it via mpv."""
        sounds = self.config_manager.config["sounds"]
        active_sounds = [s for s in sounds if s and os.path.exists(s)]
        
        if not active_sounds:
            active_sounds = [s for s in self.default_sounds if os.path.exists(s)]
            
        if active_sounds:
            chosen = random.choice(active_sounds)
            try:
                subprocess.Popen(
                    ['mpv', '--no-terminal', '--volume=100', chosen],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return chosen
            except Exception as e:
                print(f"Error playing sound '{chosen}' with mpv: {e}", file=sys.stderr)
        return None
