#! /usr/bin/env python3

import sys

# fmt: off
IV = [
    0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19,
]

ROUND_CONSTANTS = [
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2,
]
# fmt: on


### Building Blocks


def add32(*args):
    return sum(args) % (2**32)


def rightrotate32(x, n):
    assert x < 2**32, "x is too large. Did you use + instead of add32 somewhere?"
    right_part = x >> n
    left_part = x << (32 - n)
    return add32(left_part, right_part)


### The Message Schedule


def little_sigma0(word):
    return rightrotate32(word, 7) ^ rightrotate32(word, 18) ^ (word >> 3)


def little_sigma1(word):
    return rightrotate32(word, 17) ^ rightrotate32(word, 19) ^ (word >> 10)


def message_schedule_array(block):
    assert len(block) == 64
    w = []
    for i in range(16):
        assert i == len(w)
        w.append(int.from_bytes(block[4 * i : 4 * i + 4], "big"))
    for i in range(16, 64):
        s0 = little_sigma0(w[i - 15])
        s1 = little_sigma1(w[i - 2])
        w.append(add32(w[i - 16], s0, w[i - 7], s1))
    return w


### The Round Function


def big_sigma0(word):
    return rightrotate32(word, 2) ^ rightrotate32(word, 13) ^ rightrotate32(word, 22)


def big_sigma1(word):
    return rightrotate32(word, 6) ^ rightrotate32(word, 11) ^ rightrotate32(word, 25)


def choice(x, y, z):
    return (x & y) ^ (~x & z)


def majority(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)


def round(state, round_constant, schedule_word):
    S1 = big_sigma1(state[4])
    ch = choice(state[4], state[5], state[6])
    temp1 = add32(state[7], S1, ch, round_constant, schedule_word)
    S0 = big_sigma0(state[0])
    maj = majority(state[0], state[1], state[2])
    temp2 = add32(S0, maj)
    return [
        add32(temp1, temp2),
        state[0],
        state[1],
        state[2],
        add32(state[3], temp1),
        state[4],
        state[5],
        state[6],
    ]


### The Compression Function


def compress_block(input_state_words, block):
    w = message_schedule_array(block)
    state_words = input_state_words
    for round_number in range(64):
        round_constant = ROUND_CONSTANTS[round_number]
        schedule_word = w[round_number]
        state_words = round(state_words, round_constant, schedule_word)
    return [add32(x, y) for x, y in zip(input_state_words, state_words)]


### Padding


def padding_bytes(input_len):
    remainder_bytes = (input_len + 8) % 64
    filler_bytes = 64 - remainder_bytes
    zero_bytes = filler_bytes - 1
    encoded_bit_length = (8 * input_len).to_bytes(8, "big")
    return b"\x80" + b"\0" * zero_bytes + encoded_bit_length


### The Hash Function


def sha256(message):
    padded = message + padding_bytes(len(message))
    assert len(padded) % 64 == 0
    state_words = IV
    i = 0
    while i < len(padded):
        block = padded[i : i + 64]
        state_words = compress_block(state_words, block)
        i += 64
    return b"".join(x.to_bytes(4, "big") for x in state_words)


# This is a test function. If you want to run it (and the other test above),
# install pytest with `pip install pytest` and then run `pytest sha256.py`.
# This test is the only place in this solution where I use hashlib.
def test_sha256():
    import hashlib

    for test_len in range(200):
        print(f"test_len = {test_len}")
        input251 = bytes(x % 251 for x in range(test_len))
        assert sha256(input251) == hashlib.sha256(input251).digest()


### The Length Extension Attack


def extended_len(original_len, suffix_len):
    return original_len + len(padding_bytes(original_len)) + suffix_len


def reconstitute_state(original_hash):
    return [int.from_bytes(original_hash[4 * i : 4 * i + 4], "big") for i in range(8)]


def length_extend(original_hash, original_len, suffix):
    new_padding = padding_bytes(extended_len(original_len, len(suffix)))
    new_blocks = suffix + new_padding
    state_words = reconstitute_state(original_hash)
    i = 0
    while i < len(new_blocks):
        block = new_blocks[i : i + 64]
        state_words = compress_block(state_words, block)
        i += 64
    return b"".join(x.to_bytes(4, "big") for x in state_words)


# This is a test function. If you want to run it (and the other test above),
# install pytest with `pip install pytest` and then run `pytest sha256.py`.
def test_length_extend():
    for test_len in range(200):
        print(f"test_len = {test_len}")
        input251 = bytes(x % 251 for x in range(test_len))
        suffix = b"hello world"
        original_hash = sha256(input251)
        suffixed_input = input251 + padding_bytes(len(input251)) + suffix
        expected_hash = sha256(suffixed_input)
        extended_hash = length_extend(original_hash, len(input251), suffix)
        assert expected_hash == extended_hash


if __name__ == "__main__":
    message = sys.stdin.buffer.read()
    output = sha256(message)
    print(output.hex())
