const { expect } = require("chai");
const { ethers} = require('hardhat');
describe("SignatureDistribution", function () {
	let contractInstance;
	let tokenInstance;
	let owner;
	let addr1;
	let addr2;
	let addr3;
	before(async function () {
		// Deploy ERC20 token
		const Token = await ethers.getContractFactory("MyToken");
		tokenInstance = await Token.deploy("Mammad Coin","MMC");
		await tokenInstance.deployed();
		// Deploy SignatureDistribution contract
		const SignatureDistribution = await ethers.getContractFactory("SignatureDistribution");
		contractInstance = await SignatureDistribution.deploy(tokenInstance.address);
		await contractInstance.deployed();
		//grant the contract to transfer tokens.
		await tokenInstance.approve(contractInstance.address,10000000);

		[owner,addr1,addr2,addr3] = await ethers.getSigners();
		
  	});

  	it("should distribute tokens on valid signature and valid signer", async function () {
		
		const addr1Pvk = '0x78bb7ef892b79c6482ebd1a48dc90b3de8d4b5be3d969965304352624db13b61';
		const addr2Pvk = '0xb21f0017848a88f2ee740013b14a42b3c020b4e0b3e956d09029006904c34ea2';
		const addr3Pvk = '0x02daa225c512866e07dcc9d025acf73afdc10c2bf05c8f7866e46a2760fc89f4';

		// Get the initial balance of the owner
		const initialOwnerBalance = await tokenInstance.balanceOf(owner.address);
		
		
		const amount = 250;
		
		
		// Some valid private key.
		packed = web3.utils.soliditySha3({t:'address',v:addr1.address},{t:'uint256',v:amount});
		const addr1SignedMessage = web3.eth.accounts.sign(packed,addr1Pvk);
		
		packed = web3.utils.soliditySha3({t:'address',v:addr2.address},{t:'uint256',v:amount});
		const addr2SignedMessage = web3.eth.accounts.sign(packed,addr2Pvk);

		packed = web3.utils.soliditySha3({t:'address',v:addr3.address},{t:'uint256',v:amount});
		const addr3SignedMessage = web3.eth.accounts.sign(packed,addr3Pvk);
		
		
		// Verify and distribute tokens
		await contractInstance.connect(addr1).verifyAndDistribute(amount, 
			[addr1SignedMessage.signature, addr2SignedMessage.signature, addr3SignedMessage.signature]);
		

		const finalOwnerBalance = await tokenInstance.balanceOf(owner.address);
		const initialSignerBalance = await tokenInstance.balanceOf(addr1.address);

		// Check that the expected amount was distributed
		expect(initialOwnerBalance).to.equal(finalOwnerBalance.add(amount));
		expect(initialSignerBalance).to.equal(amount);
	});

	it("should revert on invalid signatures", async function () {
		const addr1Pvk = '0x782b7ef892b79c6482ebd1a48dc90b3de8d4b5be3d969965304352624db13b61';
		const addr2Pvk = '0xb23f0017848a88f2ee740013b14a42b3c020b4e0b3e956d09029006904c34ea2';
		const addr3Pvk = '0x02aaa225c512866e07dcc9d025acf73afdc10c2bf05c8f7866e46a2760fc89f4';

		// Get the initial balance of the owner
		const initialOwnerBalance = await tokenInstance.balanceOf(owner.address);
		
		
		const amount = 250;
		
		
		// Some valid private key.
		packed = web3.utils.soliditySha3({t:'address',v:addr1.address},{t:'uint256',v:amount});
		const addr1SignedMessage = web3.eth.accounts.sign(packed,addr1Pvk);
		
		packed = web3.utils.soliditySha3({t:'address',v:addr2.address},{t:'uint256',v:amount});
		const addr2SignedMessage = web3.eth.accounts.sign(packed,addr2Pvk);

		packed = web3.utils.soliditySha3({t:'address',v:addr3.address},{t:'uint256',v:amount});
		const addr3SignedMessage = web3.eth.accounts.sign(packed,addr3Pvk);
		
		await expect(
			 contractInstance.connect(addr1).verifyAndDistribute(amount, 
				[addr1SignedMessage.signature, addr2SignedMessage.signature, addr3SignedMessage.signature]
    	)).to.be.reverted;
  	});

});