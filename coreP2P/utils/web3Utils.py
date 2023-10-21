from web3 import Web3
from eth_account.messages import encode_defunct
import logging
#from .clientConfig import TOKEN_ABI


class Web3Utils:
    def __init__(self,provider_url:str, private_key:str) -> None:
        self.__web3 = Web3(Web3.HTTPProvider(provider_url))
        self.public_key = self.__web3.eth.account.from_key(private_key).address
        self.private_key = private_key 


    def check_connection(self):
        return self.__web3.is_connected(show_traceback=True)

    def verify_signer(self,signer_address, amount, signature):
        h = self.__web3.solidity_keccak(['address', 'uint256'], [signer_address, amount])
        message = encode_defunct(hexstr= h.hex())
        recoverd_address = self.__web3.eth.account.recover_message(message,signature =bytes.fromhex(signature[2:]))
        return recoverd_address==signer_address
    

    def create_signature(self, signer_address, amount):
        h = self.__web3.solidity_keccak(['address', 'uint256'], [signer_address, amount])
        message = encode_defunct(hexstr= h.hex())
        return self.__web3.eth.account.sign_message(message, self.private_key)

    def function_send_transaction(self, contract_address, function_name, abi, **kwargs):
        try:
            nonce = self.__web3.eth.get_transaction_count(self.public_key)
            contract = self.__web3.eth.contract(address=contract_address, abi=abi)
            chain_id = self.__web3.eth.chain_id
            functions = contract.functions
            if hasattr(functions, function_name) and \
                callable(getattr(functions, function_name)):
                method_to_call = getattr(functions, function_name)
            else:
                return None
            call_function = method_to_call(**kwargs).build_transaction(
                {"chainId": chain_id, "from": self.public_key, "nonce": nonce})
            
            signed_tx = self.__web3.eth.account.sign_transaction(call_function, private_key=self.private_key)
            send_tx = self.__web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = self.__web3.eth.wait_for_transaction_receipt(send_tx)
        except Exception as e:
            logging.error(f'ERROR: web3Utils function send transaction:{e}')
            return None
        logging.debug(f'tx_receipt:{tx_receipt}')
        return True
    
    def function_call(self, contract_address, function_name,abi, **kwargs):
        try:
            contract = self.__web3.eth.contract(address=contract_address, abi=abi)
            functions = contract.functions
            if hasattr(functions, function_name) and \
                callable(getattr(functions, function_name)):
                method_to_call = getattr(functions, function_name)
            else:
                return None
            result = method_to_call(**kwargs).call()
        except Exception as e:
            logging.error(f'ERROR: web3Utils function call:{e}')
            return None
        logging.debug(f'raw data:{result}')
        return result




if __name__ == '__main__':
    public_key = '0x1D1821d08ADA5aF3F48119BbBf193C865da020dE'
    private_key = '0xb21f0017848a88f2ee740013b14a42b3c020b4e0b3e956d09029006904c34ea2'
    x = Web3Utils('https://ethereum-sepolia.publicnode.com',
                  private_key)
    print (x.public_key)

    t = x.create_signature(public_key,250).signature.hex()
    print (x.verify_signer(public_key,250,t))
    # t = x.function_call('0xc732E8d77F3bacEC0B845535beA3a7D17fd9DBC1',
    #                 'balanceOf',MYTOKEN_ABI,account = public_key)
    # print(t)
    