# 🎧 Lofi Music Maker

Transform any audio into lofi-style music with vintage warmth, tape wobble, and atmospheric effects.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ai-developers-ng/generate-lofi-music.git
cd generate-lofi-music
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Or with pip3:
```bash
pip3 install -r requirements.txt
```

**Required packages:**
- PySide6 (Qt GUI framework)
- numpy (array processing)
- scipy (signal processing)
- librosa (audio processing)
- soundfile (audio I/O)

### 3. Optional: FFmpeg for MP3 Export
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Running the App

```bash
python3 main.py
```

## Basic Workflow

### 1. Load Audio
- Click **📁 Load Audio**
- Select your audio file (.wav, .flac, .mp3, .ogg)
- File name appears at the top

### 2. Choose a Preset
Select from 12 presets in the dropdown:

**Vintage Vibes:**
- 🎵 **Cozy Vinyl** - Classic warm vinyl sound
- 📼 **Tape Bedroom** - Heavy tape wobble
- 📻 **VHS Memory** - 80s VHS aesthetic

**Atmospheric:**
- 🌧️ **Rainy Night** - Reverb-heavy ambient
- ☁️ **Dreamy Clouds** - Ethereal spacious sound
- 🏖️ **Sunset Beach** - Warm beachy vibes

**Chill & Study:**
- 📚 **Chill Study** - Clean minimal processing
- ☕ **Coffee Shop** - Natural cafe ambience
- 🎷 **Jazz Cafe** - Authentic vinyl jazz

**Retro Digital:**
- 💾 **Nostalgic 90s** - Bitcrushed old-school hip-hop
- 🌃 **Late Night Drive** - Synthwave/retrowave
- 📡 **Midnight Radio** - AM radio simulation

### 3. Preview Your Sound

**Option A: Test the Preset**
- Click **▶️ Lofi Preview** to hear effects in real-time
- No export needed!

**Option B: Compare Original**
- Click **▶️ Original** to hear unprocessed audio
- Click **⏹️ Stop** to stop playback

### 4. Fine-Tune (Optional)
Adjust sliders for custom sound:
- 🔥 **Warmth** - Tape saturation/distortion
- 🌊 **Wobble** - Wow & flutter (tape speed variations)
- 📻 **Noise** - Vinyl crackle + tape hiss
- 🏠 **Room** - Reverb amount
- ⏱️ **Tempo** - Playback speed (0.8x - 1.05x)
- 🎵 **Pitch** - Pitch shift in semitones (-4 to +2)

**Tip:** After adjusting, click **🔄 Reset to Preset** to restore preset values

### 5. Export Your Lofi Track
- Click **✨ Render Lofi**
- Choose save location and format:
  - `.wav` - Lossless quality
  - `.mp3` - Compressed (requires ffmpeg)
- Watch the progress bar
- Done! ✅

## Preset Recommendations by Genre

### Hip-Hop / Beats
- Nostalgic 90s (bitcrushed)
- Tape Bedroom (heavy wobble)
- Cozy Vinyl (classic)

### Jazz / Instrumental
- Jazz Cafe
- Coffee Shop
- Chill Study

### Electronic / Synthwave
- Late Night Drive
- VHS Memory
- Midnight Radio

### Ambient / Meditation
- Dreamy Clouds
- Rainy Night
- Sunset Beach

## Keyboard Shortcuts

*Coming soon...*

## Tips & Tricks

### Getting the Best Lofi Sound:
1. Start with high-quality source audio
2. Try different presets first
3. Don't over-process (less is more!)
4. Preview before exporting
5. Use tempo slowdown (0.88-0.95x) for that classic lofi feel

### Preset Customization:
- Start from a preset you like
- Adjust 1-2 sliders at a time
- Preview to hear changes
- If you go too far, hit Reset

### Common Issues:
- **No sound in preview?** Check your system volume
- **MP3 export failed?** Install ffmpeg or use WAV format
- **Slow processing?** Large files take longer, be patient

## Advanced Usage

### Extreme Effects:
- Crank **Wobble** to 1.0 for underwater sound
- Set **Noise** to 0.5 for heavy vinyl aesthetic
- Use **Room** at 0.7+ for huge spacious sound

### Minimal Processing:
- Use **Chill Study** or **Coffee Shop**
- Keep Warmth below 0.4
- Noise below 0.08
- Perfect for clear but vintage sound

### Radio Simulation:
- Use **Midnight Radio** preset
- Adds bandpass filter (500Hz-4kHz)
- Heavy compression + static
- Authentic AM radio sound

## Technical Notes

### Supported Formats:
- **Input:** WAV, FLAC, MP3, OGG
- **Output:** WAV (always), MP3 (if ffmpeg installed)

### Processing Time:
- Depends on file length and effects
- Typical 3-minute song: 10-30 seconds
- Progress bar shows status

### System Requirements:
- Python 3.8+
- PySide6
- librosa, numpy, scipy, soundfile
- ffmpeg (optional, for MP3 export)

---

**Enjoy creating lofi music! 🎶**
