from pynput import keyboard
import time
from datetime import datetime
import pyaudio
import wave
import sched
import sys
import os

from recognizer import recognize_from_audio

CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "data/output"
DEV_INDEX=2

p = pyaudio.PyAudio()

class MyListener(keyboard.Listener):

    def __init__(self):
        super(MyListener, self).__init__(self.on_press, self.on_release)
        self.key_pressed = {}
        self.recording = {}
        self.audio_file_name = WAVE_OUTPUT_FILENAME + ".wav"
        self.text_file_name = ""
        self.wf = None

    def set_file_name(self):
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        self.audio_file_name = f"{WAVE_OUTPUT_FILENAME}_audio_{ts}.wav"
        self.text_file_name = f"{WAVE_OUTPUT_FILENAME}_text_{ts}.txt"

    def on_press(self, key):
        if key.char == 'r':
            self.key_pressed = True
            self.recording = True
            self.set_file_name()
        if key.char == 's':
            self.recording = False
        return True

    def on_release(self, key):
        if key.char == 'r':
            self.key_pressed = False
        return True

    def open_file(self):
        self.wf = wave.open(self.audio_file_name, 'wb')
        self.wf.setnchannels(CHANNELS)
        self.wf.setsampwidth(p.get_sample_size(FORMAT))
        self.wf.setframerate(RATE)
    
    def save_text(self, text):
        with open(self.text_file_name, "w", encoding="utf-8") as fh:
            fh.write(text)

    def close_file(self, frames):
        self.wf.writeframes(b''.join(frames))
        self.wf.close()
        text = recognize_from_audio(self.audio_file_name)
        print(text)
        self.save_text(text)

class Recorder(object):

    def __init__(self):
        self.listener = MyListener()
        self.listener.start()
        self.started = False
        self.stream = None
        self.frames = []

    def callback(self, in_data, frame_count, time_info, status):
        self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    def recorder(self):
        self.listener.open_file()
        if self.listener.recording and not self.started:
            # Start the recording
            try:
                self.stream = p.open(format = FORMAT,
                                channels = CHANNELS,
                                rate = RATE,
                                input_device_index = DEV_INDEX,
                                input = True,
                                frames_per_buffer = CHUNK,
                                stream_callback = self.callback)
                print("Stream active:", self.stream.is_active())
                self.started = True
                print("start Stream")
            except:
                raise

        elif not self.listener.recording and self.started:
            print("Stop recording")
            self.stream.stop_stream()
            self.stream.close()
            p.terminate()
            self.listener.close_file(self.frames)
            os.remove("data/output.wav")
            print("You should have a wav and txt files in the data directory")
            sys.exit()

        # Reschedule the recorder function in 100 ms.
        self.task.enter(0.1, 1, self.recorder, ())

    def start_keyboard(self):
        print("Press the 'r' key to begin recording")
        print("Press the 's' key to begin recording")
        self.task = sched.scheduler(time.time, time.sleep)
        self.task.enter(0.1, 1, self.recorder, ())
        self.task.run()