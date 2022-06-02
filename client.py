import socket
import time
import wave
import logging
import argparse
import pyaudio

parser = argparse.ArgumentParser()
parser.add_argument("--host", dest="receiver_host", type=str,  required=True, help="Server hostname")
command_group = parser.add_mutually_exclusive_group(required=False)
command_group.add_argument("-fr", dest="from_record", action='store_true',  default=False,
                           help="Start mic recording for 5 seconds")
command_group.add_argument("-ff", dest="from_file", required=False, type=str, help="File to be streamed and sent",
                    default="test.wav")

options = parser.parse_args()
logging.basicConfig(level=logging.DEBUG)

CHUNK = 1024
RATE = 44100
RECORD_SECONDS = 5
SERVICE_PORT = 8686


class Client():
    def __init__(self, host, port, fromfile, record=False):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.connect((self.host, self.port))
        self.log = logging.getLogger(__name__)
        self.record = record
        self.from_file = fromfile

    def start_streaming(self):
        self.log.info(" ## Ready to start streaming...")
        try:
            if self.record:
                port_to_send_audio, frames = self.get_frames_from_record()
            else:
                port_to_send_audio, frames = self.get_frames_from_file()
            if port_to_send_audio:
                for frame in frames:
                    self.udp_socket.sendto(frame, (self.host, int(port_to_send_audio)))
                    time.sleep(0.005)
            else:
                self.log.critical("No port has been provided!")

        except Exception as Ex:
            self.log.critical(Ex)

    def get_frames_from_record(self):
        frames = []

        channels = 1
        sample_width = 2

        audio = pyaudio.PyAudio()
        self.client.send(bytes(f"start {channels} {sample_width} {RATE}", encoding='UTF-8'))
        port_to_send_audio = self.client.recv(1024).decode()

        # start Recording
        stream = audio.open(format=pyaudio.paInt16, channels=1,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        self.log.info(f"Recording for {RECORD_SECONDS} seconds...")

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        self.log.info("Finished recording")

        return port_to_send_audio, frames

    def get_frames_from_file(self):
        frames = []

        wf = wave.open(self.from_file, 'rb')
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        frame_rate = wf.getframerate()

        self.log.debug(f"Filename: {self.from_file}, Channels: {channels}, "
                       f"Sample width: {sample_width}, Frame rate: {frame_rate}")

        self.client.send(bytes(f"start {channels} {sample_width} {frame_rate}", encoding='UTF-8'))
        port_to_send_audio = self.client.recv(1024).decode()

        while audio_data := wf.readframes(CHUNK):
            frames.append(audio_data)

        return port_to_send_audio, frames

    def stop_streaming(self):
        self.log.info(" ## Stop streaming")
        self.client.send(bytes("stop", encoding='UTF-8'))
        time.sleep(0.5)


client = Client(host=options.receiver_host, port=SERVICE_PORT,
                fromfile=options.from_file, record=options.from_record)
client.start_streaming()
client.stop_streaming()
