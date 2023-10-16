import random
import time
from configs import *
from multiaddr import multiaddr
import trio
import logging
from libp2p import new_host
from libp2p.crypto.secp256k1 import create_new_key_pair
from libp2p.network.stream.net_stream_interface import INetStream
from libp2p.peer.peerinfo import info_from_p2p_addr
from libp2p.typing import TProtocol
from threading import Lock
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
from  web3 import Web3
from eth_account.messages import encode_defunct
PROTOCOL_ID = TProtocol("/muon/1.0.0")



class Node:
    def __init__(self,index_of_addressList) -> None:
        self.state_mutex = Lock()
        self.rand_int_mutex = Lock()
        self.port = NODES_DICTIONARY[index_of_addressList]['port']
        self.index_of_addressList = index_of_addressList
        self.host = None
        self.addressList = NODES_DICTIONARY
        self.rand_int = 0
        self.all_rand_ints = []
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
        

    def set_rand_int(self,var):
        self.rand_int_mutex.acquire()
        self.all_rand_ints = var
        self.rand_int_mutex.release()
        
    def get_rand_int(self):
        self.rand_int_mutex.acquire()
        var = self.all_rand_ints
        self.rand_int_mutex.release()
        return var
    

    async def __run(self):
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.__run_server,self.port)
            nursery.start_soon(self.__run_check_signature)


    async def __run_check_signature(self):
        while True:
            if self.get_state() == 'pending':
                chkFailed = False
                for i in range(10):
                    rand_ints = self.get_rand_int()
                    if len(rand_ints) == len(self.addressList)- 1 and self.get_state()=='pending':
                        self.set_state('start')
                        ii = len(self.addressList)-1
                        sum = 0
                        for i in range(len(rand_ints)):
                            sum += rand_ints[i]
                        destination = f'/ip4/127.0.0.1/tcp/{self.addressList[ii]["port"]}/p2p/{self.addressList[ii]["peer_id"]}'
                        await self.__send_message_to(destination,f'RES::{sum}')
                        self.set_rand_int([])
                        break
                    await trio.sleep(GET_MESSAGE_TIMEOUT)
                
                self.set_state('start')
            else:
                await trio.sleep(0.4)

    async def __run_server(self, port: int) -> None:
        localhost_ip = "127.0.0.1"
        listen_addr = multiaddr.Multiaddr(f"/ip4/0.0.0.0/tcp/{port}")
        secret = self.addressList[self.index_of_addressList]['secret']
        self.host = new_host(key_pair=create_new_key_pair(secret))
        async with self.host.run(listen_addrs=[listen_addr]):
            logging.debug(f"I am {self.host.get_id().to_string()}")
            self.host.set_stream_handler(PROTOCOL_ID, self.__echo_stream_handler)
            logging.debug("Node is up!...")
            await trio.sleep_forever()
            
    async def __echo_stream_handler(self, stream: INetStream) -> None:
        try:
            msg = await stream.read()
            msg = msg.decode(encoding='utf-8')
            logging.debug(f'Got message: {msg}')
            if msg[:len('RND::')] == 'RND::' and self.get_state() == 'pending':
                msg = msg.split('::')
                rand_ints = self.get_rand_int()
                rand_ints.append(int(msg[1]))
                self.set_rand_int(rand_ints)
            elif msg[:len('START::')] == 'START::'  and self.get_state() == 'start':
                msg = msg.split('::')
                self.client_privatekey = msg[1]
                await self.__start_action()
            await stream.close()
        except Exception as e:
            logging.error('',exc_info=True)
        
    async def __send_message_to(self, destination:multiaddr,message):
        try:
            logging.debug (f'Sending message to :{destination}, message: {message}')
            maddr = multiaddr.Multiaddr(destination)
            info = info_from_p2p_addr(maddr)
            await self.host.connect(info)
            
            stream = await self.host.new_stream(info.peer_id, [PROTOCOL_ID])

            await stream.write(message.encode())
            await stream.close()
        except Exception as e:
            logging.error('',exc_info=True)
    
    
    def start_node(self):
        trio.run(self.__run)
    async def __start_action(self):
        if self.get_state() == 'start':
            self.rand_int = random.randint(1,20000)
            self.set_rand_int([self.rand_int])
            self.set_state('pending')
            logging.debug(f'random int generated:{self.rand_int}')
            async with trio.open_nursery() as nursery:
                for i in range(len(self.addressList)-1):
                    if i != self.index_of_addressList:
                        destination = f'/ip4/127.0.0.1/tcp/{self.addressList[i]["port"]}/p2p/{self.addressList[i]["peer_id"]}'
                        #logging.debug(f'starting soon send message to.. number {i}')
                        nursery.start_soon(self.__send_message_to, destination,f'RND::{self.rand_int}')

    
    def stop_node():
        pass
