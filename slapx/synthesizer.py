import os
import math
import wave
import struct
import random
from .constants import SOUNDS_DIR

def synthesize_defaults():
    """Synthesizes three default funny WAV sounds if they don't exist."""
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    
    s1_path = os.path.abspath(os.path.join(SOUNDS_DIR, "default_ouch.wav"))
    if not os.path.exists(s1_path):
        with wave.open(s1_path, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(44100)
            num_samples = int(44100 * 0.4)
            for i in range(num_samples):
                t = i / 44100
                freq = 800 * math.exp(-15 * t) + 150
                vol = 32767 * math.exp(-8 * t)
                val = int(vol * math.sin(2 * math.pi * freq * t))
                w.writeframes(struct.pack('<h', val))
                
    s2_path = os.path.abspath(os.path.join(SOUNDS_DIR, "default_laser.wav"))
    if not os.path.exists(s2_path):
        with wave.open(s2_path, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(44100)
            num_samples = int(44100 * 0.3)
            for i in range(num_samples):
                t = i / 44100
                freq = 2200 * (1.0 - t/0.3) + 120
                vol = 32767 * (1.0 - t/0.3)**2
                val = int(vol * math.sin(2 * math.pi * freq * t))
                w.writeframes(struct.pack('<h', val))
                
    s3_path = os.path.abspath(os.path.join(SOUNDS_DIR, "default_slap.wav"))
    if not os.path.exists(s3_path):
        with wave.open(s3_path, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(44100)
            num_samples = int(44100 * 0.25)
            for i in range(num_samples):
                t = i / 44100
                vol = 32767 * math.exp(-22 * t)
                noise = random.uniform(-1, 1) * 0.45
                sine = math.sin(2 * math.pi * 280 * t) * 0.55
                val = int(vol * (noise + sine))
                val = max(-32768, min(32767, val))
                w.writeframes(struct.pack('<h', val))
                
    return [s1_path, s2_path, s3_path]

