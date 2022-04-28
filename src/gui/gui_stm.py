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

    def new_frame(self, frame=None):
        pass

    def enter_qr_scanner(self):
        self.gui_controller.enter_qr_scanner()

    def leave_qr_scanner(self):
        self.gui_controller.leave_qr_scanner()

    def enter_gallery_mode(self):
        self.gui_controller.enter_gallery_mode()

    def leave_gallery_mode(self):
        self.gui_controller.leave_gallery_mode()

    def enter_waiting_mode(self):
        self.gui_controller.enter_waiting_mode()

    def leave_waiting_screen(self):
        self.gui_controller.leave_waiting_screen()

    def enter_video_call(self):
        self.gui_controller.enter_video_call()

    def leave_video_call(self):
        self.gui_controller.leave_video_call()

    def show_filter_menu(self):
        self.gui_controller.show_filter_menu()

    def close_filter_menu(self):
        self.gui_controller.close_filter_menu()

    def start(self):
        self.gui_controller.start()
