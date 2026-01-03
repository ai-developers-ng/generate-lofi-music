import math

import librosa
import numpy as np
from scipy.signal import butter, fftconvolve, lfilter


def apply_pipeline(audio, sr, params):
    processed = audio.copy()

    processed = _time_stretch(processed, params.get("time_stretch", 1.0))
    processed = _pitch_shift(processed, sr, params.get("pitch_shift", 0.0))
    processed = _highpass(processed, sr, params.get("highpass_hz", 30))
    processed = _lowpass(processed, sr, params.get("lowpass_hz", 14000))
    processed = _low_shelf(processed, sr, 200, params.get("bass_db", 0.0))
    processed = _high_shelf(processed, sr, params.get("highshelf_freq", 10000), params.get("highshelf_db", 0.0))
    processed = _saturate(processed, params.get("saturation", 0.0))
    processed = _compress(processed, params.get("compression", 0.0))
    processed = _bitcrush(processed, sr, params.get("bitcrush", 0.0))
    processed = _wow_flutter(processed, sr, params.get("wow_flutter", 0.0))
    processed = _stereo_width(processed, params.get("stereo_width", 1.0))
    processed = _noise(processed, params.get("noise", 0.0))
    processed = _reverb(processed, sr, params.get("reverb", 0.0))
    processed = _limit(processed, params.get("limiter", 0.95))

    return processed


def _time_stretch(audio, rate):
    if rate == 1.0:
        return audio
    return _apply_per_channel(audio, lambda ch: librosa.effects.time_stretch(ch, rate=rate))


def _pitch_shift(audio, sr, n_steps):
    if n_steps == 0.0:
        return audio
    return _apply_per_channel(
        audio, lambda ch: librosa.effects.pitch_shift(ch, sr=sr, n_steps=n_steps)
    )


def _lowpass(audio, sr, cutoff_hz):
    if cutoff_hz >= (sr / 2.0):
        return audio
    b, a = butter(4, cutoff_hz / (sr / 2.0), btype="low")
    return lfilter(b, a, audio, axis=0)


def _highpass(audio, sr, cutoff_hz):
    if cutoff_hz <= 0.0:
        return audio
    b, a = butter(4, cutoff_hz / (sr / 2.0), btype="high")
    return lfilter(b, a, audio, axis=0)


def _low_shelf(audio, sr, freq, gain_db):
    if gain_db == 0.0:
        return audio

    a = 10 ** (gain_db / 40.0)
    w0 = 2 * math.pi * freq / sr
    cos_w0 = math.cos(w0)
    sin_w0 = math.sin(w0)
    alpha = sin_w0 / 2 * math.sqrt((a + 1 / a) * (1 / 1.0 - 1) + 2)

    b0 = a * ((a + 1) - (a - 1) * cos_w0 + 2 * math.sqrt(a) * alpha)
    b1 = 2 * a * ((a - 1) - (a + 1) * cos_w0)
    b2 = a * ((a + 1) - (a - 1) * cos_w0 - 2 * math.sqrt(a) * alpha)
    a0 = (a + 1) + (a - 1) * cos_w0 + 2 * math.sqrt(a) * alpha
    a1 = -2 * ((a - 1) + (a + 1) * cos_w0)
    a2 = (a + 1) + (a - 1) * cos_w0 - 2 * math.sqrt(a) * alpha

    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return lfilter(b, a, audio, axis=0)


def _high_shelf(audio, sr, freq, gain_db):
    """High-shelf filter for treble roll-off (vintage tape characteristic)"""
    if gain_db == 0.0:
        return audio

    a = 10 ** (gain_db / 40.0)
    w0 = 2 * math.pi * freq / sr
    cos_w0 = math.cos(w0)
    sin_w0 = math.sin(w0)
    alpha = sin_w0 / 2 * math.sqrt((a + 1 / a) * (1 / 1.0 - 1) + 2)

    b0 = a * ((a + 1) + (a - 1) * cos_w0 + 2 * math.sqrt(a) * alpha)
    b1 = -2 * a * ((a - 1) + (a + 1) * cos_w0)
    b2 = a * ((a + 1) + (a - 1) * cos_w0 - 2 * math.sqrt(a) * alpha)
    a0 = (a + 1) - (a - 1) * cos_w0 + 2 * math.sqrt(a) * alpha
    a1 = 2 * ((a - 1) - (a + 1) * cos_w0)
    a2 = (a + 1) - (a - 1) * cos_w0 - 2 * math.sqrt(a) * alpha

    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return lfilter(b, a, audio, axis=0)


def _saturate(audio, amount):
    if amount <= 0.0:
        return audio
    drive = 1.0 + amount * 4.0
    return np.tanh(audio * drive) / np.tanh(drive)


def _bitcrush(audio, sr, amount):
    """Simulate lo-fi digital artifacts with bit depth and sample rate reduction"""
    if amount <= 0.0:
        return audio
    
    # Bit depth reduction
    bits = 16 - int(amount * 12)  # 16-bit down to 4-bit
    levels = 2 ** bits
    crushed = np.round(audio * levels) / levels
    
    # Sample rate reduction (simulate old samplers)
    if amount > 0.3:
        downsample_factor = 1 + int(amount * 8)
        crushed = crushed[::downsample_factor]
        # Upsample back (with aliasing artifacts)
        crushed = np.repeat(crushed, downsample_factor, axis=0)
        # Trim to original length
        if len(crushed) > len(audio):
            crushed = crushed[:len(audio)]
        elif len(crushed) < len(audio):
            pad = np.zeros((len(audio) - len(crushed), audio.shape[1]))
            crushed = np.vstack([crushed, pad])
    
    return crushed


