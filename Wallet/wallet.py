# Import dependencies
import os
import subprocess
import json
from dotenv import load_dotenv


# Load and set environment variables
load_dotenv()
mnemonic = os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
# YOUR CODE HERE
from constants import *
from web3 import Web3
from eth_account import Account
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI
    
    
# connect Web3
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1.8545'))

# including a mnemonic prefunded to test
mnemonic = os.getenv('mnemonic')

#Add the following middleware to web3.py to support the PoA algorithm:
from web3.middleware import geth_poa_middleware

w3.middleware_onion.inject(geth_poa_middleware, layer=0)



# Create a function called `derive_wallets`
def derive_wallets(coin, mnemonic, numderive): 
    command = f'php ./hd-wallet-derive/hd-wallet-derive.php -g --coin="{coin}" --mnemonic="{mnemonic}" --numderive="{numderive}" --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    return  keys

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {"eth", "btc-test"}
numderive = 3
keys = {}
for coin in coins:
    keys[coin]= derive_wallets(mnemonic, coin, numderive)
    
eth_priv_key = keys["eth"][0]['priv_key']
btc_priv_key = keys['btc-test'][0]['priv_key']



# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    
eth_privkey = keys["eth"][0]['privkey']
btc_privkey = keys['btc-test'][0]['privkey']


# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, recipient, amount):
    global tx_data
    if coin ==ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": recipient, "value": amount}
        )
        tx_data = {
            "to": recipient,
            "from": account.address,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address)
        }
        return tx_data

    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)]) 

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, recipient, amount):
    if coin == "eth": 
        tx_eth = create_tx(coin,account, recipient, amount)
        sign = account.signTransaction(tx_eth)
        result = w3.eth.sendRawTransaction(sign.rawTransaction)
        print(result.hex())
        return result.hex()
    else:
        tx_btctest= create_tx(coin,account,recipient,amount)
        sign_tx_btctest = account.sign_transaction(tx_btctest)
        from bit.network import NetworkAPI
        NetworkAPI.broadcast_tx_testnet(sign_tx_btctest)       
        return sign_tx_btctest

