import os
from src.tts import TTS
from src.subtitles import Subtitles
from src.reddit_frame_image import RedditFrameImage

def generate_assets(story_title, story_text, narrator_gender, narrator_voice, avatar_path, results_dir="results"):
    os.makedirs(results_dir, exist_ok=True)

    subtitles_generator = Subtitles(result_folder=results_dir, device="cpu", compute_type="int8")
    reddit_frame_image_generator = RedditFrameImage(postfully_url="https://postfully.app/tools/reddit-post-template/", avatar_path=avatar_path, result_folder=results_dir)
    tts = TTS(result_folder=results_dir, gender=narrator_gender, voice=narrator_voice)

    # TTS
    title_wav, _ = tts.synthesize(story_title, name="title")
    title_wav, _ = tts.trim_silence(title_wav)
    title_mp3 = tts.convert_wav_to_mp3(title_wav)

    voice_wav, voice_dur = tts.synthesize(story_text, name="voice")
    voice_wav, voice_dur = tts.trim_silence(voice_wav)
    voice_mp3 = tts.convert_wav_to_mp3(voice_wav)

    # Subtitles
    subs = subtitles_generator.transcribe(voice_wav)
    srt_path = os.path.join(results_dir, "subtitles.srt")
    subtitles_generator.generate_srt(subs, srt_path, words_per_subtitle=1, audio_duration=voice_dur)

    # Reddit Frame Image
    if avatar_path is not None:
        frame_image = None
    else:
        try:
            frame_image = reddit_frame_image_generator.download_frame_image(text=story_title)
        except Exception:
            frame_image = None

    return {
        "title_audio": title_mp3,
        "voice_audio": voice_mp3,
        "subtitles": srt_path,
        "frame_image": frame_image
    }
