#! /usr/bin/env python3

import json
import secrets
from secrets import randbits
import sys

# CAUTION: `random` isn't cryptographically secure. In general, prefer to use
# `secrets`. But `secrets` currently lacks a shuffle() function, so we just
# import that specific function from `random`.
from random import shuffle

import hashlib

animals = [
    "aardvark",
    "butterfly",
    "cat",
    "dog",
    "elephant",
    "fox",
    "giraffe",
    "hippopotamus",
    "iguana",
    "jaguar",
    "kangaroo",
    "llama",
    "manatee",
    "narwhal",
    "octopus",
    "pig",
    "quail",
    "rhinoceros",
    "sheep",
    "turkey",
    "unicorn",
    "vulture",
    "wombat",
    "xenoceratops",
    "yak",
    "zebra",
]


def random_animals(n):
    return " ".join(secrets.choice(animals) for _ in range(n))


def random_string(n):
    return random_animals(n)[:n]


inputs = {}


### Building Blocks

# Problem 1
inputs["problem1"] = [
    [1, 2],
    [(2 ** 32) - 1, 1],
    # Something random that will overflow.
    [(2 ** 31) + randbits(31), (2 ** 31) + randbits(31)],
]

# Problem 2
inputs["problem2"] = [
    [2, 1],
    [1, 1],
    [randbits(32), randbits(5)],
]


### The Message Schedule

# Problem 3
inputs["problem3"] = randbits(32)

# Problem 4
inputs["problem4"] = randbits(32)

# Problem 5
inputs["problem5"] = random_string(64)


### The Round Function

# Problem 6
inputs["problem6"] = randbits(32)

# Problem 7
inputs["problem7"] = randbits(32)

# Problem 8
inputs["problem8"] = [randbits(32), randbits(32), randbits(32)]

# Problem 9
inputs["problem9"] = [randbits(32), randbits(32), randbits(32)]

# Problem 10
state = [randbits(32) for _ in range(8)]
inputs["problem10"] = {
    "state": [randbits(32) for _ in range(8)],
    "round_constant": 0x428A2F98,
    "schedule_word": randbits(32),
}


### The Compression Function

# Problem 11
inputs["problem11"] = {
    "state": [randbits(32) for _ in range(8)],
    "block": random_string(64),
}


### Padding

# Problem 12
inputs["problem12"] = [
    0,
    1,
    55,
    56,
    64,
    secrets.randbits(61),  # not 64, because of the x8 step
]


### The Hash Function

# Problem 13
lyrics = "John Jacob Jingleheimer Schmidt! His name is my name too. Whenever we go out the people always shout there goes John Jacob Jingleheimer Schmidt! Nanananananana..."
inputs["problem13"] = [
    "",
    "hello world",
    random_string(55),
    random_string(56),
    lyrics,
]


### The Length Extension Attack

# Problem 14
inputs["problem14"] = {
    "original_input": random_animals(3),
    "chosen_suffix": random_animals(3),
}

# Problem 15
inputs["problem15"] = secrets.token_bytes(32).hex()

# Problem 16
hidden_input = random_animals(10)
inputs["problem16"] = {
    "original_hash": hashlib.sha256(hidden_input.encode()).hexdigest(),
    "original_len": len(hidden_input),
    "chosen_suffix": random_animals(5),
}


json.dump(inputs, sys.stdout, indent="  ")
print()
