from brownie import TestBLS, Dividends, accounts

from py_ecc.optimized_bn128 import *
from eth_hash.auto import keccak
from typing import Tuple
from eth_utils import encode_hex

import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BrownieTestLogger")

# used for helped aggregation
def get_public_key_G1(secret_key: int) -> Tuple[FQ, FQ, FQ]:
    return multiply(G1, secret_key)


def get_public_key(secret_key: int) -> Tuple[FQ2, FQ2, FQ2]:
    return multiply(G2, secret_key)


def sign(message: Tuple[FQ, FQ, FQ], secret_key: int):
    return multiply(message, secret_key)


def aggregate_signatures(signatures: list[Tuple[FQ, FQ, FQ]]) -> Tuple[FQ, FQ, FQ]:
    res = signatures[0]
    for signature in signatures[1:]:
        res = add(res, signature)
    return res


def aggregate_public_keys(pubkeys: list[Tuple[FQ2, FQ2, FQ2]]) -> Tuple[FQ2, FQ2, FQ2]:
    res = pubkeys[0]
    for pubkey in pubkeys[1:]:
        res = add(res, pubkey)
    return res


# used for helped aggregation
def aggregate_public_keys_G1(pubkeys: list[Tuple[FQ, FQ, FQ]]) -> Tuple[FQ, FQ, FQ]:
    res = pubkeys[0]
    for pubkey in pubkeys[1:]:
        res = add(res, pubkey)
    return res


def hash_to_point(data: str):
    return map_to_point(keccak(data))


def map_to_point(x):
    pass


def sqrt(x_sqaure: int) -> Tuple[int, bool]:
    pass


def parse_solc_G1(solc_G1: Tuple[int, int]):
    x, y = solc_G1
    return FQ(x), FQ(y), FQ(1)


def format_G1(g1_element: Tuple[FQ, FQ, FQ]) -> Tuple[FQ, FQ]:
    x, y = normalize(g1_element)
    return (str(x), str(y))


def format_G2(g2_element: Tuple[FQ2, FQ2, FQ2]) -> Tuple[FQ2, FQ2]:
    x, y = normalize(g2_element)
    x1, x2 = x.coeffs
    y1, y2 = y.coeffs
    return x1, x2, y1, y2

def test_investment():
    test_dividends = accounts[0].deploy(Dividends)
    test_bls = accounts[0].deploy(TestBLS)

    _holder_0 = accounts.add()
    _holder_1 = accounts.add()
    _holder_2 = accounts.add()
    _holder_3 = accounts.add()
    _holder_4 = accounts.add()

    test_dividends.addFirstInvestment(_holder_0.address, 1000*1000)
    test_dividends.addFirstInvestment(_holder_1.address, 1000*1000)
    test_dividends.addFirstInvestment(_holder_2.address, 1000*1000)
    test_dividends.addFirstInvestment(_holder_3.address, 1000*1000)
    test_dividends.addFirstInvestment(_holder_4.address, 1000*1000)



def test_shareholder():
    test_dividends = accounts[0].deploy(Dividends)
    test_bls = accounts[0].deploy(TestBLS)

    _holder_0 = accounts.add()
    _holder_1 = accounts.add()
    _holder_2 = accounts.add()
    _holder_3 = accounts.add()
    _holder_4 = accounts.add()

    test_dividends.addFirstInvestment(_holder_0.address, 1000*1000)
    test_dividends.addFirstInvestment(_holder_1.address, 1000*1000)
    test_dividends.addFirstInvestment(_holder_2.address, 1000*1000)
    test_dividends.addFirstInvestment(_holder_3.address, 1000*1000)
    test_dividends.addFirstInvestment(_holder_4.address, 1000*1000)

    test_dividends.addSecondInvestment(_holder_1.address, 1000*1000)
    test_dividends.setShareholderIncome(_holder_1.address, 1000)

    print(test_dividends.createProposal()) # 0
    print(test_dividends.createProposal()) # 1
    print(test_dividends.createProposal()) # 2

    _holder_private_0 = int(_holder_0.private_key, 16)
    _holder_private_1 = int(_holder_1.private_key, 16)
    _holder_private_2 = int(_holder_2.private_key, 16)
    _holder_private_3 = int(_holder_3.private_key, 16)
    _holder_private_4 = int(_holder_4.private_key, 16)
        
    _holder_key_0 = get_public_key(_holder_private_0) # ETH PRIVATE => BLS PRIVATE KEY -> BLS PUBLIC KEY
    _holder_key_1 = get_public_key(_holder_private_1)
    _holder_key_2 = get_public_key(_holder_private_2)
    _holder_key_3 = get_public_key(_holder_private_3)
    _holder_key_4 = get_public_key(_holder_private_4)

    # _holder_key_0_solc = format_G2(_holder_key_0)
    # _holder_key_1_solc = format_G2(_holder_key_1)
    # _holder_key_2_solc = format_G2(_holder_key_2)
    # _holder_key_3_solc = format_G2(_holder_key_3)

    agg_public_key = aggregate_public_keys([_holder_key_0,
                                            _holder_key_1,
                                            _holder_key_2,
                                            _holder_key_3,
                                            _holder_key_4])
    agg_pubkey_solc = format_G2(agg_public_key) # BLS aggregate public key Generator 2 -> 4 * 256bit
    # e(P, H(m)) = e(G, S) p->G2, G->G2, H(m) S -> G1

    test_dividends.setAggBlsPublicKey(agg_pubkey_solc)
    print("aggBlsPublicKey ... ", test_dividends.aggBlsPublicKey(0))
    print(agg_pubkey_solc)

    proposal_1 = 1 # proposal ID (0,1,2)
    data = proposal_1.to_bytes(32, byteorder='big')
    message_solc = tuple(test_bls.hashToPoint(data)) # hash(m->1) -> 32byte -> point G1
    message = parse_solc_G1(message_solc)
    
    sig0 = sign(message, _holder_private_0)
    sig1 = sign(message, _holder_private_1)
    sig2 = sign(message, _holder_private_2)
    sig3 = sign(message, _holder_private_3)
    sig4 = sign(message, _holder_private_4)

    agg_sig = aggregate_signatures([sig0, sig1, sig2, sig3, sig4]) # add Fq 
    agg_sig_solc = format_G1(agg_sig)

    #assert test_bls.verifySingle(agg_sig_solc, agg_pubkey_solc, message_solc)
    assert test_dividends.verifyProposal(proposal_1, agg_sig_solc)

    #print(test_bls.verifySingle(agg_sig_solc, agg_pubkey_solc, message_solc))
    print(test_dividends.proposalCount())
    print(test_dividends.totalInvestment())
    print(test_dividends.owner())

    print(test_dividends.proposals)
    
    x = test_dividends.getShareholderDividends(1, _holder_1.address)
    x = float(str(x))
    print("proposal 1, holder 1, dividend: %f" % (x/1000.00))
    return
