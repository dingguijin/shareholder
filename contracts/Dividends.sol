// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.18;

import {BLS} from "./BLS.sol";

contract Dividends {
    address public owner;
    uint256 public totalInvestment;
    uint256 public totalFirstInvestment;
    uint256 public totalSecondInvestment;
    uint256[4] public aggBlsPublicKey;
    uint256[2] public tempMemHash;
    
    struct Shareholder {
        uint256 firstInvestment;
        uint256 secondInvestment;
        uint256 income;
    }

    struct DividendProposal {
        uint256 id;
        bool hasVerified;
        mapping(address => uint256) shareholderDividends;
    }

    mapping(address => Shareholder) public shareholders;
    address[] public shareholderAddresses;
    mapping(uint256 => DividendProposal) public proposals;
    uint256 public proposalCount;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function.");
        _;
    }

    constructor() {
        owner = msg.sender;
        proposalCount = 0;
    }

    function addFirstInvestment(address _shareholder, uint256 _amount) public onlyOwner {
        require(shareholders[_shareholder].firstInvestment == 0, "First investment already made.");
        shareholders[_shareholder].firstInvestment = _amount;
        totalInvestment += _amount;
        totalFirstInvestment += _amount;
        shareholderAddresses.push(_shareholder);
    }

    function addSecondInvestment(address _shareholder, uint256 _amount) public {
        require(shareholders[_shareholder].firstInvestment > 0, "First investment not made yet.");
        shareholders[_shareholder].secondInvestment += _amount;
        totalSecondInvestment += _amount;
        totalInvestment += _amount;
    }

    function setShareholderIncome(address _shareholder, uint256 _income) public onlyOwner {
        require(shareholders[_shareholder].firstInvestment > 0, "First investment not made yet.");
        shareholders[_shareholder].income = _income;
    }

    function setAggBlsPublicKey(uint256[4] calldata _bls_public_key) public onlyOwner {
        aggBlsPublicKey[0] = _bls_public_key[0];
        aggBlsPublicKey[1] = _bls_public_key[1];
        aggBlsPublicKey[2] = _bls_public_key[2];
        aggBlsPublicKey[3] = _bls_public_key[3];
    }
    
    function calculateTotalIncome() private view returns (uint256) {
        uint256 totalIncome = 0;
        for (uint256 i = 0; i < shareholderAddresses.length; i++) {
            address _shareholder = shareholderAddresses[i];
            totalIncome += shareholders[_shareholder].income;
        }
        return totalIncome;
    }

    function calculateDividends(address _shareholder) public view returns (uint256) {
        Shareholder memory s = shareholders[_shareholder];
        uint256 totalIncome = calculateTotalIncome();
        uint256 conversionShares = ((1000 * s.firstInvestment)/totalFirstInvestment) / 2;
        uint256 conversionEarnings = 0;
        if (totalIncome != 0) {
            conversionEarnings = (1000 * s.income) / totalIncome;
        }
        uint256 secondInvestmentRatio = (1000 * s.secondInvestment) / totalInvestment;
        uint256 actualDividends = (conversionShares / 4) + (conversionEarnings / 2) + (secondInvestmentRatio / 4);
        return actualDividends;
    }

    function createProposalStruct (DividendProposal storage proposal, uint256 _id) internal {
        proposal.id = _id;
        proposal.hasVerified = false;
        for (uint256 i = 0; i < shareholderAddresses.length; i++) {
            address shareholder = shareholderAddresses[i];
            uint256 dividends = calculateDividends(shareholder);
            proposal.shareholderDividends[shareholder] = dividends;
        }
    }

    function createProposal() public onlyOwner {
        DividendProposal storage newProposal = proposals[proposalCount];
        createProposalStruct(newProposal, proposalCount);
        proposalCount += 1;
    }

    function verifyProposal(uint256 _proposalId,
                            uint256[2] memory _aggSignature) public onlyOwner returns (bool) {
        uint256[2] memory _memHash = BLS.hashToPoint(abi.encodePacked(_proposalId));
        tempMemHash[0] = _memHash[0];
        tempMemHash[1] = _memHash[1];
        require(BLS.verifySingle(_aggSignature, aggBlsPublicKey, _memHash), "BLS not verified.");
        proposals[_proposalId].hasVerified = true;
        return true;
    }
                             
    function getShareholderAddresses() public view returns (address[] memory) {
        return shareholderAddresses;
    }

    function getShareholderDividends(uint256 _proposalId, address _shareholder) public view returns (uint256) {
        return proposals[_proposalId].shareholderDividends[_shareholder];
    }
    
}
