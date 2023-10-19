from web3 import Web3
from eth_account.messages import encode_defunct
import logging
from clientConfig import MYTOKEN_ABI



class Web3Utils:
    def __init__(self,provider_url:str, publickey:str, privatekey:str) -> None:
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.public_key = publickey
        self.private_key = privatekey 
        logging.debug(self.web3.is_connected(show_traceback=True))


    def verify_signer(self,signer_address, amount, signature):
        h = self.web3.solidity_keccak(['address', 'uint256'], [signer_address, amount])
        message = encode_defunct(hexstr= h.hex())
        recoverd_address = self.web3.eth.account.recover_message(message,signature)
        return recoverd_address==signer_address

    def function_send_transaction(self, contract_address, function_name,abi, **kwargs):
        try:
            nonce = self.web3.eth.get_transaction_count(self.publickey)
            contract = self.web3.eth.contract(address=contract_address, abi=abi)
            chain_id = self.web3.eth.chain_id
            functions = contract.functions
            if hasattr(functions, function_name) and \
                callable(getattr(functions, function_name)):
                method_to_call = getattr(functions, function_name)
            else:
                return None
            call_function = method_to_call(**kwargs).buildTransaction(
                {"chainId": chain_id, "from": self.public_key, "nonce": nonce})
            
            signed_tx = self.web3.eth.account.sign_transaction(call_function, private_key=self.private_key)
            send_tx = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(send_tx)
        except Exception as e:
            logging.error("",exc_info=True)
            return None
        logging.debug(f'tx_receipt:{tx_receipt}')
        return True
    
    def function_call(self, contract_address, function_name,abi, **kwargs):
        try:
            contract = self.web3.eth.contract(address=contract_address, abi=abi)
            functions = contract.functions
            if hasattr(functions, function_name) and \
                callable(getattr(functions, function_name)):
                method_to_call = getattr(functions, function_name)
            else:
                return None
            result = method_to_call(**kwargs).call()
        except Exception as e:
            logging.error('',exc_info=True)
            return None
        logging.debug(f'raw data:{result}')
        return result




if __name__ == '__main__':
    public_key = '0x1D1821d08ADA5aF3F48119BbBf193C865da020dE'
    private_key = '0xb21f0017848a88f2ee740013b14a42b3c020b4e0b3e956d09029006904c34ea2'
    x = Web3Utils('https://ethereum-sepolia.publicnode.com',
                  public_key,private_key)
    
    t = x.function_call('0xc732E8d77F3bacEC0B845535beA3a7D17fd9DBC1',
                    'balanceOf',account = public_key)
    print(t)
    