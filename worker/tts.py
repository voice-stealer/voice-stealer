from TTS.api import TTS

from metrics import latency

class VoiceStealer:
    def __init__(self):
        self.tts = TTS("tts_models/rus/fairseq/vits")
        print('model loaded')

    @latency.time()
    def generate(self, request_id, text, speaker_filename):
        filepath = f"{request_id}.wav"
        self.tts.tts_with_vc_to_file(text, speaker_wav=speaker_filename, file_path=filepath)
        return filepath

