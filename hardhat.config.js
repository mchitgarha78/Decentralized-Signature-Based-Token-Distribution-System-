/** @type import('hardhat/config').HardhatUserConfig */
require("@nomiclabs/hardhat-web3");
require("@nomiclabs/hardhat-waffle");
module.exports =
{
  defaultNetwork: "hardhat",
  networks: {
    hardhat: {

      // accounts: ['0xbaac8ed78b498fbbe1061f62fa935deb727ded6f2bbb8ba3c2df461f7489ac9d',
      //            '0x30af87fab21f1ec6b56de1756b33519f2f10e04661acd8346b5da850a73fc831']
    }
    // sepolia: {
    //   url: "https://sepolia.infura.io/v3/<key>",
    //   accounts: [privateKey1, privateKey2]
    // }
  },
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  },
  mocha: {
    timeout: 40000
  }
}