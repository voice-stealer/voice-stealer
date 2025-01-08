from TTS.api import TTS

tts = TTS("tts_models/rus/fairseq/vits")
tts.load_vc_model_by_name("voice_conversion_models/multilingual/vctk/freevc24")
