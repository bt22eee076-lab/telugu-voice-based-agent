import speech_recognition as sr

recognizer=sr.Recognizer()
with sr.Microphone() as source:
      print("🎙️ తెలుగులో మాట్లాడండి...")
      recognizer.adjust_for_ambient_noise(source)
      audio=recognizer.listen(source)

try:
    text = recognizer.recognize_google(audio, language="te-IN") # type: ignore
    print("📝 మీరు చెప్పింది:")
    print(text)

except sr.UnknownValueError:
    print("❌ మీ మాటలు అర్థం కాలేదు. మళ్లీ ప్రయత్నించండి.")

except sr.RequestError as e:
    print("❌ Speech service error:", e)

            
