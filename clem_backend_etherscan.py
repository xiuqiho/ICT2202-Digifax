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
console = Console()
from rich.progress import Progress


def print_divider(message):
    console.rule(message, style="bold red")

def parse_message(message, tabs=0, symbol=None, symbol_style=None):
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


import time

TARGET_ADDR = "0xDa007777D86AC6d989cC9f79A73261b3fC5e0DA0".lower()
# TARGET_ADDR = "0x7129bED9a5264F0cF279110ECE27add9B6662bD5".lower()
# TARGET_ADDR = "0xddBd2B932c763bA5b1b7AE3B362eac3e8d40121A".lower()
ETHERSCAN_SITE = "https://etherscan.io/address/"
WEI = 0.000000000000000001  # 10e-19
SPACERS = "=" * 50

##### [!] All comments with [!] can be deleted after reading

# [!] Local dictionary for addrs : labels
LABELS = {}


# class DigiFax_EthScan:
#     def __init__(self):
#

def get_labels(target_addr):
    """This function returns the labels of a particular eth address based on etherscans page, returns a list"""

    # [!] Checks if the local LABELS have the target address, so as to not make unncessary calls to the web
    if target_addr in LABELS:
        return LABELS[target_addr]

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

    LABELS[target_addr] = filtered_res

    if filtered_res:
        # [!] Prints out the new labels
        # print_debug(f"{target_addr} -- {filtered_res}")
        return filtered_res
    else:
        return None


def get_txns_stats(api_obj, target_addr):
    """This function allows you to get the total number of txns of a wallet addr (incoming/outgoing)"""
    dict_full_txns = api_obj.get_normal_txs_by_address(target_addr, 0, 9999999999, 'age')
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
def get_ext_txns(api_obj, target_addr, direction="both"):
    """This function allow you to list all the incoming or outgoing txns of a wallet address
    Information extracted: timeStamp, blockNumber, labels, from, to, value"""

    list_full_txns = api_obj.get_normal_txs_by_address(target_addr, 0, 99999999, 'age')

    res = []
    expected_txn = 0

    len_all_txn, len_incoming_txn, len_outgoing_txn, len_contract_creation_txn = get_txns_stats(api_obj, target_addr)

    if direction == "both":
        expected_txn = len_all_txn
        print_info("Retrieving [bold cyan]all[/bold cyan] transactions")
    elif direction == "outgoing":
        expected_txn = len_outgoing_txn
        print_info("Retrieving [bold cyan]outgoing[/bold cyan] transactions")
    elif direction == "incoming":
        expected_txn = len_incoming_txn
        print_info("Retrieving [bold cyan]incoming[/bold cyan] transactions")

    # with console.status("[bold yellow]Compiling transactions...", spinner="aesthetic"):
    with Progress() as progress:
        task = progress.add_task("[yellow]Compiling transactions...", total=expected_txn)
        for txn in list_full_txns:
            progress.update(task, advance=1)
            # if to is empty, probably a contract creation txn
            if len(txn['to']) > 1:
                txn["to_labels"] = get_labels(txn["to"])
                txn["from_labels"] = get_labels(txn["from"])
                txn["value_in_eth"] = int(txn['value']) * WEI
                if direction == 'outgoing' or direction == "both":
                    if txn['from'] == target_addr:
                        txn["direction"] = "outgoing"
                        res.append(txn.copy())
                if direction == 'incoming' or direction == "both":
                    if txn['to'] == target_addr:
                        txn["direction"] = "outgoing"
                        res.append(txn.copy())

            if len(res) == expected_txn:
                break


    return {target_addr: res}


def main():
    api_obj = Etherscan(API_KEY)  # key in quotation marks

    num_of_eth = int(api_obj.get_eth_balance(TARGET_ADDR)) * WEI

    print_divider(f"{TARGET_ADDR}")
    print_info(f'Ethers: {num_of_eth}')

    total_txns, incoming, outgoing, contract_creation = get_txns_stats(api_obj, TARGET_ADDR)

    print_info(f'Number of Transactions: {total_txns}')
    print_info(f'Incoming: {incoming}', 1)
    print_info(f'Outgoing: {outgoing}', 1)
    print_info(f'Contract Creation: {contract_creation}', 1)
    print_info(f'Labels: {get_labels(TARGET_ADDR)}')

    res = get_ext_txns(api_obj, TARGET_ADDR, 'both')  # can use outgoing or incoming

    # pp.pprint(res)


if __name__ == "__main__":
    start = time.time()
    main()
    print_debug(f"Time elapsed: {time.time() - start}")
