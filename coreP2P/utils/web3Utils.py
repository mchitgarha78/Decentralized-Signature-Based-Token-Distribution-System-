from web3 import Web3
from eth_account.messages import encode_defunct
import logging

class Web3Utils:
    def __init__(self,provider_url) -> None:
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        logging.debug(self.web3.is_connected(show_traceback=True))


    def verify_signer(self,signer_address, amount, signature):
        h = self.web3.solidity_keccak(['address', 'uint256'], [signer_address, amount])
        message = encode_defunct(hexstr= h.hex())
        recoverd_address = self.web3.eth.account.recover_message(message,signature)
        return recoverd_address==signer_address

    def send_transaction():
        pass
    

    
    





if __name__ == '__main__':
    x = Web3Utils('https://bsc-testnet.publicnode.com')
    