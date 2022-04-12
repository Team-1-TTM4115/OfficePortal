import stmpy
from voice_recognition import VoiceRecognition, text_to_number
import text_to_speech

VOICE_COMMANDS = [
    {"command": "open menu", "feedback": "opening menu"},
    {"command": "close menu", "feedback": "closing menu"},
    {"command": "select menu item number", "feedback": "selecting menu item"},
]

class VoiceSTM:
    def __init__(self):
        self.vc = VoiceRecognition()

    def on_command_found(self, command, feedback):
        self.stm.send("cmd_found", kwargs={"command": command, "feedback": feedback})

    def on_command_not_found(self, e_msg):
        self.stm.send("cmd_not_found", kwargs={"e_msg": e_msg})

    def voice_cmd_listening(self):
        try:
            response = self.vc.recognize_command()
            if response["success"]:
                found = False
                for command in VOICE_COMMANDS:
                    if command["command"] in response["recording"]:
                        found = True
                        recognized_command = command["command"]
                        if command["command"] == "select menu item number":
                            item_num = text_to_number(
                                response["recording"], "select menu item number "
                            )
                            recognized_command = f"select menu item number {item_num}"
                        self.on_command_found(recognized_command, command["feedback"])
                if not found:
                    self.on_command_not_found(f"Unknown command: {response['recording']}")
            else:
                print(response["exception"])
                self.on_command_not_found("I did not quite catch that. Please try again.")
        except Exception as e:
            print(e)
            self.on_command_not_found(f"I was not able to process your command")

    def voice_cmd_feedback(self, feedback):        
        text_to_speech.speak(feedback)

    def send_command(self, command, feedback):
        # TODO: send command to the other STM
        print(f"Command used: {command}")
        self.stm.send("known_cmd_voice_feedback", kwargs={"feedback": command})

    def send_err_msg(self, e_msg):
        # TODO: send error message to the other STM
        self.stm.send("unknown_cmd_voice_feedback", kwargs={"feedback": e_msg})

voice_stm = VoiceSTM()

# Transitions
t0 = {"source": "initial", "target": "idle"}
t1 = {"trigger": "start_listening", "source": "idle", "target": "listening"}
t2 = {"trigger": "cmd_found", "source": "listening", "target": "known_cmd", "effect": "send_command(*)"}
t3 = {"trigger": "cmd_not_found", "source": "listening", "target": "unknown_cmd", "effect": "send_err_msg(*)"}
t4 = {"trigger": "known_cmd_voice_feedback", "source": "known_cmd", "target": "speaking"}
t5 = {"trigger": "unknown_cmd_voice_feedback", "source": "unknown_cmd", "target": "speaking"}
t6 = {"trigger": "done", "source": "speaking", "target": "listening"}

# States
s0 = {"name": "initial"}
s1 = {"name": "listening", "entry": "voice_cmd_listening"}
s2 = {"name": "known_cmd"}
s3 = {"name": "unknown_cmd"}
s4 = {"name": "speaking", "do": "voice_cmd_feedback(*)"}

machine =  stmpy.Machine(name="voice_stm", transitions=[t0, t1, t2, t3, t4, t5, t6], states=[s0, s1, s2, s3, s4], obj=voice_stm)
voice_stm.stm = machine

driver = stmpy.Driver()
driver.add_machine(machine)
driver.start()

driver.send("start_listening", "voice_stm")
