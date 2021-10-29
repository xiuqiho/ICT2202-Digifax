from PyQt5.QtWidgets import *
from PyQt5 import uic
import time
import datetime
import webbrowser

data = [{ 'blockNumber': '6141243',
          'direction': 0,
          'from': '0x7ed2d423ba4bc317e45561caa823b7d6cc2024a9',
          'from_labels': None,
          'hash': '0x1a99ef8d9ae7087e276451d460f9b100a3c667d07c69a4b95bcd0296132e5738',
          'timestamp': '1534182274',
          'to': '0x7129bed9a5264f0cf279110ece27add9b6662bd5',
          'to_labels': None,
          'value': 26.10836602777778},
      {   'blockNumber': '6141279',
          'direction': 0,
          'from': '0x3e70910bfa2bbe5b64b39adc240d9ac13dcc1ab1',
          'from_labels': None,
          'hash': '0x7173e771c8db53ee44f837816b5edee38dde4470f2a1d8866e34e718c8fc7260',
          'timestamp': '1534182703',
          'to': '0x7129bed9a5264f0cf279110ece27add9b6662bd5',
          'to_labels': None,
          'value': 203.13047668000002},
      {   'blockNumber': '6446337',
          'direction': 0,
          'from': '0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0',
          'from_labels': [   'Kraken',
                             'Exchange'],
          'hash': '0x0ac064fda91e430dc789c7b197ceee5a8717a23150aa2d8ac23f2b2b63d75637',
          'timestamp': '1538579235',
          'to': '0x7129bed9a5264f0cf279110ece27add9b6662bd5',
          'to_labels': [   'Kraken',
                           'Exchange'],
          'value': 1.91473},
      {   'blockNumber': '6751965',
          'direction': 0,
          'from': '0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0',
          'from_labels': [   'Kraken',
                             'Exchange'],
          'hash': '0x68011de3f2f6dab7f290978d82ee2c28bd0da5741f3025ac81915085bc7b0b58',
          'timestamp': '1542894315',
          'to': '0x7129bed9a5264f0cf279110ece27add9b6662bd5',
          'to_labels': [   'Kraken',
                           'Exchange'],
          'value': 10.25},
      {   'blockNumber': '7109646',
          'direction': 0,
          'from': '0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0',
          'from_labels': [   'Kraken',
                             'Exchange'],
          'hash': '0xeb1af147c78a34b4ba56a04b0411612bb21394d62a8bdec1336f70f2b589107e',
          'timestamp': '1548174424',
          'to': '0x7129bed9a5264f0cf279110ece27add9b6662bd5',
          'to_labels': [   'Kraken',
                           'Exchange'],
          'value': 1.95419},
      {   'blockNumber': '7643993',
          'direction': 0,
          'from': '0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0',
          'from_labels': [   'Kraken',
                             'Exchange'],
          'hash': '0x7c089ec2bb4127ba0819a3572d7e3ad394ecd5929ac48c6fb2118a9f83e5e0de',
          'timestamp': '1556294865',
          'to': '0x7129bed9a5264f0cf279110ece27add9b6662bd5',
          'to_labels': [   'Kraken',
                           'Exchange'],
          'value': 2.51499},
      {   'blockNumber': '7815511',
          'direction': 0,
          'from': '0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0',
          'from_labels': [   'Kraken',
                             'Exchange'],
          'hash': '0x204cb756f858eed349188606f7b9c8ea452a04090aa1ed1483475acc0726bceb',
          'timestamp': '1558608412',
          'to': '0x7129bed9a5264f0cf279110ece27add9b6662bd5',
          'to_labels': [   'Kraken',
                           'Exchange'],
          'value': 0.22894},
      {   'blockNumber': '8419882',
          'direction': 0,
          'from': '0xfbb1b73c4f0bda4f67dca266ce6ef42f520fbb98',
          'from_labels': [   'Bittrex',
                             'Exchange'],
          'hash': '0xd8dc68f1214eb302ad9275da1dad36af33322fc6cfa831f99f70899329c220ba',
          'timestamp': '1566743374',
          'to': '0x7129bed9a5264f0cf279110ece27add9b6662bd5',
          'to_labels': [   'Bittrex',
                           'Exchange'],
          'value': 5.23624051},
      {   'blockNumber': '8420482',
          'direction': 0,
          'from': '0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0',
          'from_labels': [   'Kraken',
                             'Exchange'],
          'hash': '0x0071993003079d74c036164ecc0f66f375f5908729a502d754622391ccd91cb2',
          'timestamp': '1566751182',
          'to': '0x7129bed9a5264f0cf279110ece27add9b6662bd5',
          'to_labels': [   'Kraken',
                           'Exchange'],
          'value': 7.158110000000001}]


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

        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)

        self.setFixedSize(self.width(), self.height())
        self.loadData(data)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.setSortingEnabled(True)

        self.websiteButton.clicked.connect(self.openSite)

    def openSite(self):
        txn_hash_column = 8
        selected_rows = []
        for index in self.tableWidget.selectedIndexes():
            selected_rows.append(index.row())

        for row in set(selected_rows):
            txn_hash = self.tableWidget.item(row, txn_hash_column).text()
            webbrowser.open(f"https://etherscan.io/tx/{txn_hash}")

    def loadData(self, data):
        self.tableWidget.setRowCount(len(data))

        row = 0

        datetime_column = 0
        from_column = 1
        from_label_column = 2
        to_column = 3
        to_label_column = 4
        direction_column = 5
        value_column = 6
        blocknumber_column = 7
        txn_hash_column = 8

        # Used for combining elements of list of labels into a string
        from_label_str = ""
        to_label_str = ""

        for row, x in enumerate(data):

            # Set local timezone for date column
            self.tableWidget.setHorizontalHeaderLabels([f"Datetime (YYYY/MM/DD)"])

            # Set data for column -> datetime
            converted_datetime = datetime.datetime.utcfromtimestamp(int(x["timestamp"])).strftime('%Y/%m/%d %H:%M:%S')
            self.tableWidget.setItem(row, datetime_column, QTableWidgetItem(converted_datetime))

            # Set data for column -> from
            self.tableWidget.setItem(row, from_column, QTableWidgetItem(x["from"]))

            # Set data for column -> from labels
            if x["from_labels"]:
                if len(x["from_labels"]) > 1:
                    from_label_str = ",".join(x["from_labels"])
                    self.tableWidget.setItem(row, from_label_column, QTableWidgetItem(from_label_str))
                else:
                    self.tableWidget.setItem(row, to_label_column, QTableWidgetItem(x["from_labels"]))
            else:
                self.tableWidget.setItem(row, from_label_column, QTableWidgetItem("None"))

            # Set data for column -> to
            self.tableWidget.setItem(row, to_column, QTableWidgetItem(x["to"]))

            # Set data for column -> to labels
            if x["to_labels"]:
                if len(x["to_labels"]) > 1:
                    to_label_str = ",".join(x["to_labels"])
                    self.tableWidget.setItem(row, to_label_column, QTableWidgetItem(to_label_str))
                else:
                    self.tableWidget.setItem(row, to_label_column, QTableWidgetItem(x["to_labels"]))
            else:
                self.tableWidget.setItem(row, to_label_column, QTableWidgetItem("None"))

            # Set data for column -> direction
            if x["direction"] == 0:
                self.tableWidget.setItem(row, direction_column, QTableWidgetItem("Incoming"))
            else:
                self.tableWidget.setItem(row, direction_column, QTableWidgetItem("Outgoing"))

            # Set data for column -> value
            self.tableWidget.setItem(row, value_column, QTableWidgetItem(str(x["value"])))

            # Set data for column -> blockNumber
            self.tableWidget.setItem(row, blocknumber_column, QTableWidgetItem(x["blockNumber"]))

            # Set data for column -> hash
            self.tableWidget.setItem(row, txn_hash_column, QTableWidgetItem(x["hash"]))


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
