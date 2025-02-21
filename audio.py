from gtts import gTTS
from pydub import AudioSegment
import tempfile

def gtpodcast_script_to_audio(script: str) -> str:
    if not script.strip():
        raise ValueError("No script provided for audio conversion.")

    # Generate TTS audio
    tts = gTTS(text=script, lang="en", tld='ca')  # British English accent
    temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    tts.save(temp_audio_path)

    # Load the generated audio and lower the pitch
    audio = AudioSegment.from_file(temp_audio_path)
    lowered_pitch_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * 0.95)})
    lowered_pitch_audio = lowered_pitch_audio.set_frame_rate(audio.frame_rate)

    # Export the modified audio
    podcast_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    lowered_pitch_audio.export(podcast_path, format="mp3")

    return podcast_path