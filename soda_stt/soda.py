import logging
import ctypes
from pathlib import Path

from soda_stt.soda_api_pb2 import ExtendedSodaConfigMsg, SodaResponse, SodaRecognitionResult

CHANNEL_COUNT = 1
SAMPLE_RATE = 16000
CHUNK_SIZE = 2048  # 2 chunks per frame, a frame is a single s16

CALLBACK = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_byte), ctypes.c_int, ctypes.c_void_p)

_LOGGER = logging.getLogger(__name__)


class SodaConfig(ctypes.Structure):
    _fields_ = [('soda_config', ctypes.c_char_p),
                ('soda_config_size', ctypes.c_int),
                ('callback', CALLBACK),
                ('callback_handle', ctypes.c_void_p)]


def soda_client_callback(recognition_result):
    pass


class SodaClient:

    def __init__(self, data_dir, language, channel_count=CHANNEL_COUNT, sample_rate=SAMPLE_RATE,
                 callback=soda_client_callback):
        self.text = None
        self.handle = None
        self.language = language
        data_dir = Path(data_dir)
        self.sodalib = ctypes.CDLL(str(data_dir / 'libsoda.so'))
        self.callback = callback
        cfg_proto = ExtendedSodaConfigMsg()
        cfg_proto.channel_count = channel_count
        cfg_proto.sample_rate = sample_rate
        cfg_proto.recognition_mode = 2
        cfg_proto.api_key = 'dummy_api_key'
        cfg_proto.language_pack_directory = str(data_dir / self.language)
        cfg_serialized = cfg_proto.SerializeToString()
        self.config = SodaConfig(cfg_serialized, len(cfg_serialized), CALLBACK(self.result_handler), None)
        self.is_initialized = False
        self.is_running = False
        self.sodalib.CreateExtendedSodaAsync.restype = ctypes.c_void_p

    def __del__(self):
        self.delete()

    def create(self):
        if not self.is_initialized:
            self.handle = ctypes.c_void_p(self.sodalib.CreateExtendedSodaAsync(self.config))
            self.is_initialized = True

    def delete(self):
        if self.is_initialized:
            self.sodalib.DeleteExtendedSodaAsync(self.handle)
            self.is_initialized = False

    def start(self):
        self.sodalib.ExtendedSodaStart(self.handle)

    def stop(self):
        self.sodalib.ExtendedSodaStop(self.handle)

    def release(self):
        if self.is_running:
            self.stop()
            self.is_running = False

    def add_audio(self, audio):
        self.sodalib.ExtendedAddAudio(self.handle, audio, len(audio))

    # def add_audio(self, audio):
    #     if len(audio) > CHUNK_SIZE:
    #         pass
    #         for idx in range(0, len(audio), CHUNK_SIZE):
    #             chunk = audio[idx: idx + CHUNK_SIZE]
    #             self.sodalib.ExtendedAddAudio(self.handle, chunk, len(chunk))
    #     else:
    #         chunk = audio
    #         self.sodalib.ExtendedAddAudio(self.handle, chunk, len(chunk))

    def mark_done(self):
        self.sodalib.ExtendedSodaMarkDone(self.handle)

    def begin(self):
        if not self.is_initialized:
            self.create()
        self.is_running = True
        self.text = None
        self.start()

    def end(self):
        self.mark_done()
        while self.is_running:
            pass
        self.stop()
        # self.delete()
        return self.text

    def result_handler(self, response, rlen, instance):
        res = SodaResponse()
        res.ParseFromString(ctypes.string_at(response, rlen))
        if res.soda_type == SodaResponse.SodaMessageType.RECOGNITION:
            if res.recognition_result.result_type == SodaRecognitionResult.ResultType.FINAL:
                self.text = res.recognition_result.hypothesis[0]
                self.is_running = False
                if self.callback:
                    self.callback(res.recognition_result)
        if res.soda_type == SodaResponse.SodaMessageType.STOP:
            self.is_running = False
            if self.callback:
                self.callback(None)
