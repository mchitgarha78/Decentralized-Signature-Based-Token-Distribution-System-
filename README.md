### Install package requirements
Add a venv to your project using `python3 -m venv venv` command.

Activate it `source venv/bin/activate`

And you can Install the packages via `pip install -r requirements.txt` command. Note that the libp2p package should install manually : https://github.com/libp2p/py-libp2p 

And in some linux distributions, you should install `libgmp-dev` before installing py-libp2p by running this command:
		
	$ sudo apt install libgmp-dev

     
### Run project
To the project, run the following commands:

    $(venv) python main.py -n [node-number]
  
We have 4 nodes in this project. The last node is client. So if you want to run client, you should run this command:

    $(venv) python main.py -n 3


For other node you can run:

	$(venv) python main.py -n [0 to 2]


Note that whenever you run the client, It automatically waits for 3 seconds and initiate requests to all nodes. So you should start nodes first.
    

