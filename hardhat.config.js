/** @type import('hardhat/config').HardhatUserConfig */
require("@nomiclabs/hardhat-web3");
require("@nomiclabs/hardhat-waffle");
module.exports =
{
  defaultNetwork: "hardhat",
  networks: {
    hardhat: {

      accounts: ["0xb21f0017848a88f2ee740013b14a42b3c020b4e0b3e956d09029006904c34ea2"
                , "0xcc5921003d3001f16d08ed6a9b574f23fdaef8626468100def605cdc0eff75c3"],
      gas: 3000000
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