from gui.main_screen import Screen


class GuiSTM:
    """
    This class is used to create a GUI for the STM.
    """

    def __init__(self, controller):
        self.screen = Screen(controller.cap, controller.office_name)
        self.gui_controller = controller

    def send_err_msg(self, e_msg):
        self.gui_controller.send_err_msg(e_msg)

    def enter_qr_scanner(self):
        self.gui_controller.enter_qr_scanner()

    def enter_gallery_mode(self):
        self.gui_controller.enter_gallery_mode()

    def enter_waiting_mode(self):
        self.gui_controller.enter_waiting_mode()

    def enter_video_call(self):
        self.gui_controller.enter_video_call()

    def show_filter_menu(self):
        self.gui_controller.show_filter_menu()

    def close_filter_menu(self):
        self.gui_controller.close_filter_menu()

    def start(self):
        self.gui_controller.start()
