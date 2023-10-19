
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

PROTOCOL_ID = TProtocol("/muon/1.0.0")



class Client:
    def __init__(self) -> None:
        self.state_mutex = Lock()
        self.signature_mutex = Lock()
        self.index_of_addressList = len(NODES_DICTIONARY) - 1
        self.port = NODES_DICTIONARY[self.index_of_addressList]['port']
        self.host = None
        self.addressList = NODES_DICTIONARY
        self.private_key = 'sdf'
        self.signatures = []
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

    def set_signatures(self,var):
        self.signature_mutex.acquire()
        self.signatures = var
        self.signature_mutex.release()
    
    def get_signatures(self):
        self.signature_mutex.acquire()
        var = self.signatures
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
        msg = await stream.read()
        msg = msg.decode(encoding='utf-8')
        logging.debug(f'Got message: {msg}')
        if msg[:len('RES::')] == 'RES::' and self.get_state() == 'pending':
            msg = msg.split('::')
            signatures = self.get_signatures()
            signatures.append(msg[1])
            self.set_signatures(signatures)
            signatures = self.get_signatures()
            if len(signatures) >= (len(self.addressList)-1)//2+1:
                logging.debug(f'signatures done: {signatures}')
                self.set_state('start')
        await stream.close()
    async def __send_message_to(self, destination:multiaddr):
        logging.debug (f'Sending intial request to :{destination}')
        maddr = multiaddr.Multiaddr(destination)
        info = info_from_p2p_addr(maddr)
        await self.host.connect(info)
        
        stream = await self.host.new_stream(info.peer_id, [PROTOCOL_ID])

        msg = f"START::{self.private_key}".encode()

        await stream.write(msg)
        await stream.close()
        
        logging.debug(f"Sent: {msg}")
    
    

    async def __start_action(self):
        self.set_signatures([])
        self.set_state('pending')
        async with trio.open_nursery() as nursery:
            for i in range(len(self.addressList)):
                if i != self.index_of_addressList:
                    destination = f'/ip4/127.0.0.1/tcp/{self.addressList[i]["port"]}/p2p/{self.addressList[i]["peer_id"]}'
                    nursery.start_soon(self.__send_message_to,destination)

    
    def stop_node():
        pass


         