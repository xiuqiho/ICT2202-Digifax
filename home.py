"""
Author:         Ho Xiu Qi

Date Completed: 25th Oct 2021
Last Updated:   25th Oct 2021

Description:
> GUI code for the ICT2202 Team Assignment "Digifax"

Aliases used:
> WOI = Wallet of Interest
"""
from PyQt5.QtWidgets import *                           # UI Elements library
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView     # Widget to display Pyvis HTML files
from PyQt5 import uic                                   # Library to load

from pyvis.network import Network                       # Core library for producing the transaction network graphs

from constants import *                                 # All constants used in the project
import random


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
        self.caseinfo = dict()
        self.caseinfo = {"casename": "Case Study on Gerald", "casedescription": "It has been suspected that gerald is a faggot and a slippery haxer who doesn't get caught...",
                "walletaddresses": ["0x0ea288c16bd3a8265873c8d0754b9b2109b5b810", "0xbdb5829f5452Bd10bb569B5B9B54732001ab5ab9", "0xDa007777D86AC6d989cC9f79A73261b3fC5e0DA0"],
                         "walletrelationships": {"0x0ea288c16bd3a8265873c8d0754b9b2109b5b810":[["0xbdb5829f5452Bd10bb569B5B9B54732001ab5ab9", 2]],
                                                 "0xDa007777D86AC6d989cC9f79A73261b3fC5e0DA0": [["0xbdb5829f5452Bd10bb569B5B9B54732001ab5ab9", 2]]}}

        # Connect buttons to on-click events
        self.newcasebtn.clicked.connect(self.openNewCaseWindow)
        self.opencasebtn.clicked.connect(self.openExistingCaseWindow)

        self.hide()
        self.db = Dashboard(self)
        self.db.show()

    def setNewCaseInfo(self, info):
        """
        Handler function for accepting data from NewCaseWindow child
        :param info: Dictionary containing user input for case name, description, and wallet addresses
        :return: None
        """
        self.caseinfo = info
        print(self.caseinfo)

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
        # print(self.caseinfo)

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                      "JSON Files (*.json);;All Files (*)", options=options)
        if fileName:
            print(f"[*] Opening file: {fileName}")


class Dashboard(QMainWindow):
    """
    Class definition for the main Digifax dashboard
    """

    def __init__(self, parent=None):
        super(Dashboard, self).__init__(parent)
        # Keep a local copy of the parent object
        self.homeparent = parent

        # Load the Home Window UI design from file
        uic.loadUi("dashboard.ui", self)

        # Get all wallet addresses from the case
        # <Format> [WOI_1, WOI_2, WOI_3, ...]
        self.wallets_of_interest = list(set(self.homeparent.caseinfo["walletaddresses"]))

        # Get all relationships
        # <Format> {wallet: [[relative1, weight],[relative2, weight]], ...}
        self.wallet_relationships = self.homeparent.caseinfo["walletrelationships"]

        # Call function to tune dimensions and window properties of dashboard
        self.resolution = QDesktopWidget().screenGeometry()
        self.config_dashboard()

        # Initialize the webpage view (panel) on the dashboard
        self.initWebView()

        # Call function to retrieve wallet addresses transactions(assuming new case)

        # Call function to plot the PyVis graph
        self.graph = Network(height=f'{self.resolution.height() * SCREEN_HEIGHT}px',
                             width=f'{self.resolution.width() * (WEBPANEL_WIDTH - 0.02)}px',
                             bgcolor='#000000',
                             font_color='#ffffff')
        # self.graph.show_buttons(filter_=True)
        self.initGraph()

        # Call function to populate list view
        for wallet in self.wallets_of_interest:
            temp = QListWidgetItem()
            temp.setText(wallet)
            temp.setToolTip("Yo mum g@y")           # ** Change to total # of transactions once backend code integrated **
            self.listWidget.addItem(temp)

        self.walletAddress.setText(self.homeparent.caseinfo["walletaddresses"][2])
        self.walletAddress.setAlignment(Qt.AlignCenter)

        # Connect buttons
        self.addRelationshipBtn.clicked.connect(self.addWOI)

    def config_dashboard(self):
        """
        Function to setup all dashboard window and widget properties
        :return: None
        """
        # Set window size
        self.setFixedSize(int(self.resolution.width() * SCREEN_WIDTH), int(self.resolution.height() * SCREEN_HEIGHT))

        # Center the screen
        self.move(int(self.resolution.width() / 2) - int(self.frameSize().width() / 2),
                  int(self.resolution.height() / 2) - int(self.frameSize().height() / 2))

        # Set QWidget (webwidget) size
        self.webwidget.setGeometry(0, 0, int(self.resolution.width() * WEBPANEL_WIDTH), int(self.resolution.height() * SCREEN_HEIGHT))

        # Set QLabel (walletAddress) size
        self.walletAddress.setGeometry(int(self.resolution.width() * WEBPANEL_WIDTH), 0, int(self.resolution.width() * SIDEPANEL_WIDTH),
                                       int(self.resolution.height() * LABEL_HEIGHT))

        # Set QListWidget (listWidget) size
        self.listWidget.setGeometry(int(self.resolution.width() * WEBPANEL_WIDTH), int(self.resolution.height() * LABEL_HEIGHT),
                                    int(self.resolution.width() * SIDEPANEL_WIDTH), int(self.resolution.height() * SCREEN_HEIGHT * LIST_HEIGHT))

    def initWebView(self):
        """
        Function to initialize the QWebEngineView object and stick it to the "webwidget" QWidget
        :return: None
        """
        vbox = QVBoxLayout(self.webwidget)
        self.wev = QWebEngineView()
        vbox.addWidget(self.wev)

    def initGraph(self):
        """
        Function to update graph contents and save to a new .html file
        :return: None
        """
        # Add all given nodes to the graph
        for wallet in self.wallets_of_interest:
            self.graph.add_node(wallet, wallet[:8], color=DEFAULT_COLORS[random.randint(0,3)])

        # Add all relationships (if any)
        for focus, relatives in self.wallet_relationships.items():
            for relative in relatives:
                self.graph.add_edge(focus, relative[ADDR], value=relative[WEIGHT])

        # Save the graph into a file
        self.graph.show("graph.html")
        self.loadPage('graph.html')

    def addWOI(self):
        """
        Function to update (1) backend data structs and (2) graph WRT to adding a WOI
        :param wallet: A string representation of wallet address that user is interested in
        :return:
        """
        woi = self.listWidget.selectedItems()[0].text()
        focusedWallet = self.walletAddress.text()

        # Append wallet to list of interested wallets
        if woi not in self.wallets_of_interest:
            self.wallets_of_interest.append(woi)
            self.graph.add_node(woi, woi[:8], color=DEFAULT_COLORS[random.randint(0,4)])

        # Update WOI relationships
        if woi != focusedWallet and [woi, 2] not in self.wallet_relationships[focusedWallet]:
            print(self.wallet_relationships[focusedWallet])
            self.wallet_relationships[focusedWallet].append([woi, 2])
            print(self.wallet_relationships[focusedWallet])
            self.graph.add_edge(focusedWallet, woi, value=DEFAULT_WEIGHT)   # Change DEFAULT_WEIGHT to # of transactions

            # Reload the graph
            self.graph.show("graph.html")
            self.loadPage('graph.html')

    def loadPage(self, pagename):
        """
        Function to render a given .html page onto the QWebEngineView widget
        :param pagename: A string representation of a target webpage (.html) to render
        :return: None
        """
        with open(pagename, 'r') as f:
            html = f.read()
        self.wev.setHtml(html)


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
