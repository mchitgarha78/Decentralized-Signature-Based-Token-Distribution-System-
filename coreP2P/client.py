
import random
import time
from utils.clientConfig import *
from multiaddr import multiaddr
import trio
import logging
from libp2p import new_host

from libp2p.crypto.secp256k1 import create_new_key_pair
from libp2p.network.stream.net_stream_interface import INetStream
from libp2p.peer.peerinfo import info_from_p2p_addr
from libp2p.typing import TProtocol
from threading import Lock
from utils.web3Utils import Web3Utils
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)

PROTOCOL_ID = TProtocol("/muon/1.0.0")



class Client:
    def __init__(self) -> None:
        self.web3Utils = Web3Utils(PROVIDER_URL, CLIENT_PRIVATEKEY)
        self.state_mutex = Lock()
        self.signature_mutex = Lock()
        self.index_of_addressList = len(CLIENT_DICTIONARY) - 1
        self.port = CLIENT_DICTIONARY[self.index_of_addressList]['port']
        self.host = None
        self.addressList = CLIENT_DICTIONARY
        self.node_data = []
        self.state = 'start'
        self.client_privatekey = ''
    def get_state(self):
        self.state_mutex.acquire()
        x = self.state
        self.state_mutex.release()
        return x
    
    def set_state(self, state):
        self.state_mutex.acquire()
        self.state = state
        self.state_mutex.release()

    def set_node_data(self,var):
        self.signature_mutex.acquire()
        self.node_data = var
        self.signature_mutex.release()
    
    def get_node_data(self):
        self.signature_mutex.acquire()
        var = self.node_data
        self.signature_mutex.release()
        return var

    async def __send_requests(self):
        # while True:
            await trio.sleep(3)
            await self.__start_action()
            
    async def __run(self):
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.__run_server,self.port)
            nursery.start_soon(self.__send_requests)
                
    def start_node(self):
        trio.run(self.__run)
    def set_state(self, state):
        self.state_mutex.acquire()
        self.state = state
        self.state_mutex.release()
    
    async def __run_server(self, port: int) -> None:
        localhost_ip = "127.0.0.1"
        listen_addr = multiaddr.Multiaddr(f"/ip4/0.0.0.0/tcp/{port}")

        secret = self.addressList[self.index_of_addressList]['secret']
        
        self.host = new_host(key_pair=create_new_key_pair(secret))
        async with self.host.run(listen_addrs=[listen_addr]):

            logging.debug(f"I am client: {self.host.get_id().to_string()}")
            self.host.set_stream_handler(PROTOCOL_ID, self.__echo_stream_handler)
            await trio.sleep_forever()

    async def __echo_stream_handler(self, stream: INetStream) -> None:
        try:
            msg = await stream.read()
            msg = msg.decode(encoding='utf-8')
            logging.debug(f'Got message: {msg}')
            await trio.sleep(5)
            if msg[:len('RES::')] == 'RES::' and self.get_state() == 'pending':
                msg = msg.split('::')
                if self.web3Utils.verify_signer(msg[2],int(msg[1]),msg[3]):
                    logging.debug('Message verified...')
                    nodes_data = self.get_node_data()
                    if len(nodes_data)==0 or \
                        (len(nodes_data) == 1 and nodes_data[0][0] == msg[1]):
                        nodes_data.append(msg[1:])
                        self.set_node_data(nodes_data)
                    if len(nodes_data) >= (len(self.addressList)-1)//2+1:
                        self.set_state('start')
                        logging.debug(f'Nodes data got successfully: {nodes_data}')
                        self.__send_transaction_to_contract()
            await stream.close()
        except Exception as e:
            logging.error("",exc_info=True)
    
    def __send_transaction_to_contract(self):
        '''
Nodes data got successfully: 
[['20875', '0xDbfd7D50ed5D8CfA61eed64267FABE02d70231Db', 
'0x79820228ec4bc1682671fa644990cd6ff743d7a75cb66c1576f1438a862981f927047b849ff06e220451ce4608c1d5c4a5a804f2febe8b430783f19fe868b3cf1b'], 
['20875', '0x1050297611775cC7ec729572C217f774CE9e53f7', 
'0x43024933396515ea6d51ae05e4ced463290a1343f9670f32d027ff8b0e46bbc62c2052875ef81cf1369dae5d75d20465f2c1fd474d0961182bc031f75fedf3bb1c']]
        '''

        fixedList = []
        for _dict in self.addressList:
            chk = False
            for _node in self.node_data:
                if _node[1] == _dict.get('publickey'):
                    fixedList.append(_node)
                    chk = True
                    break
            if not chk:
                fixedList.append(self.node_data[0])
        
        logging.debug(f'fixedList:{fixedList}')
        self.web3Utils.function_send_transaction(TOKEN_DISTRIBUTOR_CONTRACT_ADDRESS,
                                                 'verifyAndDistribute',
                                                 TOKEN_DISTRIBUTOR_ABI,
                                                 _amount = int(fixedList[0][0]),
                                                 _signatures = 
                                                  [fixedList[0][2],fixedList[1][2],fixedList[2][2]])
    async def __send_message_to(self, destination:multiaddr):
        logging.debug (f'Sending intial request to :{destination}')
        maddr = multiaddr.Multiaddr(destination)
        info = info_from_p2p_addr(maddr)
        await self.host.connect(info)
        
        stream = await self.host.new_stream(info.peer_id, [PROTOCOL_ID])

        msg = f"START".encode()

        await stream.write(msg)
        await stream.close()
        
        logging.debug(f"Sent: {msg}")
    
    

    async def __start_action(self):
        self.set_node_data([])
        self.set_state('pending')
        async with trio.open_nursery() as nursery:
            for i in range(len(self.addressList)):
                if i != self.index_of_addressList:
                    destination = f'/ip4/127.0.0.1/tcp/{self.addressList[i]["port"]}/p2p/{self.addressList[i]["peer_id"]}'
                    nursery.start_soon(self.__send_message_to,destination)

    
    def stop_node():
        pass


         