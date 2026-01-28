// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/forestMonitor.sol";

contract ForestMonitorTest is Test {
    forestMonitor monitor;

    address owner = makeAddr("owner");
    address fiscalAmbiental = makeAddr("fiscalAmbiental");

    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);

    function setUp() public {
        vm.prank(owner);
        monitor = new forestMonitor();
    }

    // --- Testes ---

    function test_ConstructorSetsNameAndSymbol() public view {
        assertEq(monitor.name(), "forestMonitor", "O nome do contrato deve ser 'forestMonitor'");
        assertEq(monitor.symbol(), "Monitoramento", "O simbolo do contrato deve ser 'Monitoramento'");
    }

    function test_CreateForestRecord_Success() public {
        string memory imageID = "LANDSAT-9-PARA-SUL-2025-Q3";
        string memory areaName = "Sul do Estado do Para";
        string memory periodCurrent = "2025-01-01 a 2025-12-31";
        string memory periodPrevious = "2024-01-01 a 2024-12-31";
        string memory coordinates = "-8.7451, -50.3344";
        uint256 deforestationArea = 150;
        uint256 preservedArea = 9850;

        vm.prank(fiscalAmbiental);

        vm.expectEmit(true, true, true, true);
        emit Transfer(address(0), fiscalAmbiental, 1);

        uint256 newTokenId = monitor.createforestRecord(
            imageID, areaName, periodCurrent, periodPrevious, coordinates, deforestationArea, preservedArea
        );

        assertEq(newTokenId, 1);
        assertEq(monitor.ownerOf(newTokenId), fiscalAmbiental);
        assertEq(monitor.balanceOf(fiscalAmbiental), 1);

        forestMonitor.forestRecord memory record = monitor.getforestRecord(newTokenId);

        assertEq(record.imageID, imageID);
        assertEq(record.areaName, areaName);
        assertEq(record.deforestationArea, deforestationArea);
        assertEq(record.preservedArea, preservedArea);
        assertTrue(record.timestamp > 0);
    }

    function test_TokenIdIncrementsCorrectly() public {
        vm.prank(fiscalAmbiental);
        uint256 firstTokenId = monitor.createforestRecord("IMG1", "Area1", "P1", "P0", "C1", 10, 100);

        vm.prank(owner);
        uint256 secondTokenId = monitor.createforestRecord("IMG2", "Area2", "P2", "P1", "C2", 20, 200);

        assertEq(firstTokenId, 1);
        assertEq(secondTokenId, 2);
        assertEq(monitor.ownerOf(2), owner);
    }

    /**
     * @dev Testa se a função reverte ao tentar buscar um registro para um tokenId inexistente.
     */
    function test_RevertWhenGettingRecordForNonExistentToken() public {
        vm.expectRevert();
        monitor.getforestRecord(999);
    }
}
