# Importing necessary classes from PyQt5
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton

# Importing external libraries
import psutil
import speedtest
import socket
import time

# Creating a QThread subclass for running the speed test
class SpeedTestThread(QThread):
    # Declaring a signal for emitting a message when the speed test is finished
    signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        # Creating a Speedtest instance and performing the speed test
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1000000
        # Getting the IP address of the current device
        addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in addrs.items():
            for addr in interface_addresses:
                if addr.family == socket.AF_INET:
                    ip_address = addr.address
                    break
        # Formatting the message to display the IP address and download speed
        message = f"IP Address: {ip_address}, Download Speed: {download_speed:.2f} Mbps"
        # Emitting the message signal
        self.signal.emit(message)

# Creating a QDialog subclass for the main window
class MainWindow(QDialog):
    def __init__(self):
        super().__init__()

        # Setting the title of the window
        self.setWindowTitle("Network Status Checker")

        # Creating a QVBoxLayout instance for the layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Creating a QLabel instance for displaying the IP address
        self.ip_label = QLabel()
        self.layout.addWidget(self.ip_label)

        # Creating a QLabel instance for displaying the download speed
        self.speed_label = QLabel()
        self.layout.addWidget(self.speed_label)

        # Creating two QPushButton instances for running the speed test and closing the window
        self.update_button = QPushButton("Run Speed Test")
        self.close_button = QPushButton("Close")
        self.layout.addWidget(self.update_button)
        self.layout.addWidget(self.close_button)

        # Connecting the clicked signals of the buttons to their respective functions
        self.update_button.clicked.connect(self.start_speed_test)
        self.close_button.clicked.connect(self.close)

        # Initializing the thread variable to None
        self.thread = None

    # Function for running the speed test
    def start_speed_test(self):
        # If a thread is already running, return
        if self.thread and self.thread.isRunning():
            return
        # Disable the update button and set the speed label text to "Running speed test..."
        self.update_button.setEnabled(False)
        self.speed_label.setText("Running speed test...")
        # Creating a new SpeedTestThread instance and connecting its signal to the on_speed_test_finished function
        self.thread = SpeedTestThread(self)
        self.thread.signal.connect(self.on_speed_test_finished)
        # Starting the thread
        self.thread.start()

    # Function for updating the speed label with the result of the speed test
    def on_speed_test_finished(self, message):
        self.speed_label.setText(message)
        self.update_button.setEnabled(True)

    # Function for handling the window close event
    def closeEvent(self, event):
        # If a thread is running, terminate it and wait for it to finish
        if self.thread and self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()
        super().closeEvent(event)


if __name__ == "__main__":
    # Creating a QApplication instance
    app = QApplication([])
    # Creating a MainWindow instance and setting
    main_window = MainWindow() # The above code creates a QApplication object and then creates an instance of MainWindow.
    main_window.resize(400, 200) # It sets the size of the window to 400 x 200 and shows the window. Finally, it enters the event loop using app.exec_().
    main_window.show() # This event loop is responsible for handling events such as button clicks and window close events.
    app.exec_()