from src.gui.main_screen import Screen


class GuiController:
    def __init__(self):
        self.screen = Screen()

    def enter_qr_scanner(self):
        self.screen.create_qr_page()
        self.screen.show_frame('qr_frame')

    def enter_gallery_mode(self):
        pass

    def enter_waiting_mode(self):
        # TODO: Needs component from Ingebret
        pass

    def enter_video_call(self):
        # TODO: Needs component from Ingebret
        pass

    def select_face_filter(self):
        # TODO: Needs component from Emilie
        pass

    def apply_face_filter(self):
        # TODO: Needs component from Emilie
        pass

    def select_background_filter(self):
        # TODO: Needs component from Emilie
        pass

    def apply_background_filter(self):
        # TODO: Needs component from Emilie
        pass

    def start(self):
        self.screen.run()


if __name__ == "__main__":
    gui = GuiController()
    gui.start()
