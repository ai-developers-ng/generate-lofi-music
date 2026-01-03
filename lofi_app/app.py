import sys
import tempfile
from pathlib import Path

from PySide6 import QtCore, QtMultimedia, QtWidgets

from lofi_app import dsp, presets
from lofi_app.io import load_audio, save_audio


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lofi Maker")
        self.setMinimumSize(800, 520)

        self.audio_path = None
        self.audio = None
        self.sample_rate = None
        self.processed_audio = None
        
        # Audio playback
        self.player = QtMultimedia.QMediaPlayer()
        self.audio_output = QtMultimedia.QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.temp_playback_file = None
        self.is_playing_processed = False

        # Apply dark theme
        self._apply_dark_theme()

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        layout = QtWidgets.QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QtWidgets.QLabel("🎧 Lofi Music Maker")
        header.setStyleSheet("font-size: 24px; font-weight: 700; color: #FF6B9D; padding: 10px;")
        layout.addWidget(header)

        self.file_label = QtWidgets.QLabel("No file loaded")
        self.file_label.setStyleSheet("color: #aaa; font-size: 13px;")
        layout.addWidget(self.file_label)

        file_row = QtWidgets.QHBoxLayout()
        layout.addLayout(file_row)

        load_button = QtWidgets.QPushButton("📁 Load Audio")
        load_button.setStyleSheet("""
            QPushButton {
                background-color: #4A5568;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5A6678;
            }
        """)
        load_button.clicked.connect(self.load_audio)
        file_row.addWidget(load_button)

        file_row.addSpacing(10)

        preset_label = QtWidgets.QLabel("Preset:")
        preset_label.setStyleSheet("color: #ccc; font-size: 13px;")
        file_row.addWidget(preset_label)

        self.preset_box = QtWidgets.QComboBox()
        self.preset_box.setStyleSheet("""
            QComboBox {
                background-color: #2D3748;
                color: white;
                border: 1px solid #4A5568;
                padding: 8px;
                border-radius: 5px;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 1px solid #667EEA;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2D3748;
                color: white;
                selection-background-color: #667EEA;
            }
        """)
        self.preset_box.addItems(list(presets.PRESETS.keys()))
        self.preset_box.currentTextChanged.connect(self.apply_preset)
        file_row.addWidget(self.preset_box)

        file_row.addStretch()

        self.controls = {}
        controls_layout = QtWidgets.QGridLayout()
        controls_layout.setSpacing(15)
        layout.addLayout(controls_layout)

        # Color-coded sliders with emojis
        self._add_slider(controls_layout, "🔥 Warmth", "saturation", 0.0, 1.0, 0.6, 0, 0, "#FF6B6B")
        self._add_slider(controls_layout, "🌊 Wobble", "wow_flutter", 0.0, 1.0, 0.25, 0, 1, "#4ECDC4")
        self._add_slider(controls_layout, "📻 Noise", "noise", 0.0, 0.5, 0.12, 1, 0, "#95E1D3")
        self._add_slider(controls_layout, "🏠 Room", "reverb", 0.0, 0.8, 0.2, 1, 1, "#A8E6CF")
        self._add_slider(controls_layout, "⏱️ Tempo", "time_stretch", 0.8, 1.05, 0.92, 2, 0, "#FFD93D")
        self._add_slider(controls_layout, "🎵 Pitch", "pitch_shift", -4.0, 2.0, -2.0, 2, 1, "#FFA07A")

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #4A5568;
                border-radius: 5px;
                text-align: center;
                background-color: #2D3748;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #667EEA;
                border-radius: 4px;
            }
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Audio playback controls
        playback_layout = QtWidgets.QHBoxLayout()
        playback_layout.setSpacing(10)
        layout.addLayout(playback_layout)

        playback_label = QtWidgets.QLabel("Preview:")
        playback_label.setStyleSheet("color: #ccc; font-size: 13px;")
        playback_layout.addWidget(playback_label)

        self.play_original_btn = QtWidgets.QPushButton("▶️ Original")
        self.play_original_btn.setStyleSheet("""
            QPushButton {
                background-color: #2D3748;
                color: white;
                border: 1px solid #4A5568;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3D4758;
            }
            QPushButton:disabled {
                background-color: #1A202C;
                color: #4A5568;
            }
        """)
        self.play_original_btn.setEnabled(False)
        self.play_original_btn.clicked.connect(self.play_original)
        playback_layout.addWidget(self.play_original_btn)

        self.play_processed_btn = QtWidgets.QPushButton("▶️ Lofi Preview")
        self.play_processed_btn.setStyleSheet("""
            QPushButton {
                background-color: #2D3748;
                color: white;
                border: 1px solid #667EEA;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3D4758;
                border-color: #5568D3;
            }
            QPushButton:disabled {
                background-color: #1A202C;
                color: #4A5568;
                border-color: #4A5568;
            }
        """)
        self.play_processed_btn.setEnabled(False)
        self.play_processed_btn.clicked.connect(self.play_processed)
        playback_layout.addWidget(self.play_processed_btn)

        self.stop_btn = QtWidgets.QPushButton("⏹️ Stop")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #2D3748;
                color: white;
                border: 1px solid #4A5568;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3D4758;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_playback)
        playback_layout.addWidget(self.stop_btn)

        playback_layout.addStretch()

        buttons = QtWidgets.QHBoxLayout()
        layout.addLayout(buttons)

        reset_button = QtWidgets.QPushButton("🔄 Reset to Preset")
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #4A5568;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #5A6678;
            }
        """)
        reset_button.clicked.connect(self.reset_to_preset)
        buttons.addWidget(reset_button)

        buttons.addStretch()

        render_button = QtWidgets.QPushButton("✨ Render Lofi")
        render_button.setStyleSheet("""
            QPushButton {
                background-color: #667EEA;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #5568D3;
            }
        """)
        render_button.clicked.connect(self.render_audio)
        buttons.addWidget(render_button)

        self.status = QtWidgets.QLabel("")
        self.status.setStyleSheet("color: #aaa; font-size: 12px;")
        layout.addWidget(self.status)

        self.apply_preset(self.preset_box.currentText())

    def _apply_dark_theme(self):
        """Apply dark theme to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1A202C;
            }
            QWidget {
                background-color: #1A202C;
                color: #E2E8F0;
            }
            QLabel {
                color: #E2E8F0;
            }
        """)

    def _add_slider(self, layout, label, key, min_val, max_val, default, row, col, color="#667EEA"):
        container = QtWidgets.QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: #2D3748;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        vbox = QtWidgets.QVBoxLayout(container)
        vbox.setContentsMargins(10, 10, 10, 10)

        title_layout = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel(label)
        title.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: 600;")
        value_label = QtWidgets.QLabel(f"{default:.2f}")
        value_label.setStyleSheet("color: #CBD5E0; font-size: 11px; font-weight: 500;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(value_label)
        
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: #1A202C;
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {color};
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {color};
                transform: scale(1.1);
            }}
            QSlider::sub-page:horizontal {{
                background: {color};
                border-radius: 3px;
            }}
        """)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(int((default - min_val) / (max_val - min_val) * 100))
        
        # Connect slider to update value label
        slider.valueChanged.connect(
            lambda: value_label.setText(f"{self._slider_value(key):.2f}")
        )

        vbox.addLayout(title_layout)
        vbox.addWidget(slider)
        layout.addWidget(container, row, col)

        self.controls[key] = {
            "slider": slider,
            "min": min_val,
            "max": max_val,
            "label": title,
            "value_label": value_label,
            "default": default,
        }

    def _slider_value(self, key):
        config = self.controls[key]
        slider = config["slider"]
        return config["min"] + (config["max"] - config["min"]) * (slider.value() / 100)

    def apply_preset(self, name):
        preset = presets.PRESETS.get(name, {})
        for key, config in self.controls.items():
            if key not in preset:
                continue
            value = preset[key]
            ratio = (value - config["min"]) / (config["max"] - config["min"])
            config["slider"].setValue(int(ratio * 100))

    def reset_to_preset(self):
        """Reset all controls to current preset values"""
        self.apply_preset(self.preset_box.currentText())
        self.status.setText("Reset to preset values.")

    def load_audio(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Load Audio",
            str(Path.home()),
            "Audio Files (*.wav *.flac *.mp3 *.ogg)",
        )
        if not path:
            return
        try:
            audio, sr = load_audio(path)
        except Exception as exc:
            self.status.setText(f"Failed to load audio: {exc}")
            return
        self.audio_path = Path(path)
        self.audio = audio.astype("float32")
        self.sample_rate = sr
        self.file_label.setText(f"Loaded: {self.audio_path.name}")
        self.status.setText("Ready.")
        self.play_original_btn.setEnabled(True)

    def play_original(self):
        """Play the original audio file"""
        if self.audio_path is None:
            return
        self.stop_playback()
        self.player.setSource(QtCore.QUrl.fromLocalFile(str(self.audio_path)))
        self.player.play()
        self.is_playing_processed = False
        self.status.setText("▶️ Playing original...")

    def play_processed(self):
        """Play processed audio with current settings"""
        if self.audio is None:
            return
        
        self.stop_playback()
        self.status.setText("Processing preview...")
        QtWidgets.QApplication.processEvents()
        
        # Apply current settings
        params = {key: self._slider_value(key) for key in self.controls}
        processed = dsp.apply_pipeline(self.audio, self.sample_rate, params)
        
        # Save to temp file
        if self.temp_playback_file:
            try:
                Path(self.temp_playback_file).unlink()
            except:
                pass
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self.temp_playback_file = temp_file.name
        temp_file.close()
        
        save_audio(self.temp_playback_file, processed, self.sample_rate)
        
        # Play temp file
        self.player.setSource(QtCore.QUrl.fromLocalFile(self.temp_playback_file))
        self.player.play()
        self.is_playing_processed = True
        self.status.setText("▶️ Playing lofi preview...")
        self.play_processed_btn.setEnabled(True)

    def stop_playback(self):
        """Stop audio playback"""
        self.player.stop()
        if self.audio_path:
            self.status.setText("Playback stopped.")
        else:
            self.status.setText("")

    def render_audio(self):
        if self.audio is None:
            self.status.setText("Load an audio file first.")
            return

        params = {key: self._slider_value(key) for key in self.controls}
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status.setText("Processing audio...")
        QtWidgets.QApplication.processEvents()

        # Simulate progress (in real scenario, you'd update during processing)
        self.progress_bar.setValue(30)
        QtWidgets.QApplication.processEvents()

        processed = dsp.apply_pipeline(self.audio, self.sample_rate, params)
        self.processed_audio = processed

        self.progress_bar.setValue(70)
        QtWidgets.QApplication.processEvents()

        output_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Lofi Audio",
            str(self.audio_path.with_suffix(".lofi.wav")),
            "Audio Files (*.wav *.mp3)",
        )
        if not output_path:
            self.status.setText("Export canceled.")
            self.progress_bar.setVisible(False)
            return
        
        self.progress_bar.setValue(90)
        QtWidgets.QApplication.processEvents()
        
        # Save based on extension
        if output_path.endswith('.mp3'):
            self._save_as_mp3(output_path, processed)
        else:
            save_audio(output_path, processed, self.sample_rate)
        
        self.progress_bar.setValue(100)
        self.status.setText(f"✅ Exported to {Path(output_path).name}")
        
        # Hide progress bar after a moment
        QtCore.QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))

    def _save_as_mp3(self, path, audio):
        """Save audio as MP3 format"""
        try:
            import soundfile as sf
            import subprocess
            import tempfile
            
            # Save as WAV first
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name
                sf.write(tmp_path, audio, self.sample_rate)
            
            # Convert to MP3 using ffmpeg
            subprocess.run([
                'ffmpeg', '-i', tmp_path, '-codec:a', 'libmp3lame',
                '-qscale:a', '2', path, '-y'
            ], check=True, capture_output=True)
            
            # Clean up temp file
            Path(tmp_path).unlink()
        except Exception as e:
            # Fallback to WAV if MP3 fails
            self.status.setText(f"MP3 export failed, saving as WAV: {e}")
            save_audio(path.replace('.mp3', '.wav'), audio, self.sample_rate)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
