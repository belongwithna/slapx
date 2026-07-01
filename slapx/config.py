import os
import json
from .constants import DEFAULT_CONFIG_FILE, MAX_SLOTS

class ConfigManager:
    def __init__(self, config_path=None, initial_threshold=8000, initial_cooldown=1.5):
        if config_path is None:
            # Keep it in the working directory as the original code did
            config_path = os.path.abspath(DEFAULT_CONFIG_FILE)
        self.config_path = config_path
        self.config = {}
        self.load_config(initial_threshold, initial_cooldown)

    def load_config(self, default_thresh, default_cooldown):
        """Loads config from json file, creates a default one if not found."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config.json: {e}. Reverting to defaults.")
                self.config = {}
        else:
            self.config = {}
            
        # Set default values if not present
        if "sensitivity" not in self.config:
            self.config["sensitivity"] = default_thresh
        if "cooldown" not in self.config:
            self.config["cooldown"] = default_cooldown
        if "sounds" not in self.config:
            self.config["sounds"] = ["" for _ in range(MAX_SLOTS)]
        if "total_slaps" not in self.config:
            self.config["total_slaps"] = 0
            
        self.save_config()

    def save_config(self):
        """Saves current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Failed to save config: {e}")
