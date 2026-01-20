import tempfile
import gradio as gr
from src.pipeline import Pipeline

pipeline = None

def run_generator(story_title, story_text, narrator_gender, narrator_voice, avatar):
    global pipeline
    tmpdir = tempfile.mkdtemp()
    if pipeline is None or pipeline.tts.gender != narrator_gender or pipeline.tts.voice != narrator_voice:
        pipeline = Pipeline(narrator_gender=narrator_gender, narrator_voice=narrator_voice, avatar_path=avatar, results_dir=tmpdir)
    
    outputs = pipeline.generate_assets(story_title, story_text)

    return outputs["title_audio"], outputs["voice_audio"], outputs["subtitles"], outputs["frame_image"]

with gr.Blocks() as demo:
    gr.Markdown("# Reddit Stories TikTok Generator")
    gr.Markdown(
        "Generate TikTok-ready assets (audio + subtitles). "
        "**CapCut automation is available in local mode only.**"
    )

    with gr.Row():
        title = gr.Textbox(label="Story title")
        gender = gr.Radio(["f", "m"], label="Narrator gender", value="f")

    voice = gr.Textbox(label="Narrator voice", value="heart")
    story = gr.Textbox(lines=8, label="Story text")
    gr.Markdown("Check available voices [here](https://huggingface.co/hexgrad/Kokoro-82M/tree/main/voices).")

    avatar = gr.Image(type="filepath", label="Avatar image")

    generate = gr.Button("Generate assets")

    title_audio = gr.Audio(label="Title narration")
    voice_audio = gr.Audio(label="Story narration")
    subtitles = gr.File(label="Subtitles (.srt)")
    frame = gr.Image(label="Reddit frame image")

    generate.click(
        run_generator,
        inputs=[title, story, gender, voice, avatar],
        outputs=[title_audio, voice_audio, subtitles, frame]
    )

demo.launch(server_name="0.0.0.0", server_port=7860)
