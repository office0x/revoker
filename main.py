import json
from web3 import Web3
from eth_account import Account
import asyncio
import random

# RPCS dictionary (as provided)
RPCS = {
    # 'ethereum': 'https://eth.llamarpc.com',
    'arbitrum': 'https://arb1.arbitrum.io/rpc',
    'base': 'https://base.meowrpc.com',
    'blast': 'https://rpc.envelop.is/blast',
    'optimism': 'https://mainnet.optimism.io',
    'bsc': 'https://bsc-dataseed.binance.org',
    'matic': 'https://polygon-rpc.com',
    'fantom': 'https://rpcapi.fantom.network',
    'avalanche': 'https://api.avax.network/ext/bc/C/rpc',
    'core': 'https://rpc-core.icecreamswap.com',
    'zora': 'https://rpc.zora.energy',
    'linea': 'https://rpc.linea.build',
    'zksync': 'https://mainnet.era.zksync.io'
}


TOKENS = {
    "ethereum": {
        "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "WETH": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    },
    "arbitrum": {
        "USDT": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",
        "USDC": "0xaf88d065e77c8cc2239327c5edb3a432268e5831",
        "USDCE": "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8",
        "WETH": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
    },
    "optimism": {
        "USDT": "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58",
        "USDC": "0x0b2c639c533813f4aa9d7837caf62653d097ff85",
        "WETH": "0x4200000000000000000000000000000000000006",
    },
    "base": {
        "USDC": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
        "USDbC": "0xd9aaec86b65d86f6a7b5b1b0c42ffa531710b6ca",
        "WETH": "0x4200000000000000000000000000000000000006",
    },
    "matic": {
        "USDT": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f",
        "USDC": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359",
        "WETH": "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619",
    },
    "bsc": {
        "USDT": "0x55d398326f99059ff775485246999027b3197955",
        "USDC": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
        "WETH": "0x2170ed0880ac9a755fd29b2688956bd959f933f8",
        "BUSD": "0x55d398326f99059ff775485246999027b3197955"
    },
    "avalanche": {
        "USDT": "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7",
        "USDC": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
        "WETH": "0x49d5c2bdffac6ce2bfdb6640f4f80f226bc10bab",
    },
    "zksync": {
        "USDT": "0x493257fD37EDB34451f62EDf8D2a0C418852bA4C",
        "USDC": "0x1d17CBcF0D6D143135aE902365D2E5e2A16538D4",
        "WETH": "0x5aea5775959fbc2557cc8789bc1bf90a239d9a91",
    },
    "fantom": {
        "USDB": "0x049d68029688eabf473097a2fc38ef61633a3c7a",
        "USDC": "0x04068da6c83afcfa0e13ba15a6696662335d5b75",
        "WETH": "0x74b23882a30290451a17c44f4f05243b6b58c76d",
    },
    "blast": {
        "USDB": "0x4300000000000000000000000000000000000003",
        "WETH": "0x4300000000000000000000000000000000000004",
    }
}

SPENDERS = [
    '0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae',
    '0x341e94069f53234fE6DabeF707aD424830525715',
    '0xDE1E598b81620773454588B85D6b5D4eEC32573e',
    '0x24ca98fB6972F5eE05f0dB00595c7f68D9FaFd68'
]

# ERC-20 ABI
ERC20_ABI = json.loads('[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"remaining","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"success","type":"bool"}],"type":"function"}]')

async def revoke(token_address, private_key, chain='ethereum'):
    w3 = Web3(Web3.HTTPProvider(RPCS[chain]))
    account = Account.from_key(private_key)
    address = account.address

    token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)

    for spender in SPENDERS:
        spender = Web3.to_checksum_address(spender)
        allowance = token_contract.functions.allowance(address, spender).call()
        
        if allowance > 0:
            # print(f"Revoking approval for token {token_address} from spender {spender} in {chain} for {address}")
            
            # Prepare the transaction
            txn = token_contract.functions.approve(spender, 0).build_transaction({
                'from': address,
                'nonce': w3.eth.get_transaction_count(address),
                'gas': 100000,  # Adjust as needed
                'gasPrice': w3.eth.gas_price
            })
            gas_estimate = w3.eth.estimate_gas(txn)
            txn['gas'] = int(gas_estimate * 1.2)  # Add 20% buffer

            
            # Sign the transaction
            signed_txn = w3.eth.account.sign_transaction(txn, private_key)
            
            # Send the transaction
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for the transaction receipt
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt['status'] == 1:
                print(f"Successfully revoked approval for token {token_address} from spender {spender} in {chain} for {address}")
            else:
                print(f"Failed to revoke approval for token {token_address} from spender {spender} in {chain} for {address}")
        else:
            # print(f"No approval found for token {token_address} from spender {spender} in {chain}")
            ...

async def main():
    # Read private keys from file
    with open('private_keys.txt', 'r') as f:
        private_keys = f.read().splitlines()
    
    random.shuffle(private_keys)


    for private_key in private_keys:
        account = Account.from_key(private_key)
        address = account.address
        
        print(f"Processing account: {address}")
        
        # Iterate through all chains
        for chain in RPCS.keys():
            w3 = Web3(Web3.HTTPProvider(RPCS[chain]))
            if chain in TOKENS:
                balance = w3.eth.get_balance(address)
                if balance > 0:
                        for token_name, token_address in TOKENS[chain].items():
                            try:
                                await revoke(token_address, private_key, chain)
                            except:
                                print("revoke error")

if __name__ == "__main__":
    asyncio.run(main())
