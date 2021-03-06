"""
References:
https://github.com/pcko1/etherscan-python
https://etherscan.io/txs?a=0xddbd2b932c763ba5b1b7ae3b362eac3e8d40121a
"""
import json

from etherscan import Etherscan
# from secrets import API_KEY
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen  # Python 3
import socket
from multiprocessing import Process, Manager

import sys
import time
import pprint

pp = pprint.PrettyPrinter(indent=4)

from rich.console import Console

console = Console()

API_KEY = "1XCMJP7VNAXU1NVSKS4C7XBM1ET77SYNVE"

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


def print_impt(message, tabs=0, symbol="!"):
    message = parse_message(message, tabs, symbol)
    console.print(message, style="bold red")


def print_debug(message, tabs=0):
    message = parse_message(message, tabs, symbol="*")
    console.print(message, style="bold yellow")


ETHERSCAN_SITE = "https://etherscan.io/address/"
WEI = 0.000000000000000001  # 10e-19
SPACERS = "=" * 50
INCOMING_FLAG = 0
OUTGOING_FLAG = 1
BOTH_FLAG = 69
EXPORT_DATA_KEYWORD = "ADDR"


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

    def export_data(self) -> dict:
        print_impt("Exporting data..")

        all_data = {}

        for attrib in dir(self):
            if attrib and EXPORT_DATA_KEYWORD in attrib:
                # Only in python > 3.5
                all_data = {**{attrib: getattr(self, attrib)}, **all_data}
                print_info(
                    f"Merging attribute [bold yellow][{attrib}][/] ({sys.getsizeof(getattr(self, attrib))} bytes)")

        return all_data

    def get_addr_labels(self, target_addr):
        """This function returns the labels of a particular eth address based on etherscans page, returns a list"""

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

        try:
            content = urlopen(url=req, timeout=2).read()
        except socket.timeout:
            content = ""
            print_debug(f"Timeout for {target_addr}")

        soup = BeautifulSoup(content, "html.parser")
        res = soup.find_all('a', {'class': 'mb-1'})
        filtered_res = [elem.get_text() for elem in res]

        if not filtered_res:
            filtered_res = None
        else:
            try:
                filtered_res.remove("Decompile Bytecode")
            except ValueError:
                pass

        self.ADDR_LABELS[target_addr] = filtered_res

        return filtered_res


    def get_addr_stats(self, target_addr, list_full_txns):
        """This function allows you to get the statistics of txns of a wallet addr"""

        if target_addr in self.ADDR_TXNS_STATS:
            # * is used to unpack the values so it becomes a list
            return [*self.ADDR_TXNS_STATS[target_addr].values()]

        if not list_full_txns:
            len_all_txn = 0
            len_incoming_txn = 0
            len_outgoing_txn = 0
            len_contract_creation_txn = 0
        else:
            len_all_txn = len(list_full_txns)
            len_incoming_txn = 0
            len_outgoing_txn = 0
            len_contract_creation_txn = 0

            for txn in list_full_txns:
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

    def get_addr_txns(self, target_addr, progress_txn, progress_all_txn, return_txn, return_stat, direction=BOTH_FLAG) -> None:
        EtherScanObj = Etherscan(API_KEY)

        dict_indiv_txn = {}
        res = []
        expected_txn = 0
        progress_txn[target_addr] = 0
        list_full_txns = None

        try:
            list_full_txns = EtherScanObj.get_normal_txs_by_address(target_addr, 0, 9999999999, 'desc')
            # only when there are no errors, and transactions are successfully obtained, will the program proceed
        except AssertionError:
            print_info(f"{target_addr} does not have any transaction!")
            progress_all_txn[target_addr] = 0

        print_debug(f"Compiling expected transactions for address {target_addr.strip()}")

        len_all_txn, len_incoming_txn, len_outgoing_txn, len_contract_creation_txn = self.get_addr_stats(target_addr,
                                                                                                         list_full_txns)

        return_stat[target_addr] = {"all_txn": len_all_txn, "incoming_txn": len_incoming_txn,
                                    "outgoing_txn": len_outgoing_txn, "contract_txn": len_contract_creation_txn}

        if direction == BOTH_FLAG:
            expected_txn = len_all_txn - len_contract_creation_txn
        elif direction == OUTGOING_FLAG:
            expected_txn = len_outgoing_txn
        elif direction == INCOMING_FLAG:
            expected_txn = len_incoming_txn

        progress_all_txn[target_addr] = expected_txn


        print_debug(f"Compiling transactions for address {target_addr.strip()}, expecting {expected_txn} transactions. {len_incoming_txn} incoming, {len_outgoing_txn} outgoing")

        if list_full_txns:
            for i, txn in enumerate(list_full_txns):
                if len(txn['to']) > 1:
                    progress_txn[target_addr] = progress_txn[target_addr] + 1

                    dict_indiv_txn = {
                        'timestamp': txn['timeStamp'],
                        'blockNumber': txn['blockNumber'],
                        'hash': txn['hash'],
                        'from': txn['from'],
                        'from_labels': None,
                        'to': txn['to'],
                        'to_labels': None,
                        'value': int(txn['value']) * WEI}

                    if txn['from'] == target_addr:
                        dict_indiv_txn.update({"direction": OUTGOING_FLAG})
                    if txn['to'] == target_addr:
                        dict_indiv_txn.update({"direction": INCOMING_FLAG})

                    res.append(dict_indiv_txn.copy())

                if len(res) == expected_txn:
                    break

        return_txn[target_addr] = res

    def get_ext_txns(self, list_of_addr, direction=BOTH_FLAG) -> dict:
        """This function allow you to list all the incoming or outgoing txns of a wallet address
        Information extracted: timeStamp, blockNumber, hash, labels, from, to, value"""

        start = time.time()

        process_list = []
        addr_flag = {}

        # Initialise manager dictionary objects as a way of sharing data between processes
        manager = Manager()
        return_txn = manager.dict()
        return_stat = manager.dict()
        progress_txn = manager.dict()
        progress_all_txn = manager.dict()

        for addr in list_of_addr:

            addr_flag[addr] = 0

            if addr in self.ADDR_TXNS:
                print_info("Address already queried!")
                return_txn.update({addr : self.ADDR_TXNS[addr]})
                continue

            p = Process(target=self.get_addr_txns,
                        args=(addr.lower(), progress_txn, progress_all_txn, return_txn, return_stat, direction))
            p.start()
            process_list.append(p)

        while 1:
            time.sleep(1)
            for addr in list_of_addr:
                try:
                    print_info(f"{addr}: {progress_txn[addr]}/{progress_all_txn[addr]}")
                    if progress_txn[addr] == progress_all_txn[addr]:
                        addr_flag[addr] = 1
                except KeyError:
                    continue
            if all(addr_flag.values()):
                break

        for proc in process_list:
            proc.join()

        self.ADDR_TXNS.update(return_txn)
        self.ADDR_TXNS_STATS.update(return_stat)

        print_debug(f"{time.time() - start}s taken for [underline]{len(list_of_addr)}[/] addresses")

        return return_txn

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

        # print(f'{SPACERS}')

    def update_statistics(self):
        """This function will update self.ADDR_TXNS_STATS with unique incoming and outgoing txns for each addr"""
        # add uniq_incoming and uniq_outgoing to self.ADDR_TXNS_STATS[target_addr] using self.ADDR_TXNS_SUMMARISED
        # print(SPACERS)

        for k, v in self.ADDR_TXNS_SUMMARISED.items():
            self.ADDR_TXNS_STATS[k]['incoming_uniq'] = []
            self.ADDR_TXNS_STATS[k]['outgoing_uniq'] = []
            self.ADDR_TXNS_STATS[k]['incoming_uniq_data'] = {}
            self.ADDR_TXNS_STATS[k]['outgoing_uniq_data'] = {}
            # print(self.ADDR_TXNS_SUMMARISED[k].get('outgoing')[0].get('to'))

            for dict_elem in self.ADDR_TXNS_SUMMARISED[k]['incoming']:
                self.ADDR_TXNS_STATS[k]['incoming_uniq'].append(dict_elem.get('from'))
            for dict_elem in self.ADDR_TXNS_SUMMARISED[k].get('outgoing'):
                self.ADDR_TXNS_STATS[k]['outgoing_uniq'].append(dict_elem.get('to'))

            for addr in self.ADDR_TXNS_STATS[k].get('incoming_uniq'):
                if addr not in self.ADDR_TXNS_STATS[k]['incoming_uniq_data']:
                    self.ADDR_TXNS_STATS[k]['incoming_uniq_data'][addr] = 1
                else:
                    self.ADDR_TXNS_STATS[k]['incoming_uniq_data'][addr] += 1
            self.ADDR_TXNS_STATS[k]['incoming_uniq'] = len(list(set(self.ADDR_TXNS_STATS[k].get('incoming_uniq'))))

            for addr in self.ADDR_TXNS_STATS[k].get('outgoing_uniq'):
                if addr not in self.ADDR_TXNS_STATS[k]['outgoing_uniq_data']:
                    self.ADDR_TXNS_STATS[k]['outgoing_uniq_data'][addr] = 1
                else:
                    self.ADDR_TXNS_STATS[k]['outgoing_uniq_data'][addr] += 1
            self.ADDR_TXNS_STATS[k]['outgoing_uniq'] = len(list(set(self.ADDR_TXNS_STATS[k].get('outgoing_uniq'))))

            # print(self.ADDR_TXNS_STATS[k])
            # print(SPACERS)

    def export_as_json(self, save_path):
        """
        Function to dump 'self.ADDR_TXNS_SUMMARISED' into a .json file
        :return: None
        """
        with open(save_path, 'w') as f:
            json.dump({"sanitized": self.ADDR_TXNS_SUMMARISED, "stats": self.ADDR_TXNS_STATS}, f)


