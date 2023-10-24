MESSAGE_TIMEOUT = 10 # seconds 




TOKEN_ABI = '[{"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"symbol","type":"string"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"allowance","type":"uint256"},{"internalType":"uint256","name":"needed","type":"uint256"}],"name":"ERC20InsufficientAllowance","type":"error"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"uint256","name":"needed","type":"uint256"}],"name":"ERC20InsufficientBalance","type":"error"},{"inputs":[{"internalType":"address","name":"approver","type":"address"}],"name":"ERC20InvalidApprover","type":"error"},{"inputs":[{"internalType":"address","name":"receiver","type":"address"}],"name":"ERC20InvalidReceiver","type":"error"},{"inputs":[{"internalType":"address","name":"sender","type":"address"}],"name":"ERC20InvalidSender","type":"error"},{"inputs":[{"internalType":"address","name":"spender","type":"address"}],"name":"ERC20InvalidSpender","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]'
TOKEN_DISTRIBUTOR_ABI = '[{"inputs":[{"internalType":"contract IERC20","name":"_tokenAddress","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"bytes","name":"sig","type":"bytes"}],"name":"splitSignature","outputs":[{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"},{"internalType":"uint8","name":"v","type":"uint8"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"bytes[]","name":"_signatures","type":"bytes[]"}],"name":"verifyAndDistribute","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

TOKEN_CONTRACT_ADDRESS = '0xb76A1afa44c11b00cFE94bc99D6a4224C05AEDD9'
TOKEN_DISTRIBUTOR_CONTRACT_ADDRESS = '0x05a4A7299e73A1A57e11cF93b15339E3C77a24c2'


PROVIDER_URL = 'https://ethereum-sepolia.publicnode.com'
#PROVIDER_URL = 'http://127.0.0.1:8545'
#PROVIDER_URL = 'wss://ethereum-sepolia.publicnode.com' 

CLIENT_PRIVATEKEY = '0xb21f0017848a88f2ee740013b14a42b3c020b4e0b3e956d09029006904c34ea2'
CLIENT_PUBLICKEY = '0x1D1821d08ADA5aF3F48119BbBf193C865da020dE'


CLIENT_DICTIONARY = [
    {
        'port':8000 , 
        'peer_id': '16Uiu2HAmUusmnAEcQeA4vRCtYpnvemsGL1MrRBVz2MsBzjp2n4D2',
        'publickey': '0xDbfd7D50ed5D8CfA61eed64267FABE02d70231Db'
    },
    {
        'port':8001 , 
        'peer_id': '16Uiu2HAmD9JF6yyrUDZza6ZaCFcwKmkS34yscWu1Qfftd9BXb7MA',
        'publickey' : '0x1D1821d08ADA5aF3F48119BbBf193C865da020dE'
    },
    {
        'port':8002 , 
        'peer_id': '16Uiu2HAmSKye4qAr3vAtGiMF7tkRhXaQcv1ruBpxquCtcNL6y3SJ',
        'publickey':  '0x1050297611775cC7ec729572C217f774CE9e53f7'
    },
    {
        'port':8003 , 
        'secret': b'\xce\x10i; \x0eN\xea\x9e\x9b`;\xda"\x9a\xf80\xd1\xcaI\x889n\xda\x9d\x07\x161\xa5\xaa\xc8\xd5',
    }
]



