// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Script} from "forge-std/Script.sol";
import "forge-std/console.sol";
import {forestMonitor} from "../src/forestMonitor.sol";
import {CarbonRetirement} from "../src/carbonRetirement.sol";

contract DeployAll is Script {
    function run() external returns (address, address) {
        // Pega a chave privada do seu arquivo .env
        uint256 privateKey = vm.envUint("PRIVATE_KEY");

        // Inicia a "transmissão" para a blockchain
        vm.startBroadcast(privateKey);

        // 1. Faz o deploy do contrato de NFT primeiro
        forestMonitor monitor = new forestMonitor();
        console.log("Contrato 'forestMonitor' implantado em:", address(monitor));

        // 2. Faz o deploy do contrato de aposentadoria, passando o endereço do NFT no construtor
        CarbonRetirement retirement = new CarbonRetirement(address(monitor));
        console.log("Contrato 'CarbonRetirement' implantado em:", address(retirement));

        // Finaliza a transmissão
        vm.stopBroadcast();

        return (address(monitor), address(retirement));
    }
}

// --broadcast
// --fork-url
