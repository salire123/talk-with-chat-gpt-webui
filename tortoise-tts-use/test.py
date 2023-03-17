
import os
import torchaudio

from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_voice


# This will download all the models used by Tortoise from the HF hub.
tts = TextToSpeech()

# This is the text that will be spoken.
text = "you are gay"

# Pick a "preset mode" to determine quality. Options: {"ultra_fast", "fast" (default), "standard", "high_quality"}. See docs in api.py
preset = "fast"

# Pick one of the voices from the output above
voice = "test"

# Load the voice.
voice_samples, conditioning_latents = load_voice(voice)
# Generate the audio.
gen = tts.tts_with_preset(text, voice_samples=voice_samples, conditioning_latents=conditioning_latents, preset=preset)

# Save the audio to a file.
torchaudio.save(os.path.join(f'output/test.wav'), gen.squeeze(0).cpu(), 24000)

