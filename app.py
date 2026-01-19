import tempfile
import gradio as gr
from src.pipeline import generate_assets

def run_generator(story_title, story_text, narrator_gender, narrator_voice, avatar):
    tmpdir = tempfile.mkdtemp()

    outputs = generate_assets(story_title, story_text, narrator_gender, narrator_voice, avatar, results_dir=tmpdir)

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

demo.launch()
