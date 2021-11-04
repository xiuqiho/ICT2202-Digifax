"""
Author:         Ho Xiu Qi

Date Completed: 25th Oct 2021
Last Updated:   25th Oct 2021

Description:
> GUI code for the ICT2202 Team Assignment "Digifax" Home & Dashboard page

Aliases used:
> WOI = Wallet of Interest
"""
from PyQt5.QtWidgets import *                           # UI Elements library
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWebEngineWidgets import QWebEngineView     # Widget to display Pyvis HTML files
from PyQt5 import uic                                   # Library to load
from pyvis.network import Network                       # Core library for producing the transaction network graphs

from constants import *                                 # All constants used in the project
from transactionWindow import TransactionWindow
from nodeProfileWindow import NodeProfileWindow
# from python_scripts.DigiFax_EthScan_multiproc import DigiFax_EthScan
from python_scripts.DigiFax_EthScan_multithread import DigiFax_EthScan

import multiprocessing
import threading

import random                                           # To randomly choose a node color
from pyperclip import copy                              # For putting text into user's clipboard
import re                                               # For Text Search filtering
import json                                             # For opening / writing case files in .json format


class NewCaseWindow(QMainWindow):
    """
    Class definition for window that allows users to input custom information for creating a new case
    """
    def __init__(self, parent=None):
        super(NewCaseWindow, self).__init__(parent)
        # Keep a local copy of the parent object
        self.homeparent = parent

        # Load the Home Window UI design from file
        uic.loadUi("./UI/newcasewindow.ui", self)
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
                "walletaddresses": [addr.lower() for addr in set(self.editwalletaddresses.toPlainText().split('\n'))]}

        # Check if supplied wallet addresses are all valid
        for addr in info["walletaddresses"]:
            if not self.homeparent.isValidWalletAddress(addr) and addr != "":
                self.homeparent.displayMessage(f"[-] Unaccepted wallet address format:\n{addr}")
                return

        # Check if fields are empty (description and casename are not compulsory)
        if len(info["casename"]) <= 0 or not info["casename"].isalnum():
            self.homeparent.displayMessage(f"[-] Please enter a valid case name")
            return

        # Set the walletaddresses list
        info["walletaddresses"] = list(set(info["walletaddresses"]))

        # Save the data in the parent HomeWindow's context
        self.homeparent.setNewCaseInfo(info)
        self.hide()
        self.deleteLater()


class HomeWindow(QMainWindow):
    """
    Class definition for the default home page on application startup
    """
    def __init__(self, parent=None):
        super(HomeWindow, self).__init__(parent)
        # Load the Home Window UI design from file
        uic.loadUi("./UI/home.ui", self)
        self.setFixedSize(self.width(), self.height())

        # Declaration of Child Windows
        self.newcasewindow = None
        self.db = None
        self.nodeprofilewindow = None
        self.txnwindow = None

        # Variables used by child windows
        self.caseinfo = dict()
        # Decalre filename where any active case will be saved into
        self.casefile = str()

        # Connect buttons to on-click events
        self.newcasebtn.clicked.connect(self.openNewCaseWindow)
        self.opencasebtn.clicked.connect(self.openExistingCaseWindow)

    def setNewCaseInfo(self, info):
        """
        Handler function for accepting data from NewCaseWindow child
        :param info: Dictionary containing user input for case name, description, and wallet addresses
        :return: None
        """
        # Create New Case data structure based on template from constants.py
        self.caseinfo = TEMPLATE
        self.caseinfo["casename"] = info["casename"]
        self.caseinfo["casedescription"] = info["casedescription"]
        self.caseinfo["walletaddresses"] = info["walletaddresses"]
        self.caseinfo["filename"] = info["casename"] + CASE_FILE_EXT
        self.casefile = self.caseinfo["filename"]

        # Open the dashboard
        self.openDashboard()

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
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open a Existing Case File (.json)", "",
                                                      "JSON Files (*.json);;All Files (*)", options=options)
        if fileName:
            # Try to load the file contents into 'self.caseinfo'
            print(f"[*] Opening file: {fileName}")
            with open(fileName, 'r') as f:
                data = json.load(f)
                # If keys do not match, reject the opening of the given file
                if data.keys() != TEMPLATE.keys():
                    self.displayMessage("[-] Unrecognized case file: Inconsistent data keys")
                    return
                elif len(data["casename"]) <= 0:
                    self.displayMessage("[-] Unrecognized case file: No case name in given file")
                    return

                # If all goes well, use the read data as the case data in 'self.caseinfo' and open the dashboard
                self.caseinfo = data
                self.casefile = data["filename"]
                self.openDashboard()

    def openDashboard(self):
        """
        Function to create dashboard instance and show it
        :return: None
        """
        # Display the dashboard and hide current window (Home window)
        self.db = Dashboard(self)
        self.db.show()

    def openNodeProfileWindow(self, focusnode):
        """
        Function to spawn/display a child window for inputting new case information
        :return: None
        """
        # Instantiate woi profile window and show it immediateley
        self.nodeprofilewindow = NodeProfileWindow(focusnode, self)
        self.nodeprofilewindow.show()

    def signalProfileUpdated(self):
        """
        Function to bind a specified alias to a node (WOI) address in the caseinfo["aliases"] dictionary
        :return: None
        """
        self.db.populateWoiList()
        self.db.populateGraph()

    def openTransactionWindow(self, data):
        """
        Function for displaying given transactions
        :param data: dataset received from Dashboard containing specific transactions
        :return: None
        """
        self.txnwindow = TransactionWindow(data)
        self.txnwindow.show()

    def isValidWalletAddress(self, addr):
        """
        Function that checks if a given string is a valid wallet address
        :param addr: String representation of a wallet address
        :return: True if valid wallet address, else False
        """
        if len(addr) == 42:
            if addr[0] == '0' and addr[1] == 'x' and addr[2:].isalnum():
                return True
        return False

    def saveFile(self, wois, wrs):
        """
        Function to save current work progress into file path specified at 'self.casefile'
        :param wois: latest List of wallets of interests
        :param wrs: latest Dictionary of all relationships
        :return: None
        """
        # Update wallet addresses, relationships inside 'self.caseinfo'
        self.caseinfo["walletaddresses"] = wois
        self.caseinfo["walletrelationships"] = wrs

        print(f"[*] Saving to {self.casefile}")
        # Directly save into 'self.casefile'
        with open(self.casefile, 'w') as f:
            json.dump(self.caseinfo, f)

    def saveFileAs(self, wois, wrs):
        """
        Function to save current work progress in a file path chosen by user from file dialog
        :param wois: latest List of wallets of interests
        :param wrs: latest Dictionary of all relationships
        :return: None
        """
        # Open file dialog for user to choose path to file for saving
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Case File", "",
                                                  "JSON Files (*.json)", options=options)

        if fileName:
            # Update 'self.casefile' to new filename
            self.casefile = fileName + CASE_FILE_EXT
            # Update the data structure's filename entry
            self.caseinfo["filename"] = fileName + CASE_FILE_EXT

            # Save the file
            self.saveFile(wois, wrs)
            print(f"[*] Completed saving to {self.casefile}")

    def displayMessage(self, message):
        """
        Function to display message box with arbitrary error message
        :param msg: String representation of desired error message to display to user
        :return: None
        """
        msg = QMessageBox()
        msg.setText(message)
        msg.exec_()


