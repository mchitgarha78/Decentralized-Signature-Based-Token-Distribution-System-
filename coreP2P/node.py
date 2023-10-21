from queue import Queue
import random
import time
from configs.nodeConfigs import *
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
from utils.threadSafeList import ThreadSafeList
from utils.web3Utils import Web3Utils 
PROTOCOL_ID = TProtocol("/muon/1.0.0")



class Node:
    def __init__(self,index_of_addressList) -> None:
        self.__web3Utils = Web3Utils('',NODES_DICTIONARY[index_of_addressList]['privatekey'])
        self.__port = NODES_DICTIONARY[index_of_addressList]['port']
        self.__index_of_addressList = index_of_addressList
        self.__host = None
        self.__addressList = NODES_DICTIONARY
        self.__all_rand_ints = ThreadSafeList()
        self.__state = ThreadSafeList()
        trio.run(self.__state.append, 'start')
        self.__message_queue = Queue()
    

    
    async def __message_handler(self):
        while True:
            if self.__message_queue.empty():
                await trio.sleep(0.1)
            else:
                msg = self.__message_queue.get()
                try:
                    if msg[:len('RND::')] == 'RND::' and (await self.__state.get_item(0)) == 'pending':
                        msg = msg.split('::')
                        await self.__all_rand_ints.append(int(msg[1]))
                        
                    elif msg[:len('START')] == 'START'  and (await self.__state.get_item(0)) == 'start':
                        await self.__start_seding_message_to_all_nodes()
                except Exception as e:
                    logging.error(f'Error in message handler:{e}')
        
    async def __run(self):
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.__run_server,self.__port)
            nursery.start_soon(self.__run_check_all_rand_int_received)
            nursery.start_soon(self.__message_handler)

    async def __run_check_all_rand_int_received(self):
        while True:
            if (await self.__state.get_item(0)) == 'pending':
                chk = False
                for i in range(NUMBER_OF_RETRY_MESSAGE_RECEIVED):
                    rand_ints = await self.__all_rand_ints.get_list()
                    if (len(rand_ints) == len(self.__addressList)- 1 and (await self.__state.get_item(0))=='pending') or \
                       (len(rand_ints) == (len(self.__addressList)-1)//2+1 and i == NUMBER_OF_RETRY_MESSAGE_RECEIVED-1):
                        chk = True
                        await self.__state.set_item(0,'start')
                        ii = len(self.__addressList)-1
                        sum = 0
                        for i in range(len(rand_ints)):
                            sum += rand_ints[i]
                        destination = f'/ip4/127.0.0.1/tcp/{self.__addressList[ii]["port"]}/p2p/{self.__addressList[ii]["peer_id"]}'
                        public_key = self.__web3Utils.public_key
                        signed_message = self.__web3Utils.create_signature(public_key, sum)
                        await self.__send_message_to(destination,f'RES::{sum}::{public_key}::{signed_message.signature.hex()}')
                        await self.__all_rand_ints.clear()
                        break
                    await trio.sleep(MESSAGE_TIMEOUT)
                await self.__state.set_item(0,'start')
                if not chk:
                    ii = len(self.__addressList)-1
                    destination = f'/ip4/127.0.0.1/tcp/{self.__addressList[ii]["port"]}/p2p/{self.__addressList[ii]["peer_id"]}'
                    await self.__send_message_to(destination, f'ERR::400::{self.__host.get_id().to_string()}::Not enought number from other nodes received.')
                    
            else:
                await trio.sleep(0.4)

    async def __run_server(self, port: int) -> None:
        localhost_ip = "127.0.0.1"
        listen_addr = multiaddr.Multiaddr(f"/ip4/0.0.0.0/tcp/{port}")
        secret = self.__addressList[self.__index_of_addressList]['secret']
        self.__host = new_host(key_pair=create_new_key_pair(secret))
        async with self.__host.run(listen_addrs=[listen_addr]):
            logging.debug(f"I am {self.__host.get_id().to_string()}")
            self.__host.set_stream_handler(PROTOCOL_ID, self.__echo_stream_handler)
            logging.debug("Node is up!...")
            await trio.sleep_forever()
            
    async def __echo_stream_handler(self, stream: INetStream) -> None:
        msg = await stream.read()
        msg = msg.decode(encoding='utf-8')
        logging.debug(f'Got message: {msg}')
        self.__message_queue.put(msg)
        await stream.close()
        
    async def __send_message_to(self, destination:multiaddr,message):
        try:
            logging.debug (f'Sending message to :{destination}, message: {message}')
            maddr = multiaddr.Multiaddr(destination)
            info = info_from_p2p_addr(maddr)
            await self.__host.connect(info)
            
            stream = await self.__host.new_stream(info.peer_id, [PROTOCOL_ID])

            await stream.write(message.encode())
            await stream.close()
        except Exception as e:
            logging.warning(f"Unable to send initial request to {destination}: {e}")
    
    
    def start_node(self):
        trio.run(self.__run)
    
    async def __start_seding_message_to_all_nodes(self):
        if (await self.__state.get_item(0)) == 'start':
            rand_int = random.randint(1,2000)
            await self.__all_rand_ints.append(rand_int)
            await self.__state.set_item(0,'pending')
            logging.debug(f'random int generated:{rand_int}')
            async with trio.open_nursery() as nursery:
                for i in range(len(self.__addressList)-1):
                    if i != self.__index_of_addressList:
                        destination = f'/ip4/127.0.0.1/tcp/{self.__addressList[i]["port"]}/p2p/{self.__addressList[i]["peer_id"]}'
                        #logging.debug(f'starting soon send message to.. number {i}')
                        nursery.start_soon(self.__send_message_to, destination,f'RND::{rand_int}')

    
    def stop_node():
        pass
