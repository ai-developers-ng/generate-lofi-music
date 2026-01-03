# 🎧 Lofi Music Maker App — Development Plan

## 1. Product Vision
Create an app that transforms any user-owned music into **lofi-style audio** with one tap.

**Core vibe:**
- Warm
- Chill
- Vintage
- Relaxing

---

## 2. MVP Definition

### 🎯 Goal
Convert uploaded music into lofi-style audio using DSP (no AI initially).

### ✅ MVP Features
- Upload audio (user-owned files)
- Apply lofi processing
- Preview result
- Export MP3/WAV
- Preset-based experience

---

## 3. Lofi Sound Design (DSP Chain)

**Core Processing Pipeline:**
1. **Time Stretch** → 0.85–0.95x
2. **Pitch Shift** → −1 to −3 semitones (optional)
3. **EQ**
   - Low-pass: 10–14 kHz  
   - Slight bass boost
4. **Saturation**
   - Tape-style soft clipping
5. **Compression**
   - Gentle glue compression
6. **Wow & Flutter**
   - Subtle pitch modulation
7. **Noise Layer**
   - Vinyl crackle / tape hiss
8. **Reverb**
   - Small room or plate
9. **Limiter**
   - Final output protection

---

## 4. Presets (v1)

| Preset Name | Description |
|------------|-------------|
| Cozy Vinyl | Warm, soft highs, subtle crackle |
| Tape Bedroom | Wobbly pitch + warm saturation |
| Rainy Night | Reverb + rain ambience |
| Chill Study | Clean, soft compression |

---

## 5. UX Flow

### Main Screen
- Upload / Import audio
- Preset selector (chips)
- Knobs:
  - Warmth
  - Wobble
  - Noise
  - Room
  - Tempo
  - Pitch
- A/B preview (Original vs Lofi)
- Export button

---

## 6. Tech Stack

### Mobile (Recommended)
- **iOS:** Swift + AVAudioEngine / AudioKit  
- **Android:** Kotlin + Oboe / Superpowered  
- **Cross-platform:** Flutter + native DSP modules  

### DSP Libraries
- Rubber Band (time stretch / pitch)
- SoundTouch (lightweight option)
- Custom EQ, saturation, noise

### Backend (Optional)
- AWS Lambda + API Gateway
- S3 for exports
- Cognito for auth

---

## 7. Legal & Safety
- Only allow **user-owned audio**
- No Spotify / YouTube ripping
- Clear Terms of Use
- User owns output audio

---

## 8. Development Roadmap

### Phase 0 – Research (2–3 days)
- Collect royalty-free test tracks
- Define “good lofi” benchmarks

### Phase 1 – Core Engine
- Offline processing pipeline
- Preset system
- WAV export

### Phase 2 – UI + Playback
- File import
- Real-time or fast-preview rendering
- Knob controls

### Phase 3 – Export & Monetization
- MP3/AAC export
- Save history
- Free vs Pro presets

### Phase 4 – Enhanced Lofi
- Drum loops
- Tempo detection
- Sidechain compression

### Phase 5 – AI Upgrade (Optional)
- Style transfer models
- Cloud inference
- Lofi “style packs”

---

## 9. Quality Checklist
- No audible artifacts
- Fast export (<60s for 3-min song)
- LUFS around -14
- Sounds good on phone speakers

---

## 10. 7-Day Build Plan

**Day 1–2:** DSP prototype  
**Day 3:** Presets + tuning  
**Day 4:** Import/export  
**Day 5:** UI integration  
**Day 6:** Testing + polish  
**Day 7:** Beta release  

---

## 11. Future Features
- AI style matching
- Cloud sync
- Community presets
- Beat generator
- Loop export for creators

---

✅ *Next step:*  
Tell me **platform (iOS / Android / Web / Desktop)** and whether you want **real-time preview or render-only**, and I’ll generate a **technical architecture + sample code structure**.
