const { expect } = require("chai");
const { ethers} = require('hardhat');
describe("SignatureDistribution", function () {
	let contractInstance;
	let tokenInstance;
	let owner;

	before(async function () {
		// Deploy ERC20 token
		const Token = await ethers.getContractFactory("MyToken");
		tokenInstance = await Token.deploy("Mamad Coin","MMC");

		// Deploy SignatureDistribution contract
		const SignatureDistribution = await ethers.getContractFactory("SignatureDistribution");
		contractInstance = await SignatureDistribution.deploy(tokenInstance.address,100);
		
		//grant the contract to transfer tokens.
		tokenInstance.approve(contractInstance.address,10000000);
		
		await contractInstance.deployed();

		[owner] = await ethers.getSigners();
  	});

  	it("should distribute tokens on valid signature", async function () {
		// Get the initial balance of the owner
		const initialOwnerBalance = await tokenInstance.balanceOf(owner.address);
		provider = ethers.provider;
		web3 = new Web3(provider);
		const amount = 200;
		// Some test private key.
		pvk = '0xcc5921003d3001f16d08ed6a9b574f23fdaef8626468100def605cdc0eff75c3';
		recipient = web3.eth.accounts.privateKeyToAccount(pvk);
		const packed = web3.utils.soliditySha3({t:'address',v:recipient.address},{t:'uint256',v:100});
		const signedMessage = web3.eth.accounts.sign(packed,pvk);
		// Verify and distribute tokens
		await contractInstance.verifyAndDistribute
			(amount, signedMessage.messageHash, signedMessage.signature
				,recipient.address);

		const finalOwnerBalance = await tokenInstance.balanceOf(owner.address);
		const initialSignerBalance = await tokenInstance.balanceOf(recipient.address);

		// Check that the expected amount was distributed
		expect(initialOwnerBalance).to.equal(finalOwnerBalance.add(amount));
		expect(initialSignerBalance).to.equal(amount);
	});

	it("should revert on invalid signature", async function () {
		// Generate an invalid signature
		const invalidSignature = "0xdeadbeef";
		const someMessageHash = "0xc103a9c7b301fba3815a21cef783890d86e1e5debcc5887a88cbcd4fe9eeb3af";
		const someTestAddress = "0xa28e76baBD2C507D25b7621be0AD24AA8E032823";
		// Verify and distribute tokens with the invalid signature
		await expect(
      		contractInstance.verifyAndDistribute(100, someMessageHash,invalidSignature
				,someTestAddress)
    	).to.be.reverted;
  	});

});