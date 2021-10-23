"""
References:
https://github.com/pcko1/etherscan-python
https://etherscan.io/txs?a=0xddbd2b932c763ba5b1b7ae3b362eac3e8d40121a
"""

from etherscan import Etherscan
from secrets import API_KEY
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen  # Python 3

# TARGET_ADDR = "0xDa007777D86AC6d989cC9f79A73261b3fC5e0DA0".lower()
TARGET_ADDR = "0x7129bED9a5264F0cF279110ECE27add9B6662bD5".lower()
# TARGET_ADDR = "0xddBd2B932c763bA5b1b7AE3B362eac3e8d40121A".lower()
ETHERSCAN_SITE = "https://etherscan.io/address/"
WEI = 0.000000000000000001  # 10e-19
SPACERS = "=" * 50


def get_labels(target_addr):
    """This function returns the labels of a particular eth address based on etherscans page, returns a list"""
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
    if filtered_res:
        return filtered_res
    else:
        return ['NIL']


def get_total_txns(api_obj, target_addr):
    """This function allows you to get the total number of txns of a wallet addr (incoming/outgoing)"""
    dict_full_txns = api_obj.get_normal_txs_by_address(target_addr, 0, 9999999999, 'age')
    return len(dict_full_txns)


def get_ext_txns(api_obj, target_addr, direction):
    """This function allow you to list all the incoming or outgoing txns of a wallet address
    Information extracted: timeStamp, blockNumber, labels, from, to, value"""
    list_full_txns = api_obj.get_normal_txs_by_address(target_addr, 0, 99999999, 'age')
    res = []
    for txn in list_full_txns:
        # if to is empty, probably a contract creation txn
        if len(txn['to']) > 1:
            if direction == 'outgoing':
                if txn['from'] == target_addr:
                    res.append([
                        f"{txn['timeStamp']}, {txn['blockNumber']}, {get_labels(txn['to'])}, {txn['from']}, {txn['to']}, {int(txn['value']) * WEI}"])
            if direction == 'incoming':
                if txn['to'] == target_addr:
                    res.append([
                        f"{txn['timeStamp']}, {txn['blockNumber']}, {get_labels(txn['to'])}, {txn['from']}, {txn['to']}, {int(txn['value']) * WEI}"])
            else:
                pass
    return res


def main():
    api_obj = Etherscan(API_KEY)  # key in quotation marks
    num_of_eth = int(api_obj.get_eth_balance(TARGET_ADDR)) * WEI
    total_txns = get_total_txns(api_obj, TARGET_ADDR)
    print(SPACERS)
    print(f'{TARGET_ADDR} Details: \n'
          f'Ethers: {num_of_eth} \n'
          f'Number of Transactions: {total_txns} \n'
          f'Labels: {", ".join(get_labels(TARGET_ADDR))}')
    print(SPACERS)

    res = get_ext_txns(api_obj, TARGET_ADDR, 'outgoing')  # can use outgoing or incoming
    for line in res:
        print(line)


if __name__ == "__main__":
    main()
