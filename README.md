# Reddit Stories TikTok Generator

A Python application that generates TikTok-style videos from Reddit stories with text-to-speech narration and synchronized subtitles.

## Features

- 🎙️ **Text-to-Speech**: Generate natural-sounding speech using the Kokoro-82M model
- 🎬 **Subtitle Generation**: Create SRT subtitle files with WhisperX automatic speech recognition
- ✂️ **Audio Trimming**: Automatically remove silence from the beginning and end of audio
- 🔄 **No Gaps**: Subtitles stay on screen continuously with no blank moments
- ⚙️ **Engaging**: Optimized for TikTok viewing with attention-grabbing images and sounds

## Requirements

- Python 3.8+
- FFmpeg (for audio processing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/GiuseppeRainone07/reddit-stories-tiktok-generator.git
cd reddit-stories-tiktok-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

source venv/bin/activate # Mac/Linux
# or venv\Scripts\activate # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **Mac**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

5. Clone VectCut API and run it locally:
```bash
mkdir external
cd external
git clone https://github.com/sun-guannan/VectCutAPI.git
cd VectCutAPI
python -m venv venv-capcut
source venv-capcut/bin/activate  # Linux/macOS
# or venv-capcut\Scripts\activate  # Windows
pip install -r requirements.txt
cp config.json.example config.json
python capcut_server.py # default port: 9001
```

6. Create a .env file and edit the environment variables as needed:
```bash
cp .env.example .env
```

## Usage

You need to provide:
1. A background video file (`BG_VIDEO` in .env)
2. An avatar image file, used as a profile picture for the custom Reddit frame image (`AVATAR_PATH` in .env)
3. Either a Reddit story link (`USE_LINKS=true` and `STORY_LINK` in .env) or a text file containing the story (`USE_LINKS=false` and `STORY_FILE` in .env)
4. (Optional) Customize narrator voice by setting `NARRATOR_GENDER` and `NARRATOR_VOICE` in .env. Check out all Kokoro voices [here](https://huggingface.co/hexgrad/Kokoro-82M/tree/main/voices)

Run the main script:
```bash
python src/main.py
```

If you want to check if stories are being fetched correctly, you can run the test mode:

```bash
python src/main.py test
```

This will print the fetched story text and exit without generating videos.

## How It Works

1. **Text-to-Speech**: Your story text is converted to audio using Kokoro-82M TTS model
2. **Audio Processing**: Silence is trimmed from the beginning and end of the audio
3. **Transcription**: WhisperX transcribes the audio to get rough timestamps
4. **Alignment**: The alignment model refines timestamps to word-level precision
5. **SRT Generation**: Timestamps are formatted into SRT subtitle format with no gaps between subtitles

## Technical Details

### Forced Alignment

Forced alignment is the process of automatically aligning spoken audio with its corresponding text transcript. This application uses:

- **WhisperX Base Model**: For initial transcription and rough timestamps
- **Alignment Model**: For word-level precision (accurate to ~10ms)
- **CPU Compute**: Runs on CPU with int8 quantization for efficiency

### Subtitle Format

The generated SRT files follow this format:

```
1
00:00:00,031 --> 00:00:00,592
Turns out I

2
00:00:00,592 --> 00:00:01,252
was the only

3
00:00:01,252 --> 00:00:01,994
one who didn't know.
```

## Troubleshooting

### PyTorch Compatibility Issues

If you see errors about `weights_only` or `omegaconf`, the code includes a monkey-patch to handle this automatically. No action needed.

### Slow Processing

- Use smaller models: Change `"base"` to `"tiny"` in the code
- Reduce batch size: Lower the `batch_size` parameter
- The first run is slower due to model downloads

### Inaccurate Timestamps

- Ensure your TTS audio is clear and matches the input text
- Try adjusting the `top_db` parameter for silence trimming
- Check that the language is set correctly (`language="en"`)

### Missing Audio Files

Make sure FFmpeg is installed and accessible from your PATH.

## Dependencies

Key dependencies (see `requirements.txt` for complete list):

- `whisperx==3.7.4` - Forced alignment and transcription
- `torch==2.8.0` - PyTorch for model inference
- `kokoro==0.9.4` - TTS model
- `soundfile==0.13.1` - Audio file I/O
- `numpy` - Numerical operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [WhisperX](https://github.com/m-bain/whisperX) for forced alignment
- [Kokoro](https://github.com/hexgrad/kokoro) for TTS
- OpenAI Whisper for the base transcription model
- [VectCutAPI](https://github.com/sun-guannan/VectCutAPI) for video editing

## Note

This project is for educational and fun purposes only. Don't take it too seriously!
