"""Diagnose sounddevice/PortAudio issues on Windows."""
import sys
import platform

print("=" * 60)
print("Audio Diagnostics")
print("=" * 60)
print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Architecture: {platform.architecture()}")

import sounddevice as sd
print(f"\nsounddevice version: {sd.__version__}")

# Check PortAudio library info
try:
    pa_ver = sd.get_portaudio_version()
    print(f"PortAudio version: {pa_ver}")
except Exception as e:
    print(f"PortAudio version: ERROR - {e}")

# List host APIs
print("\n--- Host APIs ---")
try:
    apis = sd.query_hostapis()
    for api in apis:
        print(f"  [{api['index']}] {api['name']} - {api['device_count']} devices "
              f"(default in: {api['default_input_device']}, out: {api['default_output_device']})")
except Exception as e:
    print(f"  ERROR: {e}")

# Try each input device individually with detailed error info
print("\n--- Input Device Probe ---")
devices = sd.query_devices()
for i, dev in enumerate(devices):
    if dev["max_input_channels"] > 0:
        sr = int(dev["default_samplerate"])
        hostapi_name = apis[dev["hostapi"]]["name"] if dev["hostapi"] < len(apis) else "?"
        print(f"\n  Device [{i}] {dev['name']}")
        print(f"    Host API: {hostapi_name} (idx {dev['hostapi']})")
        print(f"    Max input channels: {dev['max_input_channels']}")
        print(f"    Default SR: {sr}")
        print(f"    Low input latency: {dev['default_low_input_latency']}")
        print(f"    High input latency: {dev['default_high_input_latency']}")

        # Try to open at native rate
        for test_sr in [sr, 16000, 44100, 48000]:
            try:
                stream = sd.InputStream(
                    device=i,
                    samplerate=test_sr,
                    channels=1,
                    blocksize=1024,
                    dtype="float32",
                )
                stream.start()
                import time
                time.sleep(0.05)
                stream.stop()
                stream.close()
                print(f"    @ {test_sr}Hz: OK")
                break
            except Exception as e:
                err_short = str(e).split('\n')[0][:80]
                print(f"    @ {test_sr}Hz: FAIL - {err_short}")

# Try PyAudio as alternative
print("\n--- PyAudio Check ---")
try:
    import pyaudio
    pa = pyaudio.PyAudio()
    print(f"  PyAudio version: {pyaudio.get_portaudio_version_text()}")
    info = pa.get_default_input_device_info()
    print(f"  Default input: {info['name']} @ {info['defaultSampleRate']}Hz")
    
    # Try to open a stream
    stream = pa.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=int(info['defaultSampleRate']),
        input=True,
        frames_per_buffer=1024,
    )
    stream.read(1024)
    stream.close()
    pa.terminate()
    print("  PyAudio stream: OK")
except ImportError:
    print("  PyAudio not installed")
except Exception as e:
    print(f"  PyAudio error: {e}")
    try:
        pa.terminate()
    except:
        pass

print("\n" + "=" * 60)
print("Diagnostics complete")
print("=" * 60)
