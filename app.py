# app.py
import sys
from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow

if __name__ == '__main__':
    # Create the application instance
    app = QApplication(sys.argv)

    # Create and display the main window
    window = MainWindow()
    window.show()

    # Start the event loop
    sys.exit(app.exec_())
