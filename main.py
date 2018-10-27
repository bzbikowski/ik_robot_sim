from PyQt5.QtWidgets import QApplication
from window import MainWindow
import sys


def main():
    qapp = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(qapp.exec_())


if __name__ == "__main__":
    main()