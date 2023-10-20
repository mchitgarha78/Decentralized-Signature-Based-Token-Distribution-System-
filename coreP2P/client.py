
import random
import time
from utils.clientConfig import *
from multiaddr import multiaddr
import trio
import logging
from queue import Queue
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
        self.__web3Utils = Web3Utils(PROVIDER_URL, CLIENT_PRIVATEKEY)
        self.__state_mutex = Lock()
        self.__node_mutex = Lock()
        self.__index_of_addressList = len(CLIENT_DICTIONARY) - 1
        self.__port = CLIENT_DICTIONARY[self.__index_of_addressList]['port']
        self.__host = None
        self.__addressList = CLIENT_DICTIONARY
        self.__node_data = []
        self.__state = 'start'
        self.__message_queue = Queue()
    def __get_state(self):
        self.__state_mutex.acquire()
        x = self.__state
        self.__state_mutex.release()
        return x
    
    def __set_state(self, state):
        self.__state_mutex.acquire()
        self.__state = state
        self.__state_mutex.release()

    def __set_node_data(self,var):
        self.__node_mutex.acquire()
        self.__node_data = var
        self.__node_mutex.release()
    
    def __get_node_data(self):
        self.__node_mutex.acquire()
        var = self.__node_data
        self.__node_mutex.release()
        return var



    async def __wait_for_initating_requests(self):
        # while True:
            await trio.sleep(3)
            await self.__start_initiating_request_to_all_nodes()

    async def __message_handler(self):
        while True:
            if self.__message_queue.empty():
                await trio.sleep(0.1)
            else:
                msg = self.__message_queue.get()
                try:
                    if msg[:len('RES::')] == 'RES::' and self.__get_state() == 'pending':
                        msg = msg.split('::')
                        if self.__web3Utils.verify_signer(msg[2],int(msg[1]),msg[3]):
                            logging.debug('Message verified...')
                            nodes_data = self.__get_node_data()
                            if len(nodes_data)==0 or \
                                (len(nodes_data) == 1 and nodes_data[0][0] == msg[1]):
                                nodes_data.append(msg[1:])
                                self.__set_node_data(nodes_data)
                            if len(nodes_data) >= (len(self.__addressList)-1)//2+1:
                                self.__set_state('start')
                                logging.debug(f'Nodes data got successfully: {nodes_data}')
                                self.__send_transaction_to_contract()
                except Exception as e:
                    logging.error('',exc_info=True)
                
            
    async def __run(self):
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.__run_server,self.__port)
            nursery.start_soon(self.__wait_for_initating_requests)
            nursery.start_soon(self.__message_handler) 
    def start_node(self):
        trio.run(self.__run)
    def set_state(self, state):
        self.__state_mutex.acquire()
        self.__state = state
        self.__state_mutex.release()
    
    async def __run_server(self, port: int) -> None:
        listen_addr = multiaddr.Multiaddr(f"/ip4/0.0.0.0/tcp/{port}")

        secret = self.__addressList[self.__index_of_addressList]['secret']
        
        self.__host = new_host(key_pair=create_new_key_pair(secret))
        async with self.__host.run(listen_addrs=[listen_addr]):

            logging.debug(f"I am client: {self.__host.get_id().to_string()}")
            self.__host.set_stream_handler(PROTOCOL_ID, self.__echo_stream_handler)
            await trio.sleep_forever()

    async def __echo_stream_handler(self, stream: INetStream) -> None:
        try:
            msg = await stream.read()
            msg = msg.decode(encoding='utf-8')
            logging.debug(f'Got message: {msg}')
            self.__message_queue.put(msg)
            await stream.close()
        except Exception as e:
            logging.error("",exc_info=True)
    
    def __send_transaction_to_contract(self):
        fixedList = []
        for _dict in self.__addressList:
            chk = False
            for _node in self.__node_data:
                if _node[1] == _dict.get('publickey'):
                    fixedList.append(_node)
                    chk = True
                    break
            if not chk:
                fixedList.append(self.__node_data[0])
        
        logging.debug(f'fixedList:{fixedList}')
        self.__web3Utils.function_send_transaction(TOKEN_DISTRIBUTOR_CONTRACT_ADDRESS,
                                                 'verifyAndDistribute',
                                                 TOKEN_DISTRIBUTOR_ABI,
                                                 _amount = int(fixedList[0][0]),
                                                 _signatures = 
                                                  [fixedList[0][2],fixedList[1][2],fixedList[2][2]])
    async def __send_message_to(self, destination:multiaddr, message:str):
        try:
            logging.debug(f'Sending intial request to :{destination}, message:{message}')
            maddr = multiaddr.Multiaddr(destination)
            info = info_from_p2p_addr(maddr)
            await self.__host.connect(info)
            stream = await self.__host.new_stream(info.peer_id, [PROTOCOL_ID])
            msg = f"START".encode()
            await stream.write(message.encode())
            await stream.close()
            logging.debug(f"Sent: {msg}")
        except Exception as e:
            logging.error('', exc_info= True)
    
    

    async def __start_initiating_request_to_all_nodes(self):
        self.__set_node_data([])
        self.__set_state('pending')
        async with trio.open_nursery() as nursery:
            for i in range(len(self.__addressList)):
                if i != self.__index_of_addressList:
                    destination = f'/ip4/127.0.0.1/tcp/{self.__addressList[i]["port"]}/p2p/{self.__addressList[i]["peer_id"]}'
                    nursery.start_soon(self.__send_message_to,destination,'START')

    
    def stop_node():
        pass


         