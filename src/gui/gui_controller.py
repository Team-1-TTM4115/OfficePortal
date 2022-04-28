import stmpy

from gui.main_screen import Screen
from gui.gui_stm import GuiSTM


class GuiController:
    def __init__(self, cap, name):
        self.office_name = name
        self.cap = cap
        self.screen = Screen(self.cap, self.office_name)
        self.stm = None
        self.stm_driver = None

    def enter_qr_scanner(self):
        self.screen.create_qr_page()
        self.screen.show_frame('qr_frame')

    def leave_qr_scanner(self):
        self.screen.destroy_qr_page()

    def enter_gallery_mode(self):
        self.screen.show_frame('start_frame')

    def leave_gallery_mode(self):
        pass

    def enter_waiting_mode(self):
        self.screen.create_waiting_page()

    def leave_waiting_screen(self):
        self.screen.destroy_waiting_page()

    def enter_video_call(self):
        self.screen.create_video_page()

    def leave_video_call(self):
        pass

    def show_filter_menu(self):
        self.screen.show_filter()

    def close_filter_menu(self):
        self.screen.hide_filter()

    def start(self):
        self.screen.run()

    def initialize_stm(self):
        gui_stm = GuiSTM(self)

        # Transitions
        t0 = {"source": "initial", "target": "gallery_mode"}
        t1 = {"trigger": "enter_qr_scanner", "source": "gallery_mode", "target": "qr_scanner",
              "effect": "enter_qr_scanner()"}
        t2 = {"trigger": "enter_waiting_mode", "source": "gallery_mode", "target": "waiting_mode",
              "effect": "enter_waiting_mode()"}
        t3 = {"trigger": "enter_video_call", "source": "waiting_mode", "target": "video_call",
              "effect": "enter_video_call()"}
        t4 = {"trigger": "enter_waiting_mode", "source": "qr_scanner", "target": "waiting_mode",
              "effect": "enter_waiting_mode()"}
        t5 = {"trigger": "open_menu", "source": "video_call", "target": "menu_open", "effect": "show_filter_menu()"}
        t6 = {"trigger": "close_menu", "source": "menu_open", "target": "video_call", "effect": "close_filter_menu()"}
        t7 = {"trigger": "selected_face_filter", "source": "menu_open", "target": "video_call",
              "effect": "apply_face_filter()"}
        t8 = {"trigger": "selected_background_filter", "source": "menu_open", "target": "video_call",
              "effect": "apply_background_filter()"}
        t9 = {"trigger": "enter_gallery_mode", "source": "qr_scanner", "target": "gallery_mode",
              "effect": "enter_gallery_mode()"}
        t10 = {"trigger": "enter_gallery_mode", "source": "waiting_mode", "target": "gallery_mode",
               "effect": "enter_gallery_mode()"}
        t11 = {"trigger": "enter_gallery_mode", "source": "video_call", "target": "gallery_mode",
               "effect": "enter_gallery_mode()"}
        t12 = {"trigger": "enter_qr_scanner", "source": "video_call", "target": "qr_scanner",
               "effect": "enter_qr_scanner()"}
        t13 = {"trigger": "enter_waiting_mode", "source": "video_call", "target": "waiting_mode",
               "effect": "enter_waiting_mode()"}
        t14 = {"trigger": "enter_qr_scanner", "source": "waiting_mode", "target": "qr_scanner",
               "effect": "enter_qr_scanner()"}

        # States
        s0 = {"name": "initial"}
        s1 = {"name": "gallery_mode"}
        s2 = {"name": "qr_scanner"}
        s3 = {"name": "waiting_mode"}
        s4 = {"name": "video_call", "entry": "new_frame(*)"}
        s5 = {"name": "menu_open"}

        machine = stmpy.Machine(name="gui_stm",
                                transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14],
                                states=[s0, s1, s2, s3, s4, s5], obj=gui_stm)

        gui_stm.stm = machine

        self.stm = machine
