import stmpy

# from gui.gui_controller import GuiController
# from gui.main_screen import Screen

from voice_command.voice_cmd_stm import VoiceCommandComponent
from connection_and_streaming.controller import ControllerComponent
from gui.gui_controller import GuiController    

if __name__ == "__main__":
    # gui = GuiController()
    # gui.start()

    voice_cmd_component = VoiceCommandComponent()
    voice_cmd_component.initialize_stm()

    connection_controller = ControllerComponent()
    connection_controller.initialize_stm()

    gui_controller = GuiController()
    gui_controller.initialize_stm()

    driver = stmpy.Driver()

    driver.add_machine(voice_cmd_component.stm)
    driver.add_machine(connection_controller.stm)
    driver.add_machine(gui_controller.stm)

    connection_controller.stm_driver = driver   
    voice_cmd_component.stm_driver = driver
    gui_controller.stm_driver = driver

    driver.start()
    driver.send("on", "Controller")
    gui_controller.start()
