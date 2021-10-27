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
from PyQt5.QtGui import QFont, QPainter
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWebEngineWidgets import QWebEngineView     # Widget to display Pyvis HTML files
from PyQt5 import uic                                   # Library to load

from pyvis.network import Network                       # Core library for producing the transaction network graphs

from constants import *                                 # All constants used in the project
import random                                           # To randomly choose a node color
import re                                               # For Text Search filtering


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
                "walletaddresses": ["0x0ea288c16bd3a8265873c8d0754b9b2109b5b810", "0xbdb5829f5452Bd10bb569B5B9B54732001ab5ab9", "0xDa007777D86AC6d989cC9f79A73261b3fC5e0DA0", "0xbdb5829f5452Bd10bb569B5B9B54732001ab5ab9", "0xbdb5829f5452Bd10bb569B5B9B54733001ab5ab9", "0xbdb5829f5452Bd10bb569B5B4B54732001ab5ab9", "0xbdb5829f5452B510bb569B5B9B54732001ab5ab9", "0xbdb5829f5452Bd10bb569B5B6B54732001ab5ab9", "0xbdb5829f5752Bd10bb569B5B9B54732001ab5ab9", "0xbdb5829f5452Bd10bb569B5B9B547320018b5ab9", "0xbdb5829f5452Bd10bb569B599B54732001ab5ab9", "0xbdb5829f5452Bd10bb569B509B54732001ab5ab9", "0xbdb5829f5452Bd10bb569B5A9B54732001ab5ab9", "0xbdb5829f5452Bd10bb569B5B9B547320B1ab5ab9", "0xbdb5829f5452Bd10bbC69B5B9B54732001ab5ab9", "0xbdb5829f5452Bd10bb56DB5B9B54732001ab5ab9"],
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
        self.createGraph()
        self.populateGraph()
        # self.graph.show_buttons(filter_=True)

        # Call function to populate node (WOI) list view
        self.populateWoiList()

        # Call function to populate node (Transactions) list view
        self.populateTransactionList()

        # Initialize default values for dashboard
        self.initDashboardDefaultValues()

        # Setup on-click events
        self.setupEvents()

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
        self.walletLineEdit.setGeometry(int(self.resolution.width() * SCREEN_WIDTH * (WEBPANEL_WIDTH + 0.015 + FLABEL_WIDTH)),
                                        int(self.resolution.height() * SCREEN_HEIGHT * FEDIT_Y_OFFSET),
                                        int(self.resolution.width() * SCREEN_WIDTH * FEDIT_WIDTH),
                                        int(self.resolution.height() * SCREEN_HEIGHT * FEDIT_HEIGHT))

        # Set QPushButton (viewTransactionsBtn) position and size
        self.viewTransactionsBtn.setGeometry(int(self.resolution.width() * (1 - 0.133)),
                                             int(self.resolution.height() * SCREEN_HEIGHT * VTBTN_Y_OFFSET),
                                             int(self.resolution.width() * SCREEN_WIDTH * VTBTN_WIDTH),
                                             int(self.resolution.height() * SCREEN_HEIGHT * VTBTN_HEIGHT))

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

        # Set QPushButton (dropRelationshipBtn) position and size
        self.dropRelationshipBtn.setGeometry(int(self.resolution.width() * (1 - RS_BTN_SPACING * 0.1325)),
                                            int(self.resolution.height() * SCREEN_HEIGHT * RS_BTN_Y_OFFSET),
                                            int(self.resolution.width() * RS_BTN_WIDTH),
                                            int(self.resolution.height() * RS_BTN_HEIGHT))

        # Set QPushButton (addRelationshipBtn) position and size
        self.addRelationshipBtn.setGeometry(int(self.resolution.width() * (1 - 0.1325)),
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
        # Add all given nodes to the graph
        for wallet in self.wallets_of_interest:
            self.graph.add_node(wallet, wallet[:ADDR_DISPLAY_LIMIT], color=DEFAULT_COLORS[random.randint(0,3)])

        # Add all relationships (if any)
        for focus, relatives in self.wallet_relationships.items():
            for relative in relatives:
                self.graph.add_edge(focus, relative[ADDR], value=relative[WEIGHT])

        # Save the graph into a file
        self.graph.show("graph.html")
        self.loadPage('graph.html')

    def addNode(self, woi):
        """
        Function to add a specific address as a new node into the graph and backend structs
        :param woi: The wallet address that user wants to add to the graph as a node
        :return: None
        """
        if woi not in self.wallets_of_interest:
            # Append wallet to list of interested wallets
            self.wallets_of_interest.append(woi)
            # Add node to graph
            self.graph.add_node(woi, woi[:ADDR_DISPLAY_LIMIT], color=DEFAULT_COLORS[random.randint(0, 4)])

    def addNodeBtnHandler(self):
        """
        Function to handle '' button to add a new node and render the change on the graph
        :return: None
        """
        woi = "0x0000000000000000000000000000000000000001"
        self.addNode(woi)

        # Reload the graph
        self.graph.show("graph.html")
        self.loadPage('graph.html')

    def dropNode(self, woi):
        """
        Function to drop a specific address node from the graph.
        Doing so will also automatically delete all relationships the node has (if any)
        :param woi: The wallet node that user wants to drop from the graph
        :return: None
        """
        if woi not in self.wallets_of_interest:
            # Delete wallet from list of interested wallets
            self.wallets_of_interest.remove(woi)

            # Delete all wallet relationships
            del self.wallet_relationships[woi]

            # Remove all edges related to the node
            edges_to_drop = [edge for edge in self.graph.get_edges() if edge['from'] == woi or edge['to'] == woi]
            for edge in edges_to_drop:
                del self.graph.edges[self.graph.edges.index(edge)]

            # Remove the node
            self.graph.nodes.remove(self.graph.nodes.index(woi))

    def dropNodeBtnHandler(self):
        """
        Function to handle '' button to drop a existing node and render the change on the graph
        :return: None
        """
        woi = "0x0000000000000000000000000000000000000001"
        self.dropNode(woi)

        # Reload the graph
        self.graph.show("graph.html")
        self.loadPage('graph.html')

    def addRelationship(self):
        """
        Function to update (1) backend data structs and (2) graph WRT to adding a WOI
        :return: None
        """
        try:
            focusedWallet = self.nodeListWidget.currentItem().text()   # selected node
            woi = self.transactionListWidget.currentItem().text()      # selected transaction

            # Add node to graph and wallet_of_interest if necessary (node doesn't exist yet)
            self.addNode(woi)

            # Update WOI relationships
            if woi != focusedWallet and [woi, 2] not in self.wallet_relationships[focusedWallet]:  # Change [woi, 2] to [woi, # of transactions]
                # print(self.wallet_relationships[focusedWallet])
                self.wallet_relationships[focusedWallet].append([woi, 2])
                # print(self.wallet_relationships[focusedWallet])
                self.graph.add_edge(focusedWallet, woi, value=DEFAULT_WEIGHT)   # Change DEFAULT_WEIGHT to # of transactions

                # Reload the graph
                self.graph.show("graph.html")
                self.loadPage('graph.html')
        except AttributeError as err:
            # Add notification to user telling them to select a WOI (node)
            print(f"No woi selected!\n{err}")

    def dropRelationship(self):
        """
        Function to update (1) backend data structs and (2) graph WRT to removing a WOI
        :return: None
        """
        try:
            focusedWallet = self.nodeListWidget.currentItem().text()   # selected node
            woi = self.transactionListWidget.currentItem().text()      # selected transaction

            # Remove WOI relationship
            if woi != focusedWallet and [woi, 2] in self.wallet_relationships[focusedWallet]:  # Change [woi, 2] to [woi, # of transactions]
                del self.wallet_relationships[focusedWallet][self.wallet_relationships[focusedWallet].index([woi, 2])]
                try:
                    rs = [edge for edge in self.graph.get_edges() if edge['from'] == focusedWallet and edge['to'] == woi][0]
                    del self.graph.edges[self.graph.edges.index(rs)]
                except IndexError:
                    print(f"[!] Couldn't delete RS from '{focusedWallet}' to '{woi}'")
                    pass
                # Reload the graph
                self.graph.show("graph.html")
                self.loadPage('graph.html')
        except AttributeError as err:
            # Add notification to user telling them to select a WOI (node)
            print(f"No woi selected!\n{err}")

    def populateWoiList(self):
        """
        Function to populate WOI (nodes) list
        :return: None
        """
        # Reset the WOI list
        self.nodeListWidget.clear()

        # Add all WOI into the list
        for wallet in self.wallets_of_interest:
            temp = QListWidgetItem()
            temp.setText(wallet)
            # temp.setToolTip("Yo mum g@y")           # ** Change to total # of transactions once backend code integrated **
            self.nodeListWidget.addItem(temp)

        # Set default selection of node list to the first item
        # self.nodeListWidget.set

    def populateTransactionList(self):
        """
        Function to populate Transaction list view based on currently selected filters / sorting choice
        :return: None
        """
        # Check if transaction data exists for current node, if no query API for it first

        # Get the data into local structure
        try:
            # Get the selected WOI (only one should be selected at any one time)
            focus_node = self.nodeListWidget.currentItem().text()

            # Retrieve the following filters / choices
            # 1) Transaction Type (Outgoing/Incoming/All)
            # 2) Time Range (Start/End datetime, inclusive)
            trans_type = self.transactionTypePicker.currentText()
            start_datetime = self.timeStartPicker.dateTime().toSecsSinceEpoch()
            end_datetime = self.timeEndPicker.dateTime().toSecsSinceEpoch()

            # Get focused dataset based on the specified transaction type and time range
            self.dataset = [x for x in self.caseinfo["data"][focus_node][trans_type]
                            if start_datetime <= x["timestamp"] <= end_datetime]

            # Sort them into unique addresses
            self.group_transactions()

            # Refresh the Transaction List view with newly filtered and sorted data
            self.refreshView()

        except AttributeError as err:
            # Add notification to user telling them to select a WOI (node)
            print(f"No woi selected!\n{err}")

    def group_transactions(self):
        """
        Function to group transaction count by address into a dictionary, based on data in "self.dataset"
        :return: None
        """
        # Check if there is data to work with in the first place
        if len(self.dataset) <= 0:
            return

        # Loop through all transactions
        for x in self.dataset:
            # Get the direction for this transaction (is it a incoming/outgoing transaction)
            direction = "from" if self.dataset[0]["direction"] == INBOUND else "to"

            # Init / add a counter for the specific address in the dictionary accordingly
            if x[f"{direction}"] not in self.transactions_by_address:
                self.transactions_by_address[x[f"{direction}"]] = 1
            else:
                self.transactions_by_address[x[f"{direction}"]] += 1

    def refreshView(self):
        """
        Function to populate Transaction list view based on currently specified sorting choice
        :return: None
        """
        # Get display order
        display_order = self.displayOrderPicker.currentText()
        reverse_flag = False if display_order == "Descending" else True

        # Sort the transactions by count
            # Instead of manual sorting, try QListWidget::sortItems(order)
            # > https://doc.qt.io/qt-5/qlistwidget.html#sortItems
        self.sorted_addresses = sorted(self.transactions_by_address.items(),
                                              key=lambda item: item[1], reverse=reverse_flag)

        # Reset the Transaction list
        self.transactionListWidget.clear()

        # Add the transactions into the Transaction list view in specified display order
        for [addr,count] in self.sorted_addresses:
            temp = QListWidgetItem()
            temp.setText(f"[{count}] {addr}")
            self.transactionListWidget.addItem(temp)

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

        # Add items into Node ListWidget if they contain 'search_str' as a sub-string
        for woi in self.wallets_of_interest:
            if re.search(search_str, woi):
                temp = QListWidgetItem()
                temp.setText(f"{woi}")
                self.nodeListWidget.addItem(temp)

    def searchTransactionAddresses(self):
        """
        Function to filter displayed Transactions by comparing user search string input
        with each transaction address in the Transaction List view (widget)
        :return: None
        """
        # Get current text in the "transactionFilterEdit" widget
        search_str = self.transactionFilterEdit.text()

        # Reset the list widget
        self.transactionListWidget.clear()

        # Iterate through each QListWidgetItem in "transactionListWidget"
        for [addr,count] in self.sorted_addresses:
            if re.search(search_str, addr):
                temp = QListWidgetItem()
                temp.setText(f"[{count}] {addr}")
                self.transactionListWidget.addItem(temp)

    def initDashboardDefaultValues(self):
        """
        Function to initialize default values for different UI elements (e.g. placeholder texts)
        :return: None
        """
        # Set Placeholder text for "walletLineEdit"
        self.walletLineEdit.setPlaceholderText("Search for node...")
        # Adjust default font size of "walletLineEdit"
        self.walletLineEdit.setFont(QFont("Arial", 12))

        # Set Placeholder text for "transactionFilterEdit"
        self.transactionFilterEdit.setPlaceholderText("Search for transaction...")
        # Adjust default font size of "transactionFilterEdit"
        self.transactionFilterEdit.setFont(QFont("Arial", 12))

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

        # Open WOI profile (ListWidgetItem Double Clicked Event)
        self.nodeListWidget.itemDoubleClicked.connect(self.openWOIProfile)

        # Display Order Filter (Selection Changed Event)
        self.displayOrderPicker.activated.connect(self.refreshView)

        # Transaction Type Filter (Selection Changed Event)
        self.transactionTypePicker.activated.connect(self.populateTransactionList)

        # Transaction Search String Filter (Text Edited Event)
        self.transactionFilterEdit.textEdited.connect(self.searchTransactionAddresses)

        # Add / Drop Relationship (On-Click Event)
        self.addRelationshipBtn.clicked.connect(self.addRelationship)
        self.dropRelationshipBtn.clicked.connect(self.dropRelationship)

    def loadPage(self, pagename):
        """
        Function to render a given .html page onto the QWebEngineView widget
        :param pagename: A string representation of a target webpage (.html) to render
        :return: None
        """
        with open(pagename, 'r') as f:
            html = f.read()
        self.wev.setHtml(html)

    def openWOIProfile(self):
        """
        Handler function for opening new window for displaying a selected WOI's profile
        :return: None
        """
        print(self.nodeListWidget.currentItem().text())


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
