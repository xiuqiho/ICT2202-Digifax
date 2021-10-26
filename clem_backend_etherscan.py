"""
References:
https://github.com/pcko1/etherscan-python
https://etherscan.io/txs?a=0xddbd2b932c763ba5b1b7ae3b362eac3e8d40121a
"""

from etherscan import Etherscan
from secrets import API_KEY
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen  # Python 3

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import time
import pprint

pp = pprint.PrettyPrinter(indent=4)

from rich.console import Console

console = Console()
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, FileSizeColumn, \
    TotalFileSizeColumn

progress = Progress(TextColumn("[bold blue]{task.fields[filename]}", justify="right"), BarColumn(bar_width=None),
                    "[progress.percentage]{task.percentage:>3.1f}%", "•", TimeRemainingColumn(), FileSizeColumn(),
                    TotalFileSizeColumn())


def print_divider(message):
    console.rule(f"[bold red][*][/] {message}", style="bold red", align="left")


def parse_message(message, tabs=0, symbol=None, symbol_style=None):
    message = str(message)
    if not symbol:
        return "\t" * tabs + message
    if symbol_style:
        return "\t" * tabs + f"[{symbol_style}][{symbol}][/{symbol_style}] " + message
    return "\t" * tabs + f"[{symbol}] " + message


def print_info(message, tabs=0, symbol="*"):
    message = parse_message(message, tabs, symbol)
    console.print(message, style="bold white")


def print_debug(message, tabs=0):
    message = parse_message(message, tabs, symbol="*")
    console.print(message, style="bold yellow")


ETHERSCAN_SITE = "https://etherscan.io/address/"
WEI = 0.000000000000000001  # 10e-19
SPACERS = "=" * 50
INCOMING_FLAG = 0
OUTGOING_FLAG = 1
BOTH_FLAG = 69


