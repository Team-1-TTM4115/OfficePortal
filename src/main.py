from gui.camera import Camera
import cv2
import stmpy
from stream_video import StreamVideo
from connection_and_streaming.stream_audio_reciver import StreamAudioReciver
from voice_command.voice_cmd_stm import VoiceCommandComponent
from connection_and_streaming.controller import ControllerComponent
from gui.gui_controller import GuiController

if __name__ == "__main__":

    office_name = "office8"
    cap = Camera(0, cv2.CAP_DSHOW)

    voice_cmd_component = VoiceCommandComponent()
    voice_cmd_component.initialize_stm()

    stream_video_component = StreamVideo(cap, office_name)

    stream_audio_reciver_component = StreamAudioReciver(office_name)

    raspberry_pi_controller = ControllerComponent(office_name)

    gui_controller = GuiController(cap, office_name)
    gui_controller.initialize_stm()

    driver = stmpy.Driver()

    driver.add_machine(voice_cmd_component.stm)
    driver.add_machine(raspberry_pi_controller.stm)
    driver.add_machine(gui_controller.stm)
    driver.add_machine(stream_video_component.stm)
    driver.add_machine(stream_audio_reciver_component.stm)

    raspberry_pi_controller.stm_driver = driver
    voice_cmd_component.stm_driver = driver
    gui_controller.stm_driver = driver
    stream_audio_reciver_component.stm_driver = driver
    stream_video_component.stm_driver = driver

    driver.start()
    driver.start()
    driver.send("on", "Controller")

    gui_controller.start()
