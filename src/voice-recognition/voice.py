import speech_recognition as sr
from word2number import w2n
import re


def find_number(text, c):
    return re.findall(f"{c}(.+)", text)


class VoiceCommand:
    def __init__(self, commands):
        self.r = sr.Recognizer()
        self.mic = sr.Microphone()
        self.commands = commands

    def recognize_commands(self):
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


def open_menu(args=None):
    print("Opened Menu")


def close_menu(args=None):
    print("Closed Menu")


def select_menu_item(args=None):
    print(f"Selected Menu Item {args}")


def unknown_command(args=None):
    print("Unknown Command")


def listen_for_voice_commands(cmds):
    vc = VoiceCommand(cmds)
    while True:
        response = vc.recognize_commands()
        unknown_cmd = True
        if response["success"]:
            for command in cmds:
                if command["command"] in response["recording"]:
                    unknown_cmd = False
                    args = None
                    if command["command"] == "select menu item":
                        selected_item = find_number(
                            response["recording"], "select menu item"
                        )
                        if len(selected_item) > 0:
                            args = w2n.word_to_num(selected_item[0])
                    command["result"](args)
            # if unknown_cmd:
            #    unknown_command()
        else:
            print(response["exception"])


if __name__ == "__main__":
    commands = [
        {"command": "open menu", "result": open_menu},
        {"command": "close menu", "result": close_menu},
        {"command": "select menu item", "result": select_menu_item},
    ]
    listen_for_voice_commands(commands)
