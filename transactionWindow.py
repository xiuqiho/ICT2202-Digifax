from PyQt5.QtWidgets import *
from PyQt5 import uic


data = {'col1':['1','2','3','4'],
'col2':['1','2','1','3'],
'col3':['1','1','2','1']}

class TransactionWindow(QMainWindow):
    """
    Class definition for transaction window
    """
    def __init__(self, data, parent=None):
        super(TransactionWindow, self).__init__(parent)
        # Keep a local copy of the parent object
        self.homeparent = parent

        # Load the Home Window UI design from file
        uic.loadUi("./UI/transactions.ui", self)

    def setData(self):
        horizontalHeaders = []
        for n, key in enumerate(sorted(data.keys())):
            item = QTableWidgetItem(key)

        #     horizontalHeaders.append(key)
        # self.setHorizontalHeaderLabels(horizontalHeaders)


def main():
    # Define the PyQT5 application object
    app = QApplication([])

    # Create the main window and show it
    tw = TransactionWindow(data)
    tw.show()

    # Start the PyQT5 app
    app.exec_()


if __name__ == "__main__":
    main()
