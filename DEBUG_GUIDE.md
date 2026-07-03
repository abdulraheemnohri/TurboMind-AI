# TurboMind AI Debug Guide

## Desktop Testing

### Install Dependencies
pip install -r requirements.txt

### Run Application
python main.py

### Test Modules
from vision.ocr import OCRProcessor
ocr = OCRProcessor()

from voice.speech_to_text import SpeechToText
stt = SpeechToText()

from voice.text_to_speech import TextToSpeech
tts = TextToSpeech()

from runtime.inference_engine import InferenceEngine
engine = InferenceEngine()

## Android Testing

### Install Buildozer
pip install buildozer

### Build APK
buildozer android debug deploy run

## Model Download

### VOSK Models
See: https://alphacephei.com/vosk/models
Download and place in assets/ directory

### AI Models
Use transformers library to download and save to models/ directory

## Common Issues

- ModuleNotFoundError: pip install missing-package
- Tesseract not installed: sudo apt install tesseract-ocr
- PyTorch CUDA: pip install torch --extra-index-url https://download.pytorch.org/whl/cu118
- Kivy display: Use Xvfb or set DISPLAY variable

## Performance Tips

- Use quantized models (4-bit, 8-bit)
- Use smaller models (TinyLlama, Phi-2)
- Use GPU if available (device=cuda or mps)
- Limit context size

## Support

- GitHub Issues: https://github.com/abdulraheemnohri/TurboMind-AI/issues
- Kivy Docs: https://kivy.org/doc/stable/
- KivyMD Docs: https://kivymd.readthedocs.io/en/latest/
