from PyQt5.QtWidgets import *       # UI Elements library
from PyQt5.QtGui import QFont       # Text fonts library
from PyQt5 import uic
from PyQt5 import QtCore


class NewCaseWindow(QMainWindow):
    """
    Class definition for window that allows users to input custom information for creating a new case
    """
    def __init__(self, parent=None):
        super(NewCaseWindow, self).__init__(parent)
        # Keep a local copy of the parent object
        self.homeparent = parent

        # Load the Home Window UI design from file
        uic.loadUi("newcasewindow.ui", self)
        self.setFixedSize(self.width(), self.height())
        self.editcasename.setFocus()

        # Connect buttons to on-click events
        self.createcasebtn.clicked.connect(self.createCase)

    def createCase(self):
        """
        Function to call HomeWindow parent's setter function (setNewCaseInfo) to
        save user input for creating new case
        :return: None
        """
        # Capture the input fields into a dictionary
        info = {"casename": self.editcasename.text(), "casedescription": self.editcasedescription.toPlainText(),
                "walletaddresses": self.editwalletaddresses.toPlainText()}

        # Define and call function that will @gerald @clement
        # 1) Ensure no empty input
        # 2) Sanitize wallet addresses where necessary
        # 3) Split Wallet Addresses string into a list

        # Save the data in the parent HomeWindow's context
        self.homeparent.setNewCaseInfo(info)
        # self.hide()
        self.deleteLater()


class HomeWindow(QMainWindow):
    """
    Class definition for the default home page on application startup
    """
    def __init__(self, parent=None):
        super(HomeWindow, self).__init__(parent)
        # Load the Home Window UI design from file
        uic.loadUi("home.ui", self)
        self.setFixedSize(self.width(), self.height())

        # Declaration of Child Windows
        self.newcasewindow = None

        # Variables used by child windows
        self.newcaseinfo = dict()

        # Connect buttons to on-click events
        self.newcasebtn.clicked.connect(self.openNewCaseWindow)
        self.opencasebtn.clicked.connect(self.openExistingCaseWindow)

    def setNewCaseInfo(self, info):
        """
        Handler function for accepting data from NewCaseWindow child
        :param info: Dictionary containing user input for case name, description, and wallet addresses
        :return: None
        """
        self.newcaseinfo = info
        print(self.newcaseinfo)

    def openNewCaseWindow(self):
        """
        Function to spawn/display a child window for inputting new case information
        :return: None
        """
        # Instantiate new case window and show it immediateley if does not exists
        self.newcasewindow = NewCaseWindow(self)
        self.newcasewindow.show()

    def openExistingCaseWindow(self):
        """
        Function to open a file dialogue window to select a existing case file
        :return: None
        """
        # print(self.newcaseinfo)

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                      "JSON Files (*.json);;All Files (*)", options=options)
        if fileName:
            print(f"[*] Opening file: {fileName}")


def main():
    # Define the PyQT5 application object
    app = QApplication([])

    # Create the main window and show it
    home = HomeWindow()
    home.show()

    # Start the PyQT5 app
    app.exec_()


if __name__ == "__main__":
    main()
