// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "../src/carbonRetirement.sol"; 

/**
 * @title MockNFT
 * @dev Contrato ERC721 de simulação para representar os créditos de carbono.
 * Precisamos dele para poder criar NFTs e testar o contrato CarbonRetirement.
 */
contract MockNFT is ERC721 {
    constructor() ERC721("Mock Carbon Credit", "MCC") {}

    function mint(address to, uint256 tokenId) public {
        _mint(to, tokenId);
    }
}

/**
 * @title CarbonRetirementTest
 * @dev Suíte de testes para o contrato CarbonRetirement.
 */
contract CarbonRetirementTest is Test {
    // Contratos que serão testados
    CarbonRetirement public retirementContract;
    MockNFT public nftContract;

    // Endereços de usuários para os testes
    address public user1 = makeAddr("user1");
    address public anotherUser = makeAddr("anotherUser");
    uint256 public constant TOKEN_ID = 1;

    // Evento para testar emissão
    event CreditRetired(address indexed by, uint256 indexed tokenId, uint256 timestamp);

    // Função executada antes de cada teste
    function setUp() public {
        // 1. Cria o contrato de NFT
        nftContract = new MockNFT();

        // 2. Cria o contrato de aposentadoria, passando o endereço do contrato de NFT
        retirementContract = new CarbonRetirement(address(nftContract));

        // 3. Cria um NFT (tokenId 1) para o user1
        nftContract.mint(user1, TOKEN_ID);
    }

    // --- Testes ---

    /**
     * @dev Testa o cenário de sucesso: um usuário aposentando seu próprio crédito de carbono.
     */
    function test_RetireCredit_Success() public {
        // Estado inicial: verifica que o token ainda não foi aposentado
        assertFalse(retirementContract.isRetired(TOKEN_ID), "Token nao deveria estar aposentado inicialmente");

        // Simula a chamada vindo do user1 (dono do token)
        vm.prank(user1);

        // Espera que o evento CreditRetired seja emitido com os dados corretos
        vm.expectEmit(true, true, false, true);
        emit CreditRetired(user1, TOKEN_ID, block.timestamp);

        // Executa a função
        retirementContract.retireCredit(TOKEN_ID);

        // Estado final: verifica se o token agora está marcado como aposentado
        assertTrue(retirementContract.isRetired(TOKEN_ID), "Token deveria estar aposentado apos a chamada");
    }

    /**
     * @dev Testa a falha: um usuário tenta aposentar um crédito que não lhe pertence.
     */
    function test_RevertIf_CallerIsNotOwner() public {
        // Espera que a transação falhe com a mensagem de erro específica
        // OBS: A mensagem de erro no seu contrato tem um erro de digitação ("neo"). O teste precisa corresponder exatamente.
        vm.expectRevert("Voce neo possui este token.");

        // Simula a chamada vindo de outro usuário que não é dono do token
        vm.prank(anotherUser);
        retirementContract.retireCredit(TOKEN_ID);
    }

    /**
     * @dev Testa a falha: o dono do crédito tenta aposentá-lo uma segunda vez.
     */
    function test_RevertIf_CreditIsAlreadyRetired() public {
        // Primeiro, aposenta o crédito com sucesso
        vm.prank(user1);
        retirementContract.retireCredit(TOKEN_ID);

        // Confirma que foi aposentado
        assertTrue(retirementContract.isRetired(TOKEN_ID), "O token deveria estar aposentado para este teste");

        // Agora, espera que a segunda tentativa falhe com a mensagem de erro específica
        vm.expectRevert("Este credito ja foi aposentado.");

        // Tenta aposentar novamente com o mesmo usuário
        vm.prank(user1);
        retirementContract.retireCredit(TOKEN_ID);
    }
}
