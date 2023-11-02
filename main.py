import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
import Ui_MainWindow
import Controller
import threading
from utils import Communication
import alarm

class MyWindow(QMainWindow):
    def __init__(self, communication: Communication):
        super().__init__()
        self.communication_ = communication
        self.communication_.ui_signal.connect(self.update_ui)
        self.controller_ = None
        self.exit_flag = False

    def set_up(self, controller):
        self.controller_ = controller

    def update_ui(self):
        if self.controller_ is not None:
            self.controller_.ui_update()

    def closeEvent(self, event):
        self.exit_flag = True

def data_task(controller, window: MyWindow):
    while not window.exit_flag:
        controller.data_loop()
        # try:
        #     controller.data_loop()
        # except Exception as e:
        #     alarm.activate(message=f"Program runs again because of error: {e}", to=["Hieu"])

def main():
    app = QApplication(sys.argv)
    communication = Communication()
    MainWindow = MyWindow(communication)
    ui = Ui_MainWindow.Ui_MainWindow()
    ui.setupUi(MainWindow)
    controller = Controller.Controller(MainWindow, communication)
    MainWindow.set_up(controller=controller)
    MainWindow.setWindowTitle("Swap-Quarterly-Biquarterly")

    MainWindow.show()
    data_thread = threading.Thread(target=data_task, args=(controller, MainWindow))
    data_thread.start()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