def main():
    digi = DigiFax_EthScan()

    input_addr = ['0xbdb5829f5452Bd10bb569B5B9B54732001ab5ab9', '0xddBd2B932c763bA5b1b7AE3B362eac3e8d40121A',
                  '0x7129bED9a5264F0cF279110ECE27add9B6662bD5']

    # huge_txns : 0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE, 0xDa007777D86AC6d989cC9f79A73261b3fC5e0DA0

    for addr in input_addr:
        addr = addr.lower()

        # print_divider(f"{addr}")
        # print_info(f'Ethers: {digi.get_addr_balance(addr)}')
        #
        # total_txns, incoming, outgoing, contract_creation = digi.get_addr_stats(addr)
        #
        # print_info(f'Number of Transactions: {total_txns}')
        # print_info(f'Incoming: {incoming}', 1)
        # print_info(f'Outgoing: {outgoing}', 1)
        # print_info(f'Contract Creation: {contract_creation}', 1)
        # print_info(f'Labels: {digi.get_addr_labels(addr)}')

    res = digi.get_ext_txns(input_addr)  # can use outgoing or incoming

    # pp.pprint("")
    #
    digi.split_txns_based_on_direction(res)
    digi.update_statistics()

    pp.pprint(digi.ADDR_TXNS_SUMMARISED)
    # digi.export_as_json("../data.json")                   # function added by xiuqi: to export summarised data into .json file

    # pp.pprint(digi.ADDR_TXNS_STATS)

    # digi.export_data()

    # pp.pprint(digi.ADDR_TXNS)


if __name__ == "__main__":
    main()
