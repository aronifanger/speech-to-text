import speech_recognition  as sr

DEV_INDEX=2

def recognize_from_mic():
    r = sr.Recognizer()
    with sr.Microphone(device_index=DEV_INDEX) as source:
        r.adjust_for_ambient_noise(source)
        print("Say something...")
        audio = r.listen(source)
        try:
            print("You have said: \n" + r.recognize_google(audio, language='pt-BR'))
        except Exception as e:
            print(e)
    return None

def recognize_from_audio(file_path):
    r = sr.Recognizer()
    with sr.WavFile(file_path) as source:
        audio = r.record(source)
    return r.recognize_google(audio, language='pt-BR')
