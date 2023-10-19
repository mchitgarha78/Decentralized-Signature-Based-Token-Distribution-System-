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


class P2PClass:
    def __init__(self, port, secret, protocol_id = TProtocol("/muon/1.0.0")) -> None:
        self.__port = port
        self.__secret = secret
        self.__Portocol_id = protocol_id
    async def run_p2p(self):
        listen_addr = multiaddr.Multiaddr(f"/ip4/0.0.0.0/tcp/{self.__port}")
        self.host = new_host(key_pair=create_new_key_pair(self.__secret))
        async with self.host.run(listen_addrs=[listen_addr]):
            logging.debug(f"I am {self.host.get_id().to_string()}")
            self.host.set_stream_handler(self.Portocol_id, self.__echo_stream_handler)
            logging.debug("Node is up!...")
            await trio.sleep_forever()
    
    @abstractmethod
    async def __echo_stream_handler(self, stream: INetStream) -> None:
        pass
    
    async def __send_message_to(self, destination:multiaddr,message):
        logging.debug (f'Sending message to :{destination}, message: {message}')
        maddr = multiaddr.Multiaddr(destination)
        info = info_from_p2p_addr(maddr)
        await self.host.connect(info)
        
        stream = await self.host.new_stream(info.peer_id, [self.__Portocol_id])

        await stream.write(message.encode())
        await stream.close()

    def start_p2p(self):
        trio.run(self.__run)