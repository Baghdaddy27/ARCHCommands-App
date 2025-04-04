import sys
from PyQt5.QtWidgets import QApplication
from modules.ui import CommandReferenceApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommandReferenceApp()
    window.show()
    sys.exit(app.exec_())