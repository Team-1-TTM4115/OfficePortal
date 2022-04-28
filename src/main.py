from gui.camera import Camera
import cv2
import stmpy
from StreamVideo import StreamVideo
from connection_and_streaming.streamAudioReciver import StreamAudioReciver


# from gui.gui_controller import GuiController
# from gui.main_screen import Screen

from voice_command.voice_cmd_stm import VoiceCommandComponent
from connection_and_streaming.controller import ControllerComponent
from gui.gui_controller import GuiController   


if __name__ == "__main__":
    # gui = GuiController()
    # gui.start()

    office_name= "office7"
    cap = Camera(0,cv2.CAP_DSHOW)

    voice_cmd_component = VoiceCommandComponent()
    voice_cmd_component.initialize_stm()

    stream_video_component = StreamVideo()
    stream_video_component.initialize_stm(cap,office_name)

    stream_audio_reciver_component = StreamAudioReciver()
    stream_audio_reciver_component.initialize_stm(office_name)

    connection_controller = ControllerComponent()
    connection_controller.initialize_stm(office_name)

    gui_controller = GuiController(cap,office_name)
    gui_controller.initialize_stm()

    driver = stmpy.Driver()
    #driver_voice = stmpy.Driver()

    driver.add_machine(voice_cmd_component.stm)
    driver.add_machine(connection_controller.stm)
    driver.add_machine(gui_controller.stm)
    driver.add_machine(stream_video_component.stm)
    driver.add_machine(stream_audio_reciver_component.stm)


    connection_controller.stm_driver = driver   
    voice_cmd_component.stm_driver = driver
    gui_controller.stm_driver = driver
    stream_audio_reciver_component.stm_driver = driver
    stream_video_component.stm_driver =driver #driver_voice

    driver.start()
    driver.start()
    driver.send("on", "Controller")

    gui_controller.start()



