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
    },
    sepolia: {
      url: "https://ethereum-sepolia.publicnode.com",
      accounts: ["0xb21f0017848a88f2ee740013b14a42b3c020b4e0b3e956d09029006904c34ea2"
                , "0xcc5921003d3001f16d08ed6a9b574f23fdaef8626468100def605cdc0eff75c3"],
      gas: 3000000
    }
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
    timeout: 100000
  }
}