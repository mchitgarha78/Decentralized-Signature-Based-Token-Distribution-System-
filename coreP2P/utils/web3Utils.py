from web3 import Web3
from eth_account.messages import encode_defunct
import logging
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
                {"chainId": chain_id, "from": self.public_key, "nonce": nonce
                 ,"gas":3000000,})
            
            signed_tx = self.__web3.eth.account.sign_transaction(call_function, private_key=self.private_key)
            send_tx = self.__web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = self.__web3.eth.wait_for_transaction_receipt(send_tx)
        except Exception as e:
            logging.error(f'ERROR: web3Utils function send transaction:{e}',exc_info=True)
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
    fixedList = [[2176, '0xDbfd7D50ed5D8CfA61eed64267FABE02d70231Db', '0xddcc0ff8ea5a1b2d535bca582f9f2cded607d39e7b8c950f23789544ef0b7e753bc2faec13c7b27b0f0e6a29cfb6b804622a62a1ae79560910d89b3acecd31511b'],
               [2176, '0x1D1821d08ADA5aF3F48119BbBf193C865da020dE', '0xcfbd0ba17606fea1ac166c8d14cbfc93f97846b7c0a533a57ae93771693c3f8534f257cbe1c5d5b25bb7f388b4acf39e73de902951978f1c44a6c74106bf18ea1c'],
               [2176, '0x1D1821d08ADA5aF3F48119BbBf193C865da020dE', '0xcfbd0ba17606fea1ac166c8d14cbfc93f97846b7c0a533a57ae93771693c3f8534f257cbe1c5d5b25bb7f388b4acf39e73de902951978f1c44a6c74106bf18ea1c']]
    #public_key = '0x1D1821d08ADA5aF3F48119BbBf193C865da020dE'
    private_key = CLIENT_PRIVATEKEY
    x = Web3Utils('https://ethereum-sepolia.publicnode.com',
                  private_key)
    # x = Web3Utils('http://127.0.0.1:8545',
    #               private_key)
    print (x.public_key)
    C_ADDRESS = '0x05cC6C87A304e843F7db0CbB82C5d384D5BC8D14'
    # t = x.create_signature(public_key,250).signature.hex()
    # print (x.verify_signer(public_key,250,t))
    #t = x.function_send_transaction(TOKEN_DISTRIBUTOR_CONTRACT_ADDRESS,
    #                'approve',TOKEN_ABI,spender = TOKEN_DISTRIBUTOR_CONTRACT_ADDRESS, value = 1000000)
    t = x.function_send_transaction(TOKEN_DISTRIBUTOR_CONTRACT_ADDRESS,
                                                 'verifyAndDistribute',
                                                 TOKEN_DISTRIBUTOR_ABI,
                                                 _amount = int(fixedList[0][0]),
                                                 _signatures = 
                                                  [fixedList[0][2],fixedList[1][2],fixedList[2][2]])
    logging.debug(f't:{t}')
    