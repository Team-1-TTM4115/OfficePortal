import speech_recognition as sr
import re

TEXT_TO_NUMBER = {
    '0': 0,
    'zero': 0,
    '1': 1,
    'one': 1,
    '2': 2,
    'two': 2,
    'to': 2,
    'too': 2,
    '3': 3,
    'three': 3,
    'tree': 3,
    '4': 4,
    'four': 4,
    'for': 4,
    '5': 5,
    'five': 5,
}

def text_to_number(text, keyword):
    print(text)
    print(keyword)
    text_num = get_number_from_text(text, keyword)
    return TEXT_TO_NUMBER[text_num]


def get_number_from_text(text, keyword):
    return re.findall(r'%s(.+)' % keyword, text)[0].strip()

class VoiceRecognition:
    def __init__(self):
        self.r = sr.Recognizer()
        self.mic = sr.Microphone()

    def recognize_command(self):
        response = {}
        try:
            with self.mic as source:
                self.r.adjust_for_ambient_noise(source)
                audio = self.r.listen(source, phrase_time_limit=3)
            command = self.r.recognize_google(audio)
            response["recording"] = command
            response["success"] = True
        except sr.UnknownValueError:
            response[
                "exception"
            ] = "Google Speech Recognition could not understand audio"
            response["success"] = False

        except sr.RequestError as e:
            response[
                "exception"
            ] = f"Could not request results from Google Speech Recognition service; {e}"
            response["success"] = False
        return response