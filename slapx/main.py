import os
import sys
import time
import queue
import argparse
from .constants import MAX_SLOTS
from .config import ConfigManager
from .synthesizer import synthesize_defaults
from .detector import SlapDetector

class SlapDetectorApp:
    def __init__(self, headless=False, initial_threshold=8000, initial_cooldown=1.5):
        self.headless = headless
        
        # Load configuration manager
        self.config_manager = ConfigManager(initial_threshold=initial_threshold, initial_cooldown=initial_cooldown)
        
        # Synthesize default sounds
        self.default_sounds = synthesize_defaults()
        
        # Resolve config sounds - if empty, use default synthesized sounds
        self.resolve_sounds()
        
        # Multithreading communication queues
        self.audio_queue = queue.Queue(maxsize=100)
        self.trigger_queue = queue.Queue()
        
        # Create detector
        # If headless, we pass a callback to log and trigger sound play on detection
        on_slap = self.trigger_slap_headless if self.headless else None
        self.detector = SlapDetector(
            config_manager=self.config_manager,
            default_sounds=self.default_sounds,
            audio_queue=self.audio_queue,
            trigger_queue=self.trigger_queue,
            on_slap_detected_callback=on_slap
        )
        
        if self.headless:
            self.run_headless()
        else:
            # Lazy import to avoid needing Tkinter if running headless
            from .gui import SlapDetectorGUI
            self.gui = SlapDetectorGUI(
                config_manager=self.config_manager,
                detector=self.detector,
                audio_queue=self.audio_queue,
                trigger_queue=self.trigger_queue,
                default_sounds=self.default_sounds
            )
            
    def resolve_sounds(self):
        """Updates blank config slots with synthesized defaults so we are ready to play."""
        sounds = self.config_manager.config["sounds"]
        for i in range(MAX_SLOTS):
            if not sounds[i]:
                sounds[i] = self.default_sounds[i]
        self.config_manager.save_config()

    def trigger_slap_headless(self):
        """Trigger code executed inside the background thread when running headless."""
        slap_count = self.config_manager.config.get("total_slaps", 0) + 1
        self.config_manager.config["total_slaps"] = slap_count
        self.config_manager.save_config()
        
        # Play the sound
        played = self.detector.play_random_sound()
        print(f"[{time.strftime('%H:%M:%S')}] SLAP DETECTED! Total: {slap_count} | Played: {os.path.basename(played) if played else 'None'}")

    def run_headless(self):
        """Runs the application in terminal/headless mode."""
        print("====================================================")
        print("  SLAPX - Headless Slap Detector Active")
        print(f"  Config: {self.config_manager.config_path}")
        print(f"  Sensitivity: {self.config_manager.config['sensitivity']}")
        print(f"  Cooldown: {self.config_manager.config['cooldown']}s")
        active_list = [os.path.basename(s) for s in self.config_manager.config["sounds"] if s]
        print(f"  Audio Tracks: {', '.join(active_list)}")
        print("====================================================")
        print("Press Ctrl+C to stop.")
        
        try:
            self.detector.start()
            while self.detector.is_listening:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.detector.stop()

    def start(self):
        """Starts the app GUI."""
        if not self.headless:
            self.gui.start()

def main():
    parser = argparse.ArgumentParser(description="Slapx - Laptop Slap Detector Soundboard")
    parser.add_argument("--headless", action="store_true", help="Run without GUI in terminal mode")
    parser.add_argument("--sensitivity", type=int, default=8000, help="Initial threshold amplitude (1000 - 32000)")
    parser.add_argument("--cooldown", type=float, default=1.5, help="Initial delay in seconds (0.1 - 5.0)")
    
    args = parser.parse_args()
    
    app = SlapDetectorApp(
        headless=args.headless, 
        initial_threshold=args.sensitivity, 
        initial_cooldown=args.cooldown
    )
    
    if not args.headless:
        app.start()
