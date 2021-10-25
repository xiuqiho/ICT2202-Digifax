"""
References:
https://github.com/pcko1/etherscan-python
https://etherscan.io/txs?a=0xddbd2b932c763ba5b1b7ae3b362eac3e8d40121a
"""

from etherscan import Etherscan
from secrets import API_KEY
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen  # Python 3

from concurrent.futures import ThreadPoolExecutor

import pprint

pp = pprint.PrettyPrinter(indent=4)

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn, FileSizeColumn, \
    TotalFileSizeColumn

progress = Progress(TextColumn("[bold blue]Compiling Transactions...", justify="right"), BarColumn(bar_width=None),
                    "[progress.percentage]{task.percentage:>3.1f}%", "•", TimeRemainingColumn(), "•",
                    TimeElapsedColumn(), FileSizeColumn(), TotalFileSizeColumn())

import time

# TARGET_ADDR = "0xDa007777D86AC6d989cC9f79A73261b3fC5e0DA0".lower()
TARGET_ADDR = "0x7129bED9a5264F0cF279110ECE27add9B6662bD5".lower()
# TARGET_ADDR = "0xddBd2B932c763bA5b1b7AE3B362eac3e8d40121A".lower()
ETHERSCAN_SITE = "https://etherscan.io/address/"
WEI = 0.000000000000000001  # 10e-19
SPACERS = "=" * 50


##### [!] All comments with [!] can be deleted after reading

class DigiFax_EthScan:
    def __init__(self):
        self.LABELS = {}
        self.ADDR_TXNS = {}
        self.ADDR_TXN_STATS = {}

        self.console = Console()
        self.EtherScanObj = Etherscan(API_KEY)  # key in quotation marks

    def get_balance(self, target_addr):
        return int(self.EtherScanObj.get_eth_balance(TARGET_ADDR)) * WEI

    def get_labels(self, target_addr):
        """This function returns the labels of a particular eth address based on etherscans page, returns a list"""

        # [!] Checks if the local LABELS have the target address, so as to not make unncessary calls to the web
        if target_addr in self.LABELS:
            return self.LABELS[target_addr]

        req = Request(ETHERSCAN_SITE + target_addr)
        req.add_header('User-Agent',
                       'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        req.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
        req.add_header('Accept-Encoding', 'none')
        req.add_header('Accept-Language', 'en-US,en;q=0.8')
        req.add_header('Connection', 'keep-alive')
        content = urlopen(req).read()
        soup = BeautifulSoup(content, "html.parser")
        res = soup.find_all('a', {'class': 'mb-1'})
        filtered_res = [elem.get_text() for elem in res]

        self.LABELS[target_addr] = filtered_res

        if filtered_res:
            # [!] Prints out the new labels
            # print_debug(f"{target_addr} -- {filtered_res}")
            return filtered_res
        else:
            return None

    def get_txns_stats(self, target_addr):
        """This function allows you to get the total number of txns of a wallet addr (incoming/outgoing)"""
        dict_full_txns = self.EtherScanObj.get_normal_txs_by_address(target_addr, 0, 9999999999, 'age')
        len_all_txn = len(dict_full_txns)
        len_incoming_txn = 0
        len_outgoing_txn = 0
        len_contract_creation_txn = 0

        # [!] Get the number of incoming and outgoing, can be shown in the "brief" description
        for txn in dict_full_txns:
            if len(txn['to']) > 1:
                if txn['from'] == target_addr:
                    len_outgoing_txn += 1
                elif txn['to'] == target_addr:
                    len_incoming_txn += 1
            else:
                len_contract_creation_txn += 1

        return len_all_txn, len_incoming_txn, len_outgoing_txn, len_contract_creation_txn

    # [!] Added the "both" option, which will include both incoming and outgoing directions
    def get_ext_txns(self, target_addr, direction="both"):
        """This function allow you to list all the incoming or outgoing txns of a wallet address
        Information extracted: timeStamp, blockNumber, hash, labels, from, to, value"""

        list_full_txns = self.EtherScanObj.get_normal_txs_by_address(target_addr, 0, 99999999, 'age')

        dict_indiv_txn = {}
        res = []
        expected_txn = 0

        len_all_txn, len_incoming_txn, len_outgoing_txn, len_contract_creation_txn = self.get_txns_stats(target_addr)

        if direction == "both":
            expected_txn = len_all_txn
            self.print_info("Retrieving [underline bold cyan]all[/] transactions")
        elif direction == "outgoing":
            expected_txn = len_outgoing_txn
            self.print_info("Retrieving [underline bold cyan]outgoing[/] transactions")
        elif direction == "incoming":
            expected_txn = len_incoming_txn
            self.print_info("Retrieving [underline bold cyan]incoming[/] transactions")

        task = progress.add_task("[yellow]Compiling transactions...", total=expected_txn)
        # progress.start_task(task)
        with progress:
            for count, txn in enumerate(list_full_txns):
                progress.update(task, advance=1)
                # if to is empty, probably a contract creation txn
                # print_debug(f"Start: {count}")
                if len(txn['to']) > 1:
                    # txn["to_labels"] = self.get_labels(txn["to"])
                    # txn["from_labels"] = self.get_labels(txn["from"])
                    txn["value_in_eth"] = int(txn['value']) * WEI

                    dict_indiv_txn = {
                        'timestamp': txn['timeStamp'],
                        'blockNumber': txn['blockNumber'],
                        'hash': txn['hash'],
                        'from': txn['from'],
                        'to': txn['to'],
                        'value': txn['value_in_eth']}

                    if direction == 'outgoing' or direction == "both":
                        if txn['from'] == target_addr:
                            txn["direction"] = "outgoing"
                            res.append(dict_indiv_txn.copy())
                    if direction == 'incoming' or direction == "both":
                        if txn['to'] == target_addr:
                            txn["direction"] = "outgoing"
                            res.append(dict_indiv_txn.copy())

                if len(res) == expected_txn:
                    break

        return {target_addr: res}
        # print()
        # print(res)

    def print_divider(self, message):
        self.console.rule(message, style="bold red")

    def parse_message(self, message, tabs=0, symbol=None, symbol_style=None):
        if not symbol:
            return "\t" * tabs + message
        if symbol_style:
            return "\t" * tabs + f"[{symbol_style}][{symbol}][/{symbol_style}] " + message
        return "\t" * tabs + f"[{symbol}] " + message

    def print_info(self, message, tabs=0, symbol="*"):
        message = self.parse_message(message, tabs, symbol)
        self.console.print(message, style="bold white")

    def print_debug(self, message, tabs=0):
        message = self.parse_message(message, tabs, symbol="*")
        self.console.print(message, style="bold yellow")


def main():
    digi = DigiFax_EthScan()

    num_of_eth = digi.get_balance(TARGET_ADDR)

    digi.print_divider(f"{TARGET_ADDR}")
    digi.print_info(f'Ethers: {num_of_eth}')

    total_txns, incoming, outgoing, contract_creation = digi.get_txns_stats(TARGET_ADDR)

    digi.print_info(f'Number of Transactions: {total_txns}')
    digi.print_info(f'Incoming: {incoming}', 1)
    digi.print_info(f'Outgoing: {outgoing}', 1)
    digi.print_info(f'Contract Creation: {contract_creation}', 1)
    digi.print_info(f'Labels: {digi.get_labels(TARGET_ADDR)}')

    res = digi.get_ext_txns(TARGET_ADDR, 'outgoing')  # can use outgoing or incoming

    pp.pprint('')
    pp.pprint(res)


if __name__ == "__main__":
    main()
