import stmpy

from .voice_recognition import VoiceRecognition, text_to_number

VOICE_COMMANDS = [
    {"command": ["open menu", "change_session_view"]},
    {"command": ["close menu", "change_session_view"]},
    {"command": ["remove background", "change_session_view"]},
    {"command": ["remove face", "change_session_view"]},
    {"command": ["background number", "choose_filter"]},
    {"command": ["face number", "choose_filter"]},
    {"command": ["change connection", "change_connection"]},
]

class VoiceCmdSTM:
    def __init__(self, vc_component):
        self.vc_component = vc_component

    def on_command_found(self, command, trigger):
        self.vc_component.on_command_found(command, trigger)

    def on_command_not_found(self, e_msg):
        self.vc_component.on_command_not_found(e_msg)

    def voice_cmd_listening(self):
        self.vc_component.voice_cmd_listening()

    def send_command(self, command, trigger):
        self.vc_component.send_command(command, trigger)

    def send_err_msg(self, e_msg):
        self.vc_component.send_err_msg(e_msg)

class VoiceCommandComponent:
    def __init__(self):
        self.stm = None
        self.stm_driver = None
        self.vc = VoiceRecognition()

    def initialize_stm(self):
        voice_cmd_stm = VoiceCmdSTM(self)

        # Transitions
        t0 = {"source": "initial", "target": "idle"}
        t1 = {"trigger": "start_listening", "source": "idle", "target": "listening"}
        t2 = {"trigger": "stop_listening", "source": "listening", "target": "idle"}
        t3 = {"trigger": "cmd_found", "source": "listening", "target": "known_cmd", "effect": "send_command(*)"}
        t4 = {"trigger": "cmd_not_found", "source": "listening", "target": "unknown_cmd", "effect": "send_err_msg(*)"}
        t5 = {"trigger": "continue_listening", "source": "known_cmd", "target": "listening"}
        t6 = {"trigger": "continue_listening", "source": "unknown_cmd", "target": "listening"}

        # States
        s0 = {"name": "initial"}
        s1 = {"name": "listening", "entry": "voice_cmd_listening()"}
        s2 = {"name": "known_cmd", "stop_listening": "defer"}
        s3 = {"name": "unknown_cmd", "stop_listening": "defer"}

        machine =  stmpy.Machine(name="voice_stm", transitions=[t0, t1, t2, t3, t4, t5, t6], states=[s0, s1, s2, s3], obj=voice_cmd_stm)
        voice_cmd_stm.stm = machine

        self.stm = machine

    def on_command_found(self, command, trigger):
        self.stm_driver.send("cmd_found", "voice_stm", kwargs={"command": command, "trigger": trigger})

    def on_command_not_found(self, e_msg):
        self.stm_driver.send("cmd_not_found", "voice_stm", kwargs={"e_msg": e_msg})

    def voice_cmd_listening(self):
        try:
            response = self.vc.recognize_command()
            if response["success"]:
                found = False
                for command in VOICE_COMMANDS:
                    if command["command"][0] in response["recording"].lower():
                        found = True
                        recognized_command = command["command"][0]
                        if recognized_command == "background number":
                            item_num = text_to_number(
                                response["recording"], "background number"
                            )
                            recognized_command = [recognized_command, item_num]
                        elif recognized_command == "face number":
                            item_num = text_to_number(
                                response["recording"], "face number"
                            )
                            recognized_command = [recognized_command, item_num]
                        self.on_command_found(recognized_command, command["command"][1])
                if not found:
                    self.on_command_not_found(f"Unknown command: {response['recording']}")
            else:
                self.on_command_not_found("I did not quite catch that. Please try again.")
        except Exception as e:
            self.on_command_not_found(f"I was not able to process your command: {e}")

    def send_command(self, command, trigger):
        # TODO: send command to the other STM
        print(f"Command used: {command}")
        print(f"Sending trigger: {trigger} to STM with command {command}")
        self.stm_driver.send(trigger, "Controller", kwargs={"command": command})
        self.stm_driver.send("continue_listening", "voice_stm")

    def send_err_msg(self, e_msg):
        # TODO: send error message to the other STM
        print(e_msg)
        self.stm_driver.send("continue_listening", "voice_stm")