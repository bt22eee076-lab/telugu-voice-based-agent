from gtts import gTTS
import os

# Telugu text
text = "నేను మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను"

# Convert text to Telugu speech
tts = gTTS(text=text, lang="te")

# Save audio
filename = "response.mp3"
tts.save(filename)

# Play using Windows default player
os.startfile(filename)
