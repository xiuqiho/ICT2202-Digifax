import time

from etherscan import Etherscan

from rich.console import Console

console = Console()

API_KEY = "1XCMJP7VNAXU1NVSKS4C7XBM1ET77SYNVE"
ADDR = "0xddbd2b932c763ba5b1b7ae3b362eac3e8d40121a"

eth = Etherscan(API_KEY)

console.rule(f"{ADDR}")

curr_eth_usd = float(eth.get_eth_last_price()["ethusd"])

bal_in_wei = int(eth.get_eth_balance(address=ADDR))
bal_in_eth = bal_in_wei * 10e-19
bal_in_usd = bal_in_eth * curr_eth_usd

txns = (eth.get_normal_txs_by_address(address=ADDR, startblock=0, endblock=99999999, sort="asc"))

console.print(f"Number of TXNs: {len(txns)}")
console.print(f"Balance [Wei]: {bal_in_wei}")
console.print(f"Balance [Eth]: {bal_in_eth}")
console.print(f"Balance [USD]:", '${:,.2f}'.format(bal_in_usd))
