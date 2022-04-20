from src.gui.main_screen import Screen


class GuiController:
    def __init__(self):
        self.screen = Screen()

    def enter_qr_scanner(self):
        self.screen.create_qr_page()
        self.screen.show_frame('qr_frame')

    def leave_qr_scanner(self):
        self.screen.destroy_qr_page()

    def enter_gallery_mode(self):
        self.screen.show_frame('start_frame')
        pass

    def leave_gallery_mode(self):
        pass

    def enter_waiting_mode(self):
        self.screen.create_waiting_page()
        pass

    def leave_waiting_screen(self):
        self.screen.destroy_waiting_page()

    def enter_video_call(self):
        self.screen.create_video_page()
        pass

    def leave_video_call(self):
        # TODO: Check what we need to do.
        pass

    def show_filter_menu(self):
        pass

    def close_filter_menu(self):
        pass

    def start(self):
        self.screen.run()


if __name__ == "__main__":
    gui = GuiController()
    gui.start()
