import sys
from PyQt5.QtWidgets import QApplication
from controllers.LoginController import LoginController

def main():
    app = QApplication(sys.argv)

    controller = LoginController()
    controller.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()