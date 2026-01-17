import pyaudio
import time
import psutil
import numpy as np
#CONFIG
BUFFER_SIZE = 2048 
SAMPLE_RATE = 48000 
CHANNELS = 2 
GAIN = 1.0 
VB_CABLE_INPUT_INDEX = None  # CABLE Output (VB-Audio Virtual Cable)
#SPOTIFY CHECK
def is_spotify_running(): return any("spotify.exe" in p.name().lower() for p in psutil.process_iter())
#INIT
p = pyaudio.PyAudio()
#Find a usable playback device (not "Primary Sound Driver")
default_index = None 
default_name = None 
for i in range(p.get_device_count()): 
    info = p.get_device_info_by_index(i) 
    if info['maxOutputChannels'] > 0 and any(x in info['name'].lower() for x in ["speaker", "headphones", "output"]): 
        default_index = i 
        default_name = info['name'] 
        break
if default_index is None: 
    raise RuntimeError("Could not find a usable playback device.")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if (
    info['maxInputChannels'] == 2 and
    info['maxOutputChannels'] == 0 and
    "cable" in info['name'].lower() and
    "output" in info['name'].lower()):
        VB_CABLE_INPUT_INDEX = i
if VB_CABLE_INPUT_INDEX is None:
    raise RuntimeError("Could not find a usable input device.")

print("Waiting for Spotify to start...") 
while not is_spotify_running(): 
    time.sleep(2)
print("Spotify detected. Starting audio duplication...") 
print(f"Reading from VB-Cable index: {VB_CABLE_INPUT_INDEX}") 
print(f"Playing to output index: {default_index} ({default_name})") 
print(f"Applying gain: {GAIN}x")

#STREAM SETUP
stream_in = p.open(format=pyaudio.paFloat32, channels=CHANNELS, rate=SAMPLE_RATE, input=True, input_device_index=VB_CABLE_INPUT_INDEX, frames_per_buffer=BUFFER_SIZE)
stream_out = p.open(format=pyaudio.paFloat32, channels=CHANNELS, rate=SAMPLE_RATE, output=True, output_device_index=default_index, frames_per_buffer=BUFFER_SIZE)

#MAIN LOOP
try: 
    while True: 
        data = stream_in.read(BUFFER_SIZE, exception_on_overflow=False) 
        samples = np.frombuffer(data, dtype=np.float32) 
        boosted = np.clip(samples * GAIN, -1.0, 1.0).astype(np.float32).tobytes() 
        stream_out.write(boosted) 
except KeyboardInterrupt: print("Stopping...") 
finally: stream_in.stop_stream() 
stream_in.close() 
stream_out.stop_stream() 
stream_out.close() 
p.terminate()