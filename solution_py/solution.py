#! /usr/bin/env python3

import json
import sys

# sha256.py in this directory
import sha256

inputs = json.load(sys.stdin)
outputs = {}


### Building Blocks

# Problem 1
outputs["problem1"] = [sha256.add32(a, b) for a, b in inputs["problem1"]]

# Problem 2
outputs["problem2"] = [sha256.rightrotate32(a, b) for a, b in inputs["problem2"]]


### The Message Schedule

# Problem 3
outputs["problem3"] = sha256.little_sigma0(inputs["problem3"])

# Problem 4
outputs["problem4"] = sha256.little_sigma1(inputs["problem4"])

# Problem 5
outputs["problem5"] = sha256.message_schedule_array(inputs["problem5"].encode())


### The Round Function

# Problem 6
outputs["problem6"] = sha256.big_sigma0(inputs["problem6"])

# Problem 7
outputs["problem7"] = sha256.big_sigma1(inputs["problem7"])

# Problem 8
outputs["problem8"] = sha256.choice(*inputs["problem8"])

# Problem 9
outputs["problem9"] = sha256.majority(*inputs["problem9"])

# Problem 10
obj = inputs["problem10"]
outputs["problem10"] = sha256.round(
    obj["state"], obj["round_constant"], obj["schedule_word"]
)

### The Compression Function

# Problem 11
obj = inputs["problem11"]
outputs["problem11"] = sha256.compress_block(obj["state"], obj["block"].encode())


### Padding

# Problem 12
outputs["problem12"] = [sha256.padding_bytes(n).hex() for n in inputs["problem12"]]


### The Hash Function

# Problem 13
def assert_equal(s):
    import hashlib

    assert hashlib.sha256(s).digest() == sha256.sha256(s)


for s in inputs["problem13"]:
    assert_equal(s.encode())
outputs["problem13"] = [sha256.sha256(s.encode()).hex() for s in inputs["problem13"]]


### The Length Extension Attack

# Problem 14
original_input = inputs["problem14"]["original_input"].encode()
chosen_suffix = inputs["problem14"]["chosen_suffix"].encode()
outputs["problem14"] = (
    original_input + sha256.padding_bytes(len(original_input)) + chosen_suffix
).hex()

# Problem 15
outputs["problem15"] = sha256.reconstitute_state(bytes.fromhex(inputs["problem15"]))

# Problem 16
obj = inputs["problem16"]
original_hash = bytes.fromhex(obj["original_hash"])
original_len = obj["original_len"]
chosen_suffix = obj["chosen_suffix"].encode()
outputs["problem16"] = sha256.length_extend(
    original_hash, original_len, chosen_suffix
).hex()

json.dump(outputs, sys.stdout, indent="  ")
print()
