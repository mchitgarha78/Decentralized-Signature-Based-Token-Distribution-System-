
import random
import time
from configs.clientConfig import *
from multiaddr import multiaddr
import trio
import logging
from queue import Queue
from libp2p import new_host
from libp2p.crypto.secp256k1 import create_new_key_pair
from libp2p.network.stream.net_stream_interface import INetStream
from libp2p.peer.peerinfo import info_from_p2p_addr
from libp2p.typing import TProtocol
from utils.web3Utils import Web3Utils
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
from utils.threadSafeList import ThreadSafeList
PROTOCOL_ID = TProtocol("/muon/1.0.0")



class Client:
    def __init__(self) -> None:
        self.__web3Utils = Web3Utils(PROVIDER_URL, CLIENT_PRIVATEKEY)
        self.__index_of_addressList = len(CLIENT_DICTIONARY) - 1
        self.__port = CLIENT_DICTIONARY[self.__index_of_addressList]['port']
        self.__host = None
        self.__addressList = CLIENT_DICTIONARY
        self.__node_data = ThreadSafeList()
        self.__state = ThreadSafeList()
        trio.run(self.__state.append,'start')
        self.__message_queue = Queue()
        self.__lost_connection_node = ThreadSafeList()




    async def __wait_for_initating_requests(self):
        #while True:
            await trio.sleep(3)
            await self.__start_initiating_request_to_all_nodes()

    async def __message_handler(self):
        while True:
            if self.__message_queue.empty():
                await trio.sleep(0.1)
            else:
                msg = self.__message_queue.get()
                try:
                    # RES :: amount :: publickey :: signature
                    if msg[:len('RES::')] == 'RES::' and (await self.__state.get_item(0)) == 'pending': 
                        msg = msg.split('::')
                        msg[1] = int(msg[1])
                        if self.__web3Utils.verify_signer(msg[2],int(msg[1]),msg[3]):
                            logging.debug('Message verified...')
                            await self.__node_data.append(msg[1:])
                            nodes_data = await self.__node_data.get_list()
                            
                            if len(nodes_data) >= (len(self.__addressList)-1)//2+1:
                                counts = {}
                                for _node in nodes_data:
                                    counts[_node[0]] = counts.get(_node[0], 0) + 1
                                max_count = max(counts.values())
                                if max_count >= (len(self.__addressList)-1)//2+1:
                                    await self.__state.set_item(0,'start')
                                    await self.__lost_connection_node.clear()
                                    logging.debug(f'Nodes data got and verified successfully: {nodes_data}')
                                    try:
                                        await self.__send_transaction_to_contract()
                                    except Exception as e:
                                        logging.error(f'Error in sending transaction:{e}')
                                        
                    elif msg[:len('ERR::')] == 'ERR::' and (await self.__state.get_item(0)) == 'pending':
                        msg = msg.split('::')
                        if msg[1] == '400':
                            logging.error(f'ERROR {msg[1]}: More than half of the nodes lost connection to node with peer id {msg[2]}')
                            await self.__lost_connection_node.append(msg[2])
                except Exception as e:
                    logging.error(f'Error in message handler:{e}')
                
            
    async def __run(self):
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.__run_server,self.__port)
            nursery.start_soon(self.__wait_for_initating_requests)
            nursery.start_soon(self.__message_handler)
            nursery.start_soon(self.__error_handler)
            await trio.sleep_forever()
    
    async def __error_handler(self):
        while True:
            if (await self.__state.get_item(0)) == 'pending':
                if (await self.__lost_connection_node.length()) >= (len(self.__addressList)-1)//2+1:
                        await self.__state.set_item(0,'start')
                        await self.__lost_connection_node.clear()
                        
                        continue
                
                chk = False
                for i in range(NUMBER_OF_RETRY_MESSAGE_RECEIVED):
                    if (await self.__state.get_item(0)) == 'start':
                        chk = True
                        break
                    await trio.sleep(MESSAGE_TIMEOUT)
                if not chk:
                    await self.__state.set_item(0,'start')
                    await self.__lost_connection_node.clear()
                    #logging.error(f'ERROR 402 : Timeout error . Aborting request...')
                    
            else:
                await trio.sleep(0.4)


    def start_node(self):
        trio.run(self.__run)
    
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
            logging.error(f"Error in __echo_stream_handler: {e}")
    
    async def __send_transaction_to_contract(self):
        fixedList = []
        nodes_data = await self.__node_data.get_list()
        for i in range(len(self.__addressList)-1):
            _dict = self.__addressList[i]
            chk = False
            for _node in nodes_data:
                if _node[1] == _dict.get('publickey'):
                    fixedList.append(_node)
                    chk = True
                    break
            if not chk:
                fixedList.append(nodes_data[0])
        
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
            logging.error(f"Unable to send initial request to {destination}: {e}")
    
    

    async def __start_initiating_request_to_all_nodes(self):
        await self.__node_data.clear()
        await self.__state.set_item(0,'pending')
        async with trio.open_nursery() as nursery:
            for i in range(len(self.__addressList)):
                if i != self.__index_of_addressList:
                    destination = f'/ip4/127.0.0.1/tcp/{self.__addressList[i]["port"]}/p2p/{self.__addressList[i]["peer_id"]}'
                    nursery.start_soon(self.__send_message_to,destination,'START')

    
    def stop_node():
        pass


         