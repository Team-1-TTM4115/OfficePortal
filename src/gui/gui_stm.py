import stmpy


class GuiSTM:
    """
    This class is used to create a GUI for the STM.
    # TODO: Sunde mekker en gui kontroller som kan kontrollere STM'en.
    # TODO: Så vi trenger bare logikken til STM'en.
    """

    def __init__(self):
        pass

    def send_err_msg(self, e_msg):
        # TODO: send error message to the other STM
        self.stm.send("unknown_cmd", kwargs={"feedback": e_msg})


gui_stm = GuiSTM()

# Transitions
# TODO: Talk to Øystein and figure out the trigger names
t0 = {"source": "initial", "target": "gallery"}
t1 = {"trigger": "enter_qr_scanner", "source": "gallery", "target": "qr_scanner"}
t2 = {"trigger": "enter_waiting_mode", "source": "gallery", "target": "waiting_mode"}
t3 = {"trigger": "enter_video_call", "source": "waiting_mode", "target": "video_call"}
t4 = {"trigger": "enter_waiting_mode", "source": "known_cmd", "target": "speaking"}
t5 = {"trigger": "open_menu", "source": "video_call", "target": "menu_open"}
t6 = {"trigger": "close_menu", "source": "menu_open", "target": "video_call"}

# States
s0 = {"name": "initial"}
s1 = {"name": "gallery", "entry": "voice_cmd_listening"}
s2 = {"name": "qr_scanner"}
s3 = {"name": "waiting_mode"}
s4 = {"name": "video_call"}
s5 = {"name": "menu_open"}

machine = stmpy.Machine(name="gui_stm", transitions=[t0, t1, t2, t3, t4, t5, t6], states=[s0, s1, s2, s3, s4, s5],
                        obj=gui_stm)
gui_stm.stm = machine

driver = stmpy.Driver()
driver.add_machine(machine)
driver.start()

driver.send("start_listening", "voice_stm")
