import stmpy

from gui.gui_controller import GuiController


class GuiSTM:
    """
    This class is used to create a GUI for the STM.
    # TODO: Sunde mekker en gui kontroller som kan kontrollere STM'en.
    # TODO: Så vi trenger bare logikken til STM'en.
    """

    def __init__(self):
        self.controller = GuiController()
        pass

    def send_err_msg(self, e_msg):
        # TODO: send error message to the other STM
        self.stm.send("unknown_cmd", kwargs={"feedback": e_msg})

    def new_frame(self, frame):
        self.stm.send("new frame", kwargs={"frame": frame})



gui_stm = GuiSTM()

# Transitions
# TODO: Talk to Øystein and figure out the trigger names
t0 = {"source": "initial", "target": "gallery_mode"}
t1 = {"trigger": "enter_qr_scanner", "source": "gallery_mode", "target": "qr_scanner"}
t2 = {"trigger": "enter_waiting_mode", "source": "gallery_mode", "target": "waiting_mode"}
t3 = {"trigger": "enter_video_call", "source": "waiting_mode", "target": "video_call"}
t4 = {"trigger": "enter_waiting_mode", "source": "qr_scanner", "target": "waiting_mode"}
t5 = {"trigger": "open_menu", "source": "video_call", "target": "menu_open"}
t6 = {"trigger": "close_menu", "source": "menu_open", "target": "video_call"}
t7 = {"trigger": "selected_face_filter", "source": "menu_open", "target": "video_call", "effect": "apply_face_filter"}
t8 = {"trigger": "selected_background_filter", "source": "menu_open", "target": "video_call", "effect": "apply_background_filter"}
t9 = {"trigger": "enter_gallery_mode", "source": "qr_scanner", "target": "gallery_mode"}
t10 = {"trigger": "enter_gallery_mode", "source": "waiting_mode", "target": "gallery_mode"}
t11 = {"trigger": "enter_gallery_mode", "source": "video_call", "target": "gallery_mode"}
t12 = {"trigger": "enter_qr_scanner", "source": "video_call", "target": "qr_scanner"}
t13 = {"trigger": "enter_waiting_mode", "source": "video_call", "target": "waiting_mode"}


# States
s0 = {"name": "initial"}
s1 = {"name": "gallery_mode"}
s2 = {"name": "qr_scanner"}
s3 = {"name": "waiting_mode"}
s4 = {"name": "video_call", "entry": "new_frame(*)"}
s5 = {"name": "menu_open"}

machine = stmpy.Machine(name="gui_stm", transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13], states=[s0, s1, s2, s3, s4, s5],
                        obj=gui_stm)
gui_stm.stm = machine

driver = stmpy.Driver()
driver.add_machine(machine)
driver.start()

#driver.send("start_listening", "voice_stm")
