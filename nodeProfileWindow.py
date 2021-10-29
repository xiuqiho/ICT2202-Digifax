"""
Author:         Ho Xiu Qi

Date Completed: 28th Oct 2021
Last Updated:   29th Oct 2021

Description:
> GUI code for the ICT2202 Team Assignment "Digifax" Node Profile page (for editing aliases)

Aliases used:
> WOI = Wallet of Interest
"""

from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic                                   # Library to load
from constants import NPW_WIDTH, NPW_HEIGHT             # Constants for specifying window width/height


class NodeProfileWindow(QMainWindow):
    """
    Class definition for window that allows users to input custom information for creating a new case
    """
    def __init__(self, focusnode, parent=None):
        super(NodeProfileWindow, self).__init__(parent)
        # Keep a local copy of the parent object
        self.focusnode = focusnode
        self.homeparent = parent

        # Load the Home Window UI design from file
        uic.loadUi("./UI/nodeprofile.ui", self)
        self.setFixedSize(NPW_WIDTH, NPW_HEIGHT)
        self.setWindowTitle(f"Node Information")

        # Setup 'addr_label' to reflect full address of node (WOI)
        self.addr_label.setText(focusnode)

        # If exist, set the saved description as the text in 'desc_lineedit'
        if focusnode in self.homeparent.caseinfo["description"].keys():
            self.desc_lineedit.setText(self.homeparent.caseinfo["description"][focusnode])
        # Set placeholder text and focus on the 'desc_lineedit' UI element (widget)
        self.desc_lineedit.setPlaceholderText("Enter a description...")
        self.desc_lineedit.setFocus()

        # Create alias key in caseinfo["aliases"] dictionary if does not exist
        if focusnode in self.homeparent.caseinfo["aliases"].keys():
            self.alias_lineedit.setText(self.homeparent.caseinfo["aliases"][focusnode])

        # Set placeholder text on the 'alias_lineedit' UI element (widget)
        self.alias_lineedit.setPlaceholderText("Enter a alias...")

        # Connect buttons to on-click events
        self.saveAliasBtn.clicked.connect(self.saveProfileInfo)

        # Center the screen
        self.move(int(self.homeparent.db.resolution.width() / 2) - (NPW_WIDTH/2),
                  int(self.homeparent.db.resolution.height() / 2) - (NPW_HEIGHT/2))

    def saveProfileInfo(self):
        """
        Function to call HomeWindow parent's setter function (setNewCaseInfo) to
        save user input for creating new case
        :return: None
        """
        new_desc = self.desc_lineedit.text()
        new_alias = self.alias_lineedit.text()

        # If something was typed into the description field, save it
        if len(new_desc) > 0:
            self.homeparent.caseinfo["description"][self.focusnode] = new_desc
        # If something was typed into the alias field, save it
        if len(new_alias) > 0:
            self.homeparent.caseinfo["aliases"][self.focusnode] = new_alias

        # Signal to Home that changes have been made to update any necessary UI elements in the dashboard
        self.homeparent.signalProfileUpdated()

        # Close this node profile window
        self.close()

        # Delete this window
        self.deleteLater()
