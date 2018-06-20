import sys

from PyQt5.QtWidgets import QApplication
from view import DialogMain


def main():
    app = QApplication(sys.argv)
    window = DialogMain.DialogMain()
    window.setWindowTitle('Abacus PYQ')
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