def _compress(audio, amount):
    if amount <= 0.0:
        return audio
    threshold = 0.5
    ratio = 1.0 + amount * 4.0
    attack = 0.01
    release = 0.1

    env = np.zeros(audio.shape[0], dtype=np.float32)
    gain = np.ones_like(env)
    for i in range(1, len(env)):
        env[i] = max(abs(audio[i]).max(), env[i - 1] * (1 - release))
        target = 1.0
        if env[i] > threshold:
            target = (threshold + (env[i] - threshold) / ratio) / env[i]
        coeff = attack if target < gain[i - 1] else release
        gain[i] = gain[i - 1] + coeff * (target - gain[i - 1])
    return audio * gain[:, None]


def _wow_flutter(audio, sr, amount):
    if amount <= 0.0:
        return audio
    depth = 0.003 * amount
    # Multiple modulation frequencies for more realistic tape mechanics
    t = np.arange(audio.shape[0]) / sr
    slow_mod = depth * np.sin(2 * math.pi * 0.5 * t)  # 0.5 Hz slow wow
    fast_mod = (depth * 0.3) * np.sin(2 * math.pi * 5.0 * t)  # 5 Hz fast flutter
    mod = slow_mod + fast_mod
    return _fractional_delay(audio, mod * sr)


def _stereo_width(audio, width):
    """Adjust stereo width using mid/side processing"""
    if width == 1.0 or audio.shape[1] < 2:
        return audio
    
    # Convert to mid/side
    mid = (audio[:, 0] + audio[:, 1]) / 2
    side = (audio[:, 0] - audio[:, 1]) / 2
    
    # Adjust width (0 = mono, 1 = normal, 2 = wide)
    side = side * width
    
    # Convert back to left/right
    left = mid + side
    right = mid - side
    
    return np.stack([left, right], axis=1)


def _noise(audio, amount):
    """Enhanced noise with pink noise, vinyl crackle, and tape hiss"""
    if amount <= 0.0:
        return audio
    
    output = audio.copy()
    
    # Pink noise (more natural than white noise) - reduced intensity
    pink = _generate_pink_noise(audio.shape)
    output += pink * amount * 0.004  # Reduced from 0.008
    
    # Vinyl crackle (random pops) - only at higher amounts
    if amount > 0.2:
        crackle_density = amount * 0.00005  # Reduced from 0.0001
        crackle = np.random.random(audio.shape) < crackle_density
        crackle_audio = crackle.astype(float) * np.random.uniform(-0.3, 0.3, audio.shape)
        output += crackle_audio * amount * 0.5
    
    # Tape hiss (filtered white noise) - very subtle
    if amount > 0.05:
        hiss = np.random.normal(0.0, 0.003, size=audio.shape)  # Reduced from 0.005
        output += hiss * amount * 0.5
    
    return output


def _generate_pink_noise(shape):
    """Generate pink noise (1/f noise) for more natural sound"""
    white = np.random.randn(shape[0], shape[1])
    # Simple pink noise approximation using multiple octaves
    pink = np.zeros_like(white)
    octaves = [1, 2, 4, 8, 16]
    for octave in octaves:
        if shape[0] // octave > 0:
            resampled = np.repeat(np.random.randn(shape[0] // octave, shape[1]), octave, axis=0)
            pink[:len(resampled)] += resampled[:shape[0]] / octave
    return pink / len(octaves)


def _reverb(audio, sr, amount):
    if amount <= 0.0:
        return audio
    decay = 0.3 + 1.2 * amount
    length = int(sr * 0.4)
    impulse = np.exp(-np.linspace(0, decay, length))
    impulse[0] = 1.0
    wet = np.vstack(
        [fftconvolve(audio[:, ch], impulse, mode="full")[: audio.shape[0]] for ch in range(audio.shape[1])]
    ).T
    return (1 - amount) * audio + amount * wet


def _limit(audio, ceiling):
    """Soft limiter to preserve dynamics"""
    if ceiling <= 0.0:
        return audio
    peak = np.max(np.abs(audio))
    if peak <= ceiling:
        return audio
    # Soft limiting with gentle knee
    ratio = ceiling / peak
    return audio * (ratio * 0.95)  # Leave some headroom


def _apply_per_channel(audio, fn):
    channels = []
    for ch in range(audio.shape[1]):
        channels.append(fn(audio[:, ch]))
    min_len = min(len(ch) for ch in channels)
    stacked = np.stack([ch[:min_len] for ch in channels], axis=1)
    return stacked


def _fractional_delay(audio, delay_samples):
    out = np.zeros_like(audio)
    max_index = audio.shape[0] - 1
    for i in range(audio.shape[0]):
        idx = i - delay_samples[i]
        if idx <= 0 or idx >= max_index:
            continue
        i0 = int(math.floor(idx))
        if i0 >= max_index:
            continue
        i1 = i0 + 1
        frac = idx - i0
        out[i] = (1 - frac) * audio[i0] + frac * audio[i1]
    return out
