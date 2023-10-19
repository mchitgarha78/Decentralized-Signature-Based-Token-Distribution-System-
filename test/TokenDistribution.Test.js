const { expect } = require("chai");
const { ethers} = require('hardhat');
describe("SignatureDistribution", function () {
	let contractInstance;
	let tokenInstance;
	//let validPrivateKey = '0xb21f0017848a88f2ee740013b14a42b3c020b4e0b3e956d09029006904c34ea2';
	let owner;
	before(async function () {
		// Deploy ERC20 token
		const Token = await ethers.getContractFactory("MyToken");
		tokenInstance = await Token.deploy("Mammad Coin","MMC");
		await tokenInstance.deployed();
		console.log("ttt");
		// Deploy SignatureDistribution contract
		const SignatureDistribution = await ethers.getContractFactory("SignatureDistribution");
		contractInstance = await SignatureDistribution.deploy(tokenInstance.address);
		await contractInstance.deployed();
		//grant the contract to transfer tokens.
		await tokenInstance.approve(contractInstance.address,10000000);
		
  	});

  	it("should distribute tokens on valid signature and valid signer", async function () {
		console.log("t");
		ownerPvk = '0xb21f0017848a88f2ee740013b14a42b3c020b4e0b3e956d09029006904c34ea2';
		owner = web3.eth.accounts.privateKeyToAccount(ownerPvk);
		// Get the initial balance of the owner
		const initialOwnerBalance = await tokenInstance.balanceOf(owner.address);
		console.log("t2");
		provider = ethers.provider;
		web3 = new Web3(provider);
		const amount = 250;
		// Some valid private key.
		pvk = '0xb21f0017848a88f2ee740013b14a42b3c020b4e0b3e956d09029006904c34ea2';
		recipient = web3.eth.accounts.privateKeyToAccount(pvk);
		const packed = web3.utils.soliditySha3({t:'address',v:recipient.address},{t:'uint256',v:amount});
		const signedMessage = web3.eth.accounts.sign(packed,pvk);
		// Verify and distribute tokens
		console.log("t3");
		await contractInstance.verifyAndDistribute(amount, signedMessage.signature);
		console.log("t4");
		const finalOwnerBalance = await tokenInstance.balanceOf(owner.address);
		const initialSignerBalance = await tokenInstance.balanceOf(recipient.address);

		// Check that the expected amount was distributed
		expect(initialOwnerBalance).to.equal(finalOwnerBalance.add(amount));
		expect(initialSignerBalance).to.equal(amount);
	});

	// it("should revert on invalid signature", async function () {
	// 	// Generate an invalid signature
	// 	const invalidSignature = "0xdeadbeef";
	// 	const someMessageHash = "0xc103a9c7b301fba3815a21cef783890d86e1e5debcc5887a88cbcd4fe9eeb3af";
	// 	const someTestAddress = "0xa28e76baBD2C507D25b7621be0AD24AA8E032823";
	// 	// Verify and distribute tokens with the invalid signature
	// 	await expect(
    //   		contractInstance.verifyAndDistribute(100, someMessageHash,invalidSignature
	// 			,someTestAddress)
    // 	).to.be.reverted;
  	// });

});