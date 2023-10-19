from web3 import Web3
from eth_account.messages import encode_defunct
import logging




class Web3Utils:
    def __init__(self,provider_url,publickey,privatekey) -> None:
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.public_key = publickey
        self.private_key = privatekey 

        logging.debug(self.web3.is_connected(show_traceback=True))


    def verify_signer(self,signer_address, amount, signature):
        h = self.web3.solidity_keccak(['address', 'uint256'], [signer_address, amount])
        message = encode_defunct(hexstr= h.hex())
        recoverd_address = self.web3.eth.account.recover_message(message,signature)
        self.api = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"balanceLeft","type":"uint256"}],"name":"balance","type":"event"},{"inputs":[{"internalType":"address payable","name":"recipient","type":"address"}],"name":"destroy","outputs":[],"stateMutability":"nonpayable","type":"function"}'
        return recoverd_address==signer_address

    def function_send_transaction(self, contract_address, function_name):
        try:
            nonce = self.web3.eth.get_transaction_count(self.publickey)
            contract = self.web3.eth.contract(address=contract_address, abi=self.abi)
            chain_id = self.web3.eth.chain_id
            call_function = contract.functions
            if hasattr(call_function, function_name) and \
                callable(getattr(call_function, function_name)):
                method_to_call = getattr(call_function, function_name)
            method_to_call().buildTransaction(
                {"chainId": chain_id, "from": self.public_key, "nonce": nonce})
            signed_tx = self.web3.eth.account.sign_transaction(call_function, private_key=self.private_key)
            send_tx = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(send_tx)
        except Exception as e:
            logging.error("",exc_info=True)
            return False
        logging.debug(f'tx_receipt:{tx_receipt}')
        return True
    
    def function_call(self, contract_address, function_name):
        try:
            nonce = self.web3.eth.get_transaction_count(self.publickey)
            contract = self.web3.eth.contract(address=contract_address, abi=self.abi)
            chain_id = self.web3.eth.chain_id
            call_function = contract.functions
            if hasattr(call_function, function_name) and \
                callable(getattr(call_function, function_name)):
                method_to_call = getattr(call_function, function_name)
            result = method_to_call().call()
        except Exception as e:
            logging.error('',exc_info=True)
        logging.debug(f'raw data:{result}')
        return result




if __name__ == '__main__':
    x = Web3Utils('https://bsc-testnet.publicnode.com')
    