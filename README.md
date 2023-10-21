### Install package requirements
After cloning the project, Add a venv to your project using `python3 -m venv venv` command.

Activate it `source venv/bin/activate`

And you can Install the packages via `pip install -r requirements.txt` command.After the installation, you should install the libp2p package manually : https://github.com/libp2p/py-libp2p 

And in some linux distributions, `libgmp-dev` should be installed before installing py-libp2p by running this command:
		
	$ sudo apt install libgmp-dev

     
### Run project
To the project, run the following commands:

    $(venv) cd coreP2P
    $(venv) python main.py -n [node-number]
  
We have 4 nodes in this project. The last node is client. So if you want to run client, you should run this command:

    $(venv) python main.py -n 3

For other nodes you can run:

	$(venv) python main.py -n [0 to 2]


Note that whenever you run the client, It automatically waits for 3 seconds and initiate requests to all nodes. So you should start nodes first and then start the client.

If you want to change any configurations about nodes or client, you can change the files in these directories: `coreP2P/configs/clientConfig.py` and `coreP2P/configs/nodeConfigs.py`.


### Hardhat Testing
You can test the contracts using this command in local network:

    $ npx hardhat test

and if you want to test on testnet network you can run:

    $ npx hardhat test --network sepolia



    

