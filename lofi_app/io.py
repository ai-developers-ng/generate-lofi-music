import soundfile as sf


def load_audio(path):
    audio, sr = sf.read(path, always_2d=True)
    return audio, sr


def save_audio(path, audio, sr):
    sf.write(path, audio, sr)
