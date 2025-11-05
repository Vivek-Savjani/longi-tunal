import sounddevice as sd
import numpy as np
from collections import deque
import time
BASS_LOW = 20
BASS_HIGH = 150
WINDOW_SEC = 5
THRESHOLD_MULT = 1.5 
beat_times = deque()
prev_bass_amp = 0 
SR = 44100
BLOCK_SIZE = 1024  # Number of frames per read

# Find VB Cable device
devices = sd.query_devices()
device_index = None
for i, d in enumerate(devices):
    if "cable output" in d["name"].lower():
        print("Found VB Cable device:", d["name"])
        device_index = i
        break

if device_index is None:
    raise RuntimeError("VB Cable not found. Make sure it's installed and enabled.")

def get_amplitude(indata):
    mono = np.mean(indata, axis=1)
    amplitude = np.sqrt(np.mean(mono ** 2)) * 300
    return f"{amplitude:.2f}"

def get_current_bpm(indata):
    global prev_bass_amp, beat_times
    mono = np.mean(indata, axis=1)

    spectrum = np.fft.rfft(mono)
    freqs = np.fft.rfftfreq(len(mono), 1/SR)
    bass_range = (freqs >= BASS_LOW) & (freqs <= BASS_HIGH)
    bass_amp = np.mean(np.abs(spectrum[bass_range]))

    now = time.time()

    if bass_amp > prev_bass_amp * THRESHOLD_MULT and bass_amp > 0.2:
        if len(beat_times) == 0 or now - beat_times[-1] > 0.2:  # avoid double-counting
            beat_times.append(now)

    prev_bass_amp = bass_amp

    while beat_times and now - beat_times[0] > WINDOW_SEC:
        beat_times.popleft()

    if len(beat_times) > 1:
        intervals = np.diff(beat_times)
        bpm = 60 / np.mean(intervals)
    else:
        bpm = 0

    return f"{bpm:.0f}"

with sd.InputStream(channels=2, samplerate=SR, blocksize=BLOCK_SIZE, device=device_index) as stream:
    while True:
        indata, _ = stream.read(BLOCK_SIZE)
        amplitude = get_amplitude(indata)
        bpm = get_current_bpm(indata)
        print(bpm, amplitude)