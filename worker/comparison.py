from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import librosa

def load_audio(file_path):
    wav, sr = librosa.load(file_path, sr=None)
    return preprocess_wav(wav, source_sr=sr)

def compare_audio(audio1, audio2):
    reference_wav = load_audio(audio1)
    test_wav = load_audio(audio2)

    encoder = VoiceEncoder()

    reference_embedding = encoder.embed_utterance(reference_wav)
    test_embedding = encoder.embed_utterance(test_wav)

    similarity = np.dot(reference_embedding, test_embedding) / (np.linalg.norm(reference_embedding) * np.linalg.norm(test_embedding))
    return similarity


