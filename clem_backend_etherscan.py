from etherscan import Etherscan
from secrets import API_KEY
from json import dumps

TARGET_ADDR = "0xddBd2B932c763bA5b1b7AE3B362eac3e8d40121A".lower()
WEI = 0.000000000000000001  # 10e-19
SPACERS = "=" * 80


def get_total_txns(api_obj, target_addr):
    """This function allows you to get the total number of txns of a wallet addr (incoming/outgoing)"""
    dict_full_txns = api_obj.get_normal_txs_by_address(target_addr, 0, 9999999999, 'age')
    return len(dict_full_txns)


def get_ext_txns(api_obj, target_addr, direction):
    """This function allow you to list all the incoming or outgoing txns of a wallet address
    Information extracted: timeStamp, from, to, value, blockNumber"""
    list_full_txns = api_obj.get_normal_txs_by_address(target_addr, 0, 9999999999, 'age')
    res = []
    for txn in list_full_txns:
        # if to is empty, probably a contract creation txn
        if len(txn['to']) > 1:
            if direction == 'outgoing':
                if txn['from'] == target_addr:
                    res.append(
                        f"{txn['timeStamp']}, {txn['blockNumber']}, {txn['from']}, {txn['to']}, {int(txn['value']) * WEI}")
            if direction == 'incoming':
                if txn['to'] == target_addr:
                    res.append(
                        f"{txn['timeStamp']}, {txn['blockNumber']}, {txn['from']}, {txn['to']}, {int(txn['value']) * WEI}")
            else:
                pass
    print(res)


def main():
    api_obj = Etherscan(API_KEY)  # key in quotation marks
    num_of_eth = int(api_obj.get_eth_balance(TARGET_ADDR)) * WEI
    total_txns = get_total_txns(api_obj, TARGET_ADDR)
    print(SPACERS + "\n" + f'{TARGET_ADDR} has {num_of_eth} Ether and {total_txns} txns' + '\n' + SPACERS)
    get_ext_txns(api_obj, TARGET_ADDR, 'outgoing')
    get_ext_txns(api_obj, TARGET_ADDR, 'incoming')


if __name__ == "__main__":
    main()
