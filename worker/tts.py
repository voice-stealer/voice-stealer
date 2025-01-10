from TTS.api import TTS

from comparison import compare_audio

from metrics import latency, voice_similarity_gauge

class VoiceStealer:
    def __init__(self):
        self.tts = TTS("tts_models/rus/fairseq/vits")
        print('model loaded')

    @latency.time()
    def generate(self, request_id, text, speaker_filename):
        filepath = f"{request_id}.wav"
        self.tts.tts_with_vc_to_file(text, speaker_wav=speaker_filename, file_path=filepath)
        similarity = compare_audio(speaker_filename, filepath)
        print(similarity)
        voice_similarity_gauge.set(similarity)
        return filepath