class DigiFax_EthScan:
    def __init__(self):

        # Consist of all labels for addresses
        self.ADDR_LABELS = {}

        # Consist of all transactions for all input addresses
        self.ADDR_TXNS = {}

        # Consist of unique transactions for all input addresses
        self.ADDR_TXNS_SUMMARISED = {}

        # Consist of all input address transaction statistics
        self.ADDR_TXNS_STATS = {}

        self.EtherScanObj = Etherscan(API_KEY)  # key in quotation marks

    def get_addr_balance(self, target_addr) -> int:
        """Returns the balance of a particular address in Ether"""
        return int(self.EtherScanObj.get_eth_balance(target_addr)) * WEI

    def get_addr_labels(self, target_addr):
        """This function returns the labels of a particular eth address based on etherscans page, returns a list"""

        # [!] Checks if the local ADDR_LABELS has the target address, so as to not make unncessary calls to the web
        if target_addr in self.ADDR_LABELS:
            return self.ADDR_LABELS[target_addr]

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
        if not filtered_res:
            filtered_res = None

        self.ADDR_LABELS[target_addr] = filtered_res

        return filtered_res

    def get_addr_stats(self, target_addr):
        """This function allows you to get the statistics of txns of a wallet addr"""

        # [!] Checks if the local ADDR_TXNS_STATS have the target address, so as to not make unncessary processing
        if target_addr in self.ADDR_TXNS_STATS:
            # * is used to unpack the values so it becomes a list
            return [*self.ADDR_TXNS_STATS[target_addr].values()]

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

        self.ADDR_TXNS_STATS[target_addr] = {"all_txn": len_all_txn,
                                             "incoming_txn": len_incoming_txn,
                                             "outgoing_txn": len_outgoing_txn,
                                             "contract_txn": len_contract_creation_txn}

        return [len_all_txn, len_incoming_txn, len_outgoing_txn, len_contract_creation_txn]

    def get_addr_txns(self, task_id, target_addr, direction=OUTGOING_FLAG) -> dict:
        list_full_txns = self.EtherScanObj.get_normal_txs_by_address(target_addr, 0, 99999999, 'desc')

        dict_indiv_txn = {}
        res = []
        expected_txn = 0

        len_all_txn, len_incoming_txn, len_outgoing_txn, len_contract_creation_txn = self.get_addr_stats(target_addr)

        if direction == BOTH_FLAG:
            expected_txn = len_all_txn - len_contract_creation_txn
        elif direction == OUTGOING_FLAG:
            expected_txn = len_outgoing_txn
        elif direction == INCOMING_FLAG:
            expected_txn = len_incoming_txn

        progress.update(task_id, total=expected_txn)
        progress.start_task(task_id)

        for txn in list_full_txns:
            # if to is empty, probably a contract creation txn
            if len(txn['to']) > 1:
                dict_indiv_txn = {
                    'timestamp': txn['timeStamp'],
                    'blockNumber': txn['blockNumber'],
                    'hash': txn['hash'],
                    'from': txn['from'],
                    'from_labels': self.get_addr_labels(txn["from"]),
                    'to': txn['to'],
                    'to_labels': self.get_addr_labels(txn["to"]),
                    'value': int(txn['value']) * WEI}

                if txn['from'] == target_addr:
                    dict_indiv_txn.update({"direction": OUTGOING_FLAG})
                    res.append(dict_indiv_txn.copy())
                    progress.update(task_id, advance=1)
                if txn['to'] == target_addr:
                    dict_indiv_txn.update({"direction": INCOMING_FLAG})
                    res.append(dict_indiv_txn.copy())
                    progress.update(task_id, advance=1)

                ## BUGGY COS OF THE BOTH_FLAG
                # if direction == OUTGOING_FLAG or direction == BOTH_FLAG:
                #     if txn['from'] == target_addr:
                #         dict_indiv_txn.update({"direction": OUTGOING_FLAG})
                #         res.append(dict_indiv_txn.copy())
                #         progress.update(task_id, advance=1)
                # if direction == INCOMING_FLAG or direction == BOTH_FLAG:
                #     if txn['to'] == target_addr:
                #         dict_indiv_txn.update({"direction": INCOMING_FLAG})
                #         res.append(dict_indiv_txn.copy())
                #         progress.update(task_id, advance=1)
                ## /BUGGY COS OF THE BOTH_FLAG

            if len(res) == expected_txn:
                break

        self.ADDR_TXNS[target_addr] = res

        return {target_addr: res}

    # [!] Added the "both" option, which will include both incoming and outgoing directions
    def get_ext_txns(self, list_of_addr, direction=OUTGOING_FLAG) -> dict:
        """This function allow you to list all the incoming or outgoing txns of a wallet address
        Information extracted: timeStamp, blockNumber, hash, labels, from, to, value"""

        process_list = []
        res = {}

        with progress:
            with ThreadPoolExecutor() as executor:
                for addr in list_of_addr:
                    task_id = progress.add_task(f"Compiling {addr} transactions...", filename=addr, start=False)
                    process_list.append(executor.submit(self.get_addr_txns, task_id, addr.lower(), direction))

                for _ in as_completed(process_list):
                    res.update(_.result())

        return res

    def split_txns_based_on_direction(self, dict_all_txn):
        """This function will split the txns into unique incoming or outgoing txns"""
        for k, v in dict_all_txn.items():

            if k not in self.ADDR_TXNS_SUMMARISED:
                self.ADDR_TXNS_SUMMARISED[k] = {'outgoing': [], 'incoming': []}

            for indiv_txn in v:
                if indiv_txn['direction'] == OUTGOING_FLAG:
                    self.ADDR_TXNS_SUMMARISED[k]['outgoing'].append(indiv_txn)
                if indiv_txn['direction'] == INCOMING_FLAG:
                    self.ADDR_TXNS_SUMMARISED[k]['incoming'].append(indiv_txn)

        print(f'{SPACERS}')

    def update_statistics(self):
        """This function will update self.ADDR_TXNS_STATS with unique incoming and outgoing txns for each addr"""
        # add uniq_incoming and uniq_outgoing to self.ADDR_TXNS_STATS[target_addr] using self.ADDR_TXNS_SUMMARISED
        pass


def main():
    digi = DigiFax_EthScan()

    p = ["0x0Ea288c16bd3A8265873C8D0754B9b2109b5B810", "0xbdb5829f5452Bd10bb569B5B9B54732001ab5ab9",
         "0xc084350789944A2A1af3c39b32937dcdd2AD2748", "0xddBd2B932c763bA5b1b7AE3B362eac3e8d40121A",
         "0x7129bED9a5264F0cF279110ECE27add9B6662bD5"]
    # 0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE (17m), 0xDa007777D86AC6d989cC9f79A73261b3fC5e0DA0 (5.3k)
    for addr in p:
        addr = addr.lower()

        print_divider(f"{addr}")
        print_info(f'Ethers: {digi.get_addr_balance(addr)}')

        total_txns, incoming, outgoing, contract_creation = digi.get_addr_stats(addr)

        print_info(f'Number of Transactions: {total_txns}')
        print_info(f'Incoming: {incoming}', 1)
        print_info(f'Outgoing: {outgoing}', 1)
        print_info(f'Contract Creation: {contract_creation}', 1)
        print_info(f'Labels: {digi.get_addr_labels(addr)}')

    res = digi.get_ext_txns(p)  # can use outgoing or incoming

    pp.pprint("")
    digi.split_txns_based_on_direction(res)
    digi.update_statistics()
    pp.pprint(digi.ADDR_TXNS_SUMMARISED)

    # pp.pprint(digi.ADDR_TXNS)

    # for i in digi.ADDR_TXNS:
    #     print_info(f"{i} - {len(digi.ADDR_TXNS[i])} incoming/outgoing txns")

    # for addr in res:
    #     print_info(f"{addr} - {len(res[addr])} ")


if __name__ == "__main__":
    main()