class Dashboard(QMainWindow):
    """
    Class definition for the main Digifax dashboard
    """
    def __init__(self, parent=None):
        super(Dashboard, self).__init__(parent)
        self.loaded = 0
        # Keep a local copy of the parent object
        self.homeparent = parent
        # Load the Home Window UI design from file
        uic.loadUi("./UI/dashboard.ui", self)

        # Etherscan object
        self.ethscan = DigiFax_EthScan()

        # Get all wallet addresses from the case
        # <Format> [WOI_1, WOI_2, WOI_3, ...]
        self.wallets_of_interest = list(set(self.homeparent.caseinfo["walletaddresses"]))

        # Get all relationships
        # <Format> {wallet: [[relative1, weight],[relative2, weight]], ...}
        self.wallet_relationships = self.homeparent.caseinfo["walletrelationships"]

        # Declare dataset that will be used to hold filtered transactions in Transaction List
        self.dataset = list()
        self.transactions_by_address = dict()
        self.sorted_addresses = list()

        # Call function to tune dimensions and window properties of dashboard
        self.resolution = QDesktopWidget().screenGeometry()
        self.config_dashboard()

        # Initialize the webpage view (panel) on the dashboard
        self.initWebView()

        # Call function to retrieve wallet addresses transactions(assuming new case)

        # Call function to plot the PyVis graph
        self.graph = None
        self.populateGraph()
        # self.graph.show_buttons(filter_=True)

        # Initialize default values for dashboard
        self.initDashboardDefaultValues()

        # Call function to populate node (WOI) list view
        self.selectedWOI = None
        self.populateWoiList()

        # Call function to populate node (Transactions) list view
        # self.populateTransactionList()

        # Setup events
        self.setupEvents()

        # Set page to loaded once all setup / config is done
        self.loaded = 1

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

        # Set QWidget (webwidget) position and size
        self.webwidget.setGeometry(0,
                                   0,
                                   int(self.resolution.width() * WEBPANEL_WIDTH),
                                   int(self.resolution.height() * SCREEN_HEIGHT))

        # Set QLabel (filterLabel) position and size
        self.filterLabel.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (WEBPANEL_WIDTH + 0.035)),
                                     int(self.resolution.height() * SCREEN_HEIGHT * FLABEL_Y_OFFSET),
                                     int(self.resolution.width() * SCREEN_WIDTH * FLABEL_WIDTH),
                                     int(self.resolution.height() * SCREEN_HEIGHT * FLABEL_HEIGHT))

        # Set QLineEdit (walletLineEdit) position and size
        self.walletLineEdit.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (WEBPANEL_WIDTH + 0.018 + FLABEL_WIDTH)),
                                        int(self.resolution.height() * SCREEN_HEIGHT * FEDIT_Y_OFFSET),
                                        int(self.resolution.width() * SCREEN_WIDTH * FEDIT_WIDTH),
                                        int(self.resolution.height() * SCREEN_HEIGHT * FEDIT_HEIGHT))

        # Set QPushButton (addNodeBtn) position and size
        self.addNodeBtn.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (1 - 0.072)),
                                             int(self.resolution.height() * SCREEN_HEIGHT * ANBTN_Y_OFFSET),
                                             int(self.resolution.width() * SCREEN_WIDTH * ANBTN_WIDTH),
                                             int(self.resolution.height() * SCREEN_HEIGHT * ANBTN_HEIGHT))

        # Set QListWidget (listWidget) position and size
        self.nodeListWidget.setGeometry(int(self.resolution.width() * WEBPANEL_WIDTH),
                                    int(self.resolution.height() * (FLABEL_HEIGHT+0.01)),
                                    int(self.resolution.width() * SIDEPANEL_WIDTH),
                                    int(self.resolution.height() * SCREEN_HEIGHT * NLIST_HEIGHT))

        # Set QLabel (displayOrderLabel) position and size
        self.displayOrderLabel.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (WEBPANEL_WIDTH + 0.035)),
                                     int(self.resolution.height() * SCREEN_HEIGHT * DOLABEL_Y_OFFSET),
                                     int(self.resolution.width() * SCREEN_WIDTH * DOLABEL_WIDTH),
                                     int(self.resolution.height() * SCREEN_HEIGHT * DOLABEL_HEIGHT))

        # Set QComboBox (displayOrderPicker) position and size
        self.displayOrderPicker.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (WEBPANEL_WIDTH + 0.035 + DOLABEL_WIDTH)),
                                        int(self.resolution.height() * SCREEN_HEIGHT * DOPICKER_Y_OFFSET),
                                        int(self.resolution.width() * SCREEN_WIDTH * DOPICKER_WIDTH),
                                        int(self.resolution.height() * SCREEN_HEIGHT * DOPICKER_HEIGHT))
        # Add Display Order options into "displayOrderPicker"
        self.displayOrderPicker.addItems(["Descending", "Ascending"])

        # Set QLabel (transactionTypeLabel) position and size
        self.transactionTypeLabel.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (WEBPANEL_WIDTH + 0.055 + DOLABEL_WIDTH + DOPICKER_WIDTH)),
                                     int(self.resolution.height() * SCREEN_HEIGHT * TTLABEL_Y_OFFSET),
                                     int(self.resolution.width() * SCREEN_WIDTH * TTLABEL_WIDTH),
                                     int(self.resolution.height() * SCREEN_HEIGHT * TTLABEL_HEIGHT))

        # Set QComboBox (transactionTypePicker) position and size
        self.transactionTypePicker.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (WEBPANEL_WIDTH + 0.053 + DOLABEL_WIDTH + DOPICKER_WIDTH + TTLABEL_WIDTH)),
                                        int(self.resolution.height() * SCREEN_HEIGHT * TTPICKER_Y_OFFSET),
                                        int(self.resolution.width() * SCREEN_WIDTH * TTPICKER_WIDTH),
                                        int(self.resolution.height() * SCREEN_HEIGHT * TTPICKER_HEIGHT))

        # Add Transaction Type options into "transactionTypePicker"
        self.transactionTypePicker.addItems(["Outgoing", "Incoming", "All"])

        # Set QLabel (timeStartLabel) position and size
        self.timeStartLabel.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (WEBPANEL_WIDTH + 0.035)),
                                     int(self.resolution.height() * SCREEN_HEIGHT * TSLABEL_Y_OFFSET),
                                     int(self.resolution.width() * SCREEN_WIDTH * TSLABEL_WIDTH),
                                     int(self.resolution.height() * SCREEN_HEIGHT * TSLABEL_HEIGHT))

        # Set QDateEdit(timeStartPicker) position and size
        self.timeStartPicker.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (WEBPANEL_WIDTH + 0.035 + DOLABEL_WIDTH)),
                                     int(self.resolution.height() * SCREEN_HEIGHT * TSPICKER_Y_OFFSET),
                                     int(self.resolution.width() * SCREEN_WIDTH * TSPICKER_WIDTH),
                                     int(self.resolution.height() * SCREEN_HEIGHT * TSPICKER_HEIGHT))

        # Set QLabel (timeEndLabel) position and size
        self.timeEndLabel.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (WEBPANEL_WIDTH + DOLABEL_WIDTH + DOPICKER_WIDTH + 0.055)),
                                        int(self.resolution.height() * SCREEN_HEIGHT * TELABEL_Y_OFFSET),
                                        int(self.resolution.width() * SCREEN_WIDTH * TELABEL_WIDTH),
                                        int(self.resolution.height() * SCREEN_HEIGHT * TELABEL_HEIGHT))

        # Set QDateEdit(timeEndPicker) position and size
        self.timeEndPicker.setGeometry(
            int(self.resolution.width() * SCREEN_WIDTH * (WEBPANEL_WIDTH + DOLABEL_WIDTH + DOPICKER_WIDTH + TEPICKER_WIDTH + 0.0075)),
            int(self.resolution.height() * SCREEN_HEIGHT * TEPICKER_Y_OFFSET),
            int(self.resolution.width() * SCREEN_WIDTH * TEPICKER_WIDTH),
            int(self.resolution.height() * SCREEN_HEIGHT * TEPICKER_HEIGHT))
        # Enable calendar popup
        self.timeStartPicker.setCalendarPopup(True)
        self.timeEndPicker.setCalendarPopup(True)

        # Set default time range

        # Set QLabel (transactionsLabel) position and size
        self.transactionsLabel.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (WEBPANEL_WIDTH + 0.035)),
                                     int(self.resolution.height() * SCREEN_HEIGHT * TFLABEL_Y_OFFSET),
                                     int(self.resolution.width() * SCREEN_WIDTH * TFLABEL_WIDTH),
                                     int(self.resolution.height() * SCREEN_HEIGHT * TFLABEL_HEIGHT))

        # Set QLineEdit (transactionFilterEdit) position and size
        self.transactionFilterEdit.setGeometry(
            int(self.resolution.width() * SCREEN_WIDTH * (WEBPANEL_WIDTH + 0.037 + DOLABEL_WIDTH)),
            int(self.resolution.height() * SCREEN_HEIGHT * TFEDIT_Y_OFFSET),
            int(self.resolution.width() * SCREEN_WIDTH * TFEDIT_WIDTH),
            int(self.resolution.height() * SCREEN_HEIGHT * TFEDIT_HEIGHT))

        # Set QListWidget (transactionListWidget) position and size
        self.transactionListWidget.setGeometry(int(self.resolution.width() * WEBPANEL_WIDTH),
                                        int(self.resolution.height() * SCREEN_HEIGHT * (TFLABEL_Y_OFFSET + 0.035)),
                                        int(self.resolution.width() * SIDEPANEL_WIDTH),
                                        int(self.resolution.height() * SCREEN_HEIGHT * TLIST_HEIGHT))

        # Set QPushButton (dropRelationshipBtn) position and size   0.829 (1612px)
        self.dropRelationshipBtn.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (1 - 0.171)),
                                            int(self.resolution.height() * SCREEN_HEIGHT * RS_BTN_Y_OFFSET),
                                            int(self.resolution.width() * RS_BTN_WIDTH),
                                            int(self.resolution.height() * RS_BTN_HEIGHT))

        # Set QPushButton (addRelationshipBtn) position and size 0.913 (1776px)
        self.addRelationshipBtn.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (1 - 0.087)),
                                    int(self.resolution.height() * SCREEN_HEIGHT * RS_BTN_Y_OFFSET),
                                    int(self.resolution.width() * RS_BTN_WIDTH),
                                    int(self.resolution.height() * RS_BTN_HEIGHT))

        # Set QPushButton (dropNodeBtn) position and size
        self.dropNodeBtn.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (1 - 0.255)),
                                            int(self.resolution.height() * SCREEN_HEIGHT * RS_BTN_Y_OFFSET),
                                            int(self.resolution.width() * RS_BTN_WIDTH),
                                            int(self.resolution.height() * RS_BTN_HEIGHT))

    def initWebView(self):
        """
        Function to initialize the QWebEngineView object and stick it to the "webwidget" QWidget
        :return: None
        """
        vbox = QVBoxLayout(self.webwidget)
        self.wev = QWebEngineView()
        vbox.addWidget(self.wev)

    def createGraph(self):
        """
        Function to initialize the PyVis Network graph with default parameters
        :return: None
        """
        self.graph = Network(height=f'{self.resolution.height() * (SCREEN_HEIGHT - 0.035)}px',
                             width=f'{self.resolution.width() * (WEBPANEL_WIDTH - 0.024)}px',
                             bgcolor='#000000',
                             font_color='#ffffff')

    def populateGraph(self):
        """
        Function to update graph contents and save to a new .html file
        :return: None
        """
        # Reset graph
        self.createGraph()

        # Add all given nodes to the graph
        for wallet in self.wallets_of_interest:
            # Set display label (for the node in the graph) using the alias if it exists
            if wallet in self.homeparent.caseinfo["aliases"].keys():
                display_lbl = self.homeparent.caseinfo["aliases"][wallet]
            else:
                display_lbl = wallet[:ADDR_DISPLAY_LIMIT]

            self.graph.add_node(wallet, display_lbl, color=DEFAULT_COLORS[random.randint(0,3)])

        # Add all relationships (if any)
        for focus, relatives in self.wallet_relationships.items():
            for relative in relatives:
                self.graph.add_edge(focus, relative[ADDR], value=relative[WEIGHT])

        # Save the graph into a file
        self.graph.save_graph("graph.html")
        self.loadPage('graph.html')

    def addNode(self, woi):
        """
        Function to add a specific address as a new node into the graph and backend structs
        :param woi: The wallet address that user wants to add to the graph as a node (MUST BE IN LOWERCASE!!!)
        :return: None
        """
        if woi not in self.wallets_of_interest:
            # Append wallet to list of interested wallets
            self.wallets_of_interest.append(woi)

    def addNodeBtnHandler(self):
        """
        Function to handle 'Add Node' button to add a new node and render the change on the graph
        :return: None
        """
        # If input text is a valid wallet address and it does not already exist
        woi = self.walletLineEdit.text().split(' ')[0].lower()
        if self.homeparent.isValidWalletAddress(woi):
            if woi not in self.wallets_of_interest:
                self.addNode(woi)

                # Update the WOI Node List
                self.populateWoiList()

                # Reload the graph
                self.populateGraph()

                # Clear 'walletLineEdit' text
                self.walletLineEdit.clear()
            else:
                self.homeparent.displayMessage("[-] Unable to add node:\nNode with this address already exists")
        else:
            self.homeparent.displayMessage("[-] Unable to add node:\nInvalid wallet address given")

    def dropNode(self, woi):
        """
        Function to drop a specific address node from the graph.
        Doing so will also automatically delete all relationships the node has (if any)
        :param woi: The wallet node that user wants to drop from the graph (MUST BE IN LOWERCASE!!!)
        :return: None
        """
        # If woi in self.wallets_of_interest:
        if woi in self.wallets_of_interest:
            # Delete wallet from list of interested wallets
            self.wallets_of_interest.remove(woi)

            # Delete all relationships this wallet has been registered with
            try:
                del self.wallet_relationships[woi]
            except KeyError:
                pass

            # If wallet exists as a relationship under the registration of another wallet, Delete it
            to_remove = list()
            for focus, relatives in self.wallet_relationships.items():
                for relative in relatives:
                    if woi == relative[ADDR]:
                        to_remove.append({"focus": focus, "relative": relative})
            for removable in to_remove:
                self.wallet_relationships[removable["focus"]].remove(removable["relative"])

    def dropNodeBtnHandler(self):
        """
        Function to handle 'Drop Node' button to drop a existing node and render the change on the graph
        :return: None
        """
        try:
            woi = self.nodeListWidget.currentItem().text().split(' ')[0].lower()
            # If woi in self.wallets_of_interest:
            if woi in self.wallets_of_interest:
                self.dropNode(woi)

                # Update the WOI Node List
                self.populateWoiList()

                # Reload the graph
                self.populateGraph()
        except AttributeError as err:
            # Add notification to user telling them to select a WOI (node)
            if self.loaded:
                self.homeparent.displayMessage("[-] Unable to drop node:\nNo node (WOI) was selected")

    def getRSWeight(self, focus_node, txn_addr):
        """
        Function to get a corresponding weight for the rs between WOI and address selected in the transaction list
        :return weight: An integer representation of the weight to draw for relationship of given woi & transaction
        """
        total_txn_count = int()

        try:
            if txn_addr in self.homeparent.caseinfo['data'][STATS][focus_node][UNIQ_IN].keys():
                total_txn_count += self.homeparent.caseinfo['data'][STATS][focus_node][UNIQ_IN][txn_addr]
            if txn_addr in self.homeparent.caseinfo['data'][STATS][focus_node][UNIQ_OUT].keys():
                total_txn_count += self.homeparent.caseinfo['data'][STATS][focus_node][UNIQ_OUT][txn_addr]

            if total_txn_count < LOWER_BOUND:
                return LOW_WEIGHT
            elif total_txn_count <= MIDDLE_BOUND:
                return MEDIUM_WEIGHT
            else:
                return HIGH_WEIGHT
        except KeyError:
            pass

    def addRelationship(self):
        """
        Function to update backend data structs
        :return: None
        """
        try:
            focusedWallet = self.nodeListWidget.currentItem().text().split(' ')[0].lower()                # selected node
            woi = self.transactionListWidget.currentItem().text().split("] ")[1].lower()    # selected transaction

            # Add node to wallet_of_interest if necessary (node doesn't exist yet)
            self.addNode(woi)

            # Update WOI relationships
            if focusedWallet not in self.wallet_relationships.keys():
                self.wallet_relationships[focusedWallet] = list()

            # If relationship does not already exist, add it
            if woi != focusedWallet:
                # Get weight of relationship between focusedWallet and woi
                weight = self.getRSWeight(focusedWallet, woi)

                if [woi, weight] not in self.wallet_relationships[focusedWallet]:
                    self.wallet_relationships[focusedWallet].append([woi, weight])

                    # Update the WOI Node List
                    self.populateWoiList()

                    # Reload the graph
                    self.populateGraph()

        except AttributeError as err:
            # Add notification to user telling them to select a WOI (node)
            if self.loaded:
                self.homeparent.displayMessage("[-] Unable to add relationship:\nPlease select (1) a node and (2) a transaction address")

    def dropRelationship(self):
        """
        Function to update (1) backend data structs and (2) graph WRT to removing a WOI
        :return: None
        """
        try:
            focusedWallet = self.nodeListWidget.currentItem().text().split(' ')[0].lower()   # selected node
            woi = self.transactionListWidget.currentItem().text().split("] ")[1].lower()      # selected transaction
            # Exit function if key of focusedWallet (selected node in Node List) does not exist
            if focusedWallet not in self.wallet_relationships.keys():
                return

            # Remove WOI relationship
            if woi != focusedWallet:
                # Get weight of relationship between focusedWallet and woi
                weight = self.getRSWeight(focusedWallet, woi)
                if [woi, weight] in self.wallet_relationships[focusedWallet]:
                    del self.wallet_relationships[focusedWallet][self.wallet_relationships[focusedWallet].index([woi, weight])]
                    try:
                        # Delete node if no more edges exists for it
                        if woi not in self.wallet_relationships.keys() and woi in self.wallets_of_interest:
                            self.dropNode(woi)
                    except IndexError as err:
                        if self.loaded:
                            self.homeparent.displayMessage(
                                f"[-] Unable to delete relationship between:\n'{focusedWallet}'\nto\n'{woi}'\n\nReason: {err}")

                    # Update the WOI Node List
                    self.populateWoiList()

                    # Reload the graph
                    self.populateGraph()
        except AttributeError as err:
            # Add notification to user telling them to select a WOI (node)
            if self.loaded:
                self.homeparent.displayMessage(
                    "[-] Unable to drop relationship:\nPlease select (1) a node and (2) a transaction address")

    def populateWoiList(self):
        """
        Function to populate WOI (nodes) list
        :return: None
        """
        try:
            # Get the currently selected item
            previous = self.nodeListWidget.currentItem()
            if previous is not None:
                previous = previous.text().split(' ')[0].lower()

            # Reset the WOI list
            self.nodeListWidget.clear()

            # Add all WOI into the list
            for wallet in self.wallets_of_interest:
                temp = QListWidgetItem()
                # Set Alias at end of WOI address if it exists
                if wallet in self.homeparent.caseinfo["aliases"].keys():
                    temp.setText(wallet + f" [{self.homeparent.caseinfo['aliases'][wallet]}]")
                else:
                    temp.setText(wallet)
                # Set tooltip (hover) over each WOI entry as the total transactions it has (incoming+outgoing)
                if STATS in self.homeparent.caseinfo["data"].keys():
                    if wallet in self.homeparent.caseinfo["data"][STATS].keys():
                        temp.setToolTip(f"Total Transactions: {self.homeparent.caseinfo['data'][STATS][wallet][TOTAL_TXNS]}")
                    else:
                        temp.setToolTip(f"Total Transactions: [NO DATA]")
                else:
                    print("[-] No STATS")
                self.nodeListWidget.addItem(temp)

            # Set previous item as selected if it still exists
            prev_item = self.nodeListWidget.findItems(previous, Qt.MatchContains)
            if previous is not None and len(prev_item) > 0:
                self.nodeListWidget.setCurrentItem(prev_item[0])
        except RuntimeError:
            pass


    def populateTransactionList_helperfunc(self, focus_node):
        """
        Helper function to populateTransactionList(), helper function's main purpose is multithreading.
        """
        txns = self.ethscan.get_ext_txns([focus_node])
        self.ethscan.split_txns_based_on_direction(txns)
        self.ethscan.update_statistics()
        self.homeparent.caseinfo["data"][SANITIZED_DATA][focus_node] = self.ethscan.ADDR_TXNS_SUMMARISED[focus_node]
        self.homeparent.caseinfo["data"][STATS][focus_node] = self.ethscan.ADDR_TXNS_STATS[focus_node]

        # If the focus node is still selected
        # if self.nodeListWidget.currentItem().text().split(' ')[0].lower() == focus_node:
            # Refresh the Transaction List view with newly filtered and sorted data
        print(f"Address: {focus_node} completed complilating.")

    def populateTransactionList(self):
        """
        Function to populate self.dataset based on currently selected filters (INCOMING/OUTGOING/ALL) and calls
        self.refreshView() to display the items accordingly
        :return: None
        """
        self.refreshView()

        # Get the data into local structure
        try:
            # Get the selected WOI (only one should be selected at any one time)
            focus_node = self.nodeListWidget.currentItem().text().split(' ')[0].lower()

            # Check if transaction data exists for current (focus) node, if no query API for it first
            if SANITIZED_DATA in self.homeparent.caseinfo["data"].keys():
                if focus_node not in self.homeparent.caseinfo["data"][SANITIZED_DATA].keys():
                    # Blocking displayMessage.
                    self.homeparent.displayMessage(f"Retrieving txns for address {focus_node.lower()}")

                    self.homeparent.caseinfo["data"][SANITIZED_DATA][focus_node] = {}

                    threading.Thread(target=self.populateTransactionList_helperfunc, args=([focus_node])).start()

                    return
                else:
                    # Retrieve the following filters / choices
                    # 1) Transaction Type (Outgoing/Incoming/All)
                    # 2) Time Range (Start/End datetime, inclusive)
                    trans_type = self.transactionTypePicker.currentText().lower()
                    start_datetime = int(self.timeStartPicker.dateTime().toSecsSinceEpoch())
                    end_datetime = int(self.timeEndPicker.dateTime().toSecsSinceEpoch())

                    # Set flag for filter the dataset if there exists user input in the transaction search filter
                    search_str = self.transactionFilterEdit.text().lower()

                    # Get focused dataset based on the specified transaction type and time range
                    if trans_type == ALL:
                        self.dataset = [x for x in self.homeparent.caseinfo["data"][SANITIZED_DATA][focus_node][INBOUND]
                                        if start_datetime <= int(x[TIMESTAMP]) <= end_datetime and search_str in x[FROM]] + \
                                       [x for x in self.homeparent.caseinfo["data"][SANITIZED_DATA][focus_node][OUTBOUND]
                                        if start_datetime <= int(x[TIMESTAMP]) <= end_datetime and search_str in x[TO]]
                    else:
                        target = FROM if trans_type == INBOUND else TO
                        self.dataset = [x for x in self.homeparent.caseinfo["data"][SANITIZED_DATA][focus_node][trans_type]
                                        if start_datetime <= int(x[TIMESTAMP]) <= end_datetime and search_str in x[target]]

                    # Count # of transactions (that has been time range filtered) by transaction address
                    self.group_transactions()

                    # Refresh the Transaction List view with newly filtered and sorted data
                    self.refreshView()
            else:
                # No SANITIZED field in dictionary, just return since no data at all
                return

        except AttributeError:
            # Add notification to user telling them to select a WOI (node)
            if self.loaded:
                self.homeparent.displayMessage("[-] No node (WOI) selected!")
        except RuntimeError:
            pass
        except TypeError:
            pass
        except KeyError:
            pass

    def refreshView(self):
        """
        Function to populate Transaction list view based on currently specified sorting choice
        :return: None
        """
        # Claer transaction list
        self.transactionListWidget.clear()

        # Get display order
        display_order = self.displayOrderPicker.currentText()
        reverse_flag = True if display_order == "Descending" else False

        # Sort the transactions by count
        self.sorted_addresses = sorted(self.transactions_by_address.items(),
                                              key=lambda item: item[1], reverse=reverse_flag)

        # Add the transactions into the Transaction list view in specified display order
        for [addr,count] in self.sorted_addresses:
            temp = QListWidgetItem()
            temp.setText(f"[{count}] {addr}")
            self.transactionListWidget.addItem(temp)

    def group_transactions(self):
        """
        Function to group transaction count by address into a dictionary, based on data in "self.dataset"
        :return: None
        """
        # Reset Transaction by address dictionary
        self.transactions_by_address = dict()

        # Loop through all transactions
        for x in self.dataset:
            # Get the direction for this transaction (is it a incoming/outgoing transaction)
            direction = FROM if x["direction"] == IN else TO
            # Init / add a counter for the specific address in the dictionary accordingly
            if x[f"{direction}"] not in self.transactions_by_address:
                self.transactions_by_address[x[f"{direction}"]] = 1
            else:
                self.transactions_by_address[x[f"{direction}"]] += 1

    def searchWOIAddresses(self):
        """
        Function to filter displayed WOIs by comparing user search string input
        with each WOI address in the Node List view (widget)
        :return: None
        """
        # Get current text in the "walletLineEdit" widget
        search_str = self.walletLineEdit.text()

        # Reset the list widget
        self.nodeListWidget.clear()

        # Add all WOI into the list
        for wallet in self.wallets_of_interest:
            if re.search(search_str, wallet):
                temp = QListWidgetItem()
                # Set Alias at end of WOI address if it exists
                if wallet in self.homeparent.caseinfo["aliases"].keys():
                    temp.setText(wallet + f" [{self.homeparent.caseinfo['aliases'][wallet]}]")
                else:
                    temp.setText(wallet)
                # Set tooltip (hover) over each WOI entry as the total transactions it has (incoming+outgoing)
                if wallet in self.homeparent.caseinfo["data"][STATS].keys():
                    temp.setToolTip(
                        f"Total Transactions: {self.homeparent.caseinfo['data'][STATS][wallet][TOTAL_TXNS]}")
                else:
                    temp.setToolTip(f"Total Transactions: [NO DATA]")
                self.nodeListWidget.addItem(temp)

    def initDashboardDefaultValues(self):
        """
        Function to initialize default values for different UI elements (e.g. placeholder texts)
        :return: None
        """
        # Init dashboard window title
        self.setWindowTitle("Digifax - " + self.homeparent.caseinfo["filename"])

        # Set Placeholder text for "walletLineEdit"
        self.walletLineEdit.setPlaceholderText("Node address")
        # Adjust default font size of "walletLineEdit"
        # self.walletLineEdit.setFont(QFont("Arial", 12))

        # Set Placeholder text for "transactionFilterEdit"
        self.transactionFilterEdit.setPlaceholderText("Search for transaction...")
        # Adjust default font size of "transactionFilterEdit"
        # self.transactionFilterEdit.setFont(QFont("Arial", 12))

        # Set Min,Max Datetimes for "timeStartPicker" & "timeEndPicker"
        currentDateTime = QDateTime.currentDateTime()
        self.timeStartPicker.setDateTimeRange(self.timeStartPicker.dateTime(), currentDateTime)
        self.timeEndPicker.setDateTimeRange(self.timeEndPicker.dateTime(), currentDateTime)

        # Set Default Datetime for "timeEndPicker" to current dateTime
        self.timeEndPicker.setDateTime(currentDateTime)

    def setupEvents(self):
        """
        Function to do all the connection of events / signal handlers
        :return: None
        """
        # WOI Search String Filter (Text Edited Event)
        self.walletLineEdit.textEdited.connect(self.searchWOIAddresses)

        # View Transactions of selected WOI (On-Click Event)
        self.addNodeBtn.clicked.connect(self.addNodeBtnHandler)

        # Open WOI profile (ListWidgetItem Double Clicked Event)
        self.nodeListWidget.itemClicked.connect(self.copyToClipboard)
        self.nodeListWidget.itemDoubleClicked.connect(self.openWOIProfile)

        # Display Order Filter (Selection Changed Event)
        self.displayOrderPicker.activated.connect(self.refreshView)

        # Transaction Type Filter (Selection Changed Event)
        self.transactionTypePicker.activated.connect(self.filter)

        # Transaction Search String Filter (Text Edited Event)
        self.transactionFilterEdit.textEdited.connect(self.filter)

        # Date Time Picker Changed ( Event)
        self.timeStartPicker.dateTimeChanged.connect(self.filter)
        self.timeEndPicker.dateTimeChanged.connect(self.filter)

        # View transactions with selected Unique wallet address under current filter conditions
        self.transactionListWidget.itemClicked.connect(self.clipTransaction)
        self.transactionListWidget.itemDoubleClicked.connect(self.openTransactions)

        # Add / Drop Relationship (On-Click Event)
        self.addRelationshipBtn.clicked.connect(self.addRelationship)
        self.dropRelationshipBtn.clicked.connect(self.dropRelationship)

        # Drop Node (On-Click Event)
        self.dropNodeBtn.clicked.connect(self.dropNodeBtnHandler)

        # Menubar Events
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionSave.setShortcut("Ctrl+S")
        self.actionHelp.setShortcut("Ctrl+I")
        self.actionClose.setShortcut("Ctrl+D")
        self.actionOpen.triggered.connect(self.open)
        self.actionSave.triggered.connect(self.save)
        self.actionSave_As.triggered.connect(self.saveAs)
        self.actionHelp.triggered.connect(self.help)
        self.actionClose.triggered.connect(self.closeDashboard)

    def loadPage(self, pagename):
        """
        Function to render a given .html page onto the QWebEngineView widget
        :param pagename: A string representation of a target webpage (.html) to render
        :return: None
        """
        try:
            with open(pagename, 'r') as f:
                html = f.read()
            self.wev.setHtml(html)
        except RuntimeError:
            pass

    def filter(self):
        """
        Function to handle any change in filter specified by user (transaction type, time range, search query)
        :return: None
        """
        # Clear the transaction list
        self.transactionListWidget.clear()

        # Repopulate the transaction list
        self.populateTransactionList()

    def clipTransaction(self):
        """
        Function to put highlighted transaction in Transaction List Widget into clipboard
        :return: None
        """
        copy(self.transactionListWidget.currentItem().text().split('] ')[1])

    def copyToClipboard(self):
        """
        Function to put highlighted WOI in Node List Widget into clipboard
        :return: None
        """
        copy(self.nodeListWidget.currentItem().text().split(' ')[0])
        self.populateTransactionList()

    def openWOIProfile(self):
        """
        Handler function for opening new window for displaying a selected WOI's profile
        :return: None
        """
        self.homeparent.openNodeProfileWindow(self.nodeListWidget.currentItem().text().split(' ')[0])

    def openTransactions(self):
        """
        Handler function for opening transaction window WRT to all transactions
        that current node has under specified filters
        :return: None
        """
        selected_txn_addr = self.transactionListWidget.currentItem().text().split("] ")[1].lower()
        txns = [txn for txn in self.dataset if selected_txn_addr in txn[FROM] or selected_txn_addr in txn[TO]]

        for txn in txns:
            to_labels = self.ethscan.get_addr_labels(txn["to"])
            from_labels = self.ethscan.get_addr_labels(txn["from"])
            txn["to_labels"] = to_labels
            txn["from_labels"] = from_labels

        self.homeparent.openTransactionWindow(txns)

    def open(self):
        """
        Handler Function to open another case
        :return: None
        """
        self.homeparent.openExistingCaseWindow()
        self.closeDashboard()

    def save(self):
        """
        Handler Function to save current work progress
        :return: None
        """
        self.homeparent.saveFile(self.wallets_of_interest, self.wallet_relationships)

    def saveAs(self):
        """
        Handler Function to save current work progress with a specific filename and location
        :return: None
        """
        self.homeparent.saveFileAs(self.wallets_of_interest, self.wallet_relationships)
        self.setWindowTitle("Digifax - " + self.homeparent.caseinfo["filename"])

    def help(self):
        """
        Handler Function to display help message box
        :return: None
        """
        self.homeparent.displayMessage("[OPEN ANOTHER CASE]\nCTRL+O\n\n[SAVE CURRENT CASE]\nCTRL+S\n\n[SHOW THIS TOOLTIP]\nCTRL+I\n\n[CLOSE DASHBOARD]\nCTRL+D")

    def closeDashboard(self):
        """
        Handler Function to close dashboard and go back to Home window
        :return: None
        """
        self.close()
        self.deleteLater()


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
