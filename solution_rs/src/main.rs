use serde::{Deserialize, Serialize};
use std::convert::TryInto;

type State = [u32; 8];
type Block = [u8; 64];
type Hash = [u8; 32];

const IV: [u32; 8] = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
];

const ROUND_CONSTANTS: [u32; 64] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

fn add32(a: u32, b: u32) -> u32 {
    a.wrapping_add(b)
}

fn rightrotate32(x: u32, n: u32) -> u32 {
    // The right operand of >> or << must always be within 0..=31.
    (x >> (n % 32)) | (x << ((32 - n) % 32))
}

fn little_sigma0(x: u32) -> u32 {
    rightrotate32(x, 7) ^ rightrotate32(x, 18) ^ (x >> 3)
}

fn little_sigma1(x: u32) -> u32 {
    rightrotate32(x, 17) ^ rightrotate32(x, 19) ^ (x >> 10)
}

fn message_schedule(block: &Block) -> [u32; 64] {
    let mut w = [0; 64];
    for i in 0..16 {
        w[i] = u32::from_be_bytes(block[4 * i..][..4].try_into().unwrap());
    }
    for i in 16..64 {
        w[i] = w[i - 16].wrapping_add(
            little_sigma0(w[i - 15]).wrapping_add(w[i - 7].wrapping_add(little_sigma1(w[i - 2]))),
        )
    }
    w
}

fn big_sigma0(x: u32) -> u32 {
    rightrotate32(x, 2) ^ rightrotate32(x, 13) ^ rightrotate32(x, 22)
}

fn big_sigma1(x: u32) -> u32 {
    rightrotate32(x, 6) ^ rightrotate32(x, 11) ^ rightrotate32(x, 25)
}

fn choice(x: u32, y: u32, z: u32) -> u32 {
    (x & y) ^ (!x & z)
}

fn majority(x: u32, y: u32, z: u32) -> u32 {
    (x & y) ^ (x & z) ^ (y & z)
}

fn round(state: &State, round_constant: u32, schedule_word: u32) -> State {
    let ch = choice(state[4], state[5], state[6]);
    let temp1 = add32(
        add32(
            add32(add32(state[7], big_sigma1(state[4])), ch),
            round_constant,
        ),
        schedule_word,
    );
    let maj = majority(state[0], state[1], state[2]);
    let temp2 = add32(big_sigma0(state[0]), maj);
    [
        add32(temp1, temp2),
        state[0],
        state[1],
        state[2],
        add32(state[3], temp1),
        state[4],
        state[5],
        state[6],
    ]
}

fn compress(input_state: &State, block: &Block) -> State {
    let w = message_schedule(block);
    let mut state = *input_state;
    for i in 0..64 {
        state = round(&state, ROUND_CONSTANTS[i], w[i]);
    }
    [
        add32(input_state[0], state[0]),
        add32(input_state[1], state[1]),
        add32(input_state[2], state[2]),
        add32(input_state[3], state[3]),
        add32(input_state[4], state[4]),
        add32(input_state[5], state[5]),
        add32(input_state[6], state[6]),
        add32(input_state[7], state[7]),
    ]
}

fn padding(input_length: u64) -> Vec<u8> {
    let mut padding_bytes = vec![0x80];
    let remainder_bytes = (input_length + 8) % 64;
    let filler_bytes = 64 - remainder_bytes;
    let zero_bytes = filler_bytes - 1;
    for _ in 0..zero_bytes {
        padding_bytes.push(0);
    }
    padding_bytes.extend_from_slice(&(8 * input_length).to_be_bytes());
    padding_bytes
}

fn hash_from_state(state: &State) -> Hash {
    let mut hash = [0; 32];
    for i in 0..8 {
        hash[4 * i..][..4].copy_from_slice(&state[i].to_be_bytes());
    }
    hash
}

fn sha256(message: &[u8]) -> Hash {
    let mut padded_message = message.to_vec();
    padded_message.extend_from_slice(&padding(message.len() as u64));
    assert_eq!(0, padded_message.len() % 64);
    let mut state = IV;
    for block in padded_message.chunks(64) {
        state = compress(&state, block.try_into().unwrap());
    }
    hash_from_state(&state)
}

#[test]
fn test_sha256() {
    // The sha2 dependency is only used right here, for testing.
    use sha2::{Digest, Sha256};
    for i in 0..1000 {
        dbg!(i);
        let input = vec![i as u8; i];
        let my_hash = sha256(&input);
        let mut standard_hasher = Sha256::new();
        standard_hasher.update(&input);
        let expected = standard_hasher.finalize();
        assert_eq!(my_hash[..], expected[..]);
    }
}

fn recover_state(hash: &Hash) -> State {
    let mut state = [0; 8];
    for i in 0..8 {
        state[i] = u32::from_be_bytes(hash[4 * i..][..4].try_into().unwrap());
    }
    state
}

fn length_extend(original_hash: &Hash, original_len: u64, chosen_suffix: &[u8]) -> Hash {
    let mut state = recover_state(original_hash);
    let mut padded_suffix = chosen_suffix.to_vec();
    let synthetic_len =
        original_len + padding(original_len).len() as u64 + chosen_suffix.len() as u64;
    padded_suffix.extend_from_slice(&padding(synthetic_len));
    for block in padded_suffix.chunks(64) {
        state = compress(&state, block.try_into().unwrap());
    }
    hash_from_state(&state)
}

#[derive(Deserialize)]
struct Input {
    problem1: Vec<(u32, u32)>,
    problem2: Vec<(u32, u32)>,
    problem3: u32,
    problem4: u32,
    problem5: String,
    problem6: u32,
    problem7: u32,
    problem8: (u32, u32, u32),
    problem9: (u32, u32, u32),
    problem10: Problem10Input,
    problem11: Problem11Input,
    problem12: Vec<u64>,
    problem13: Vec<String>,
    problem14: Problem14Input,
    problem15: String,
    problem16: Problem16Input,
}

#[derive(Deserialize)]
struct Problem10Input {
    state: State,
    round_constant: u32,
    schedule_word: u32,
}

#[derive(Deserialize)]
struct Problem11Input {
    state: State,
    block: String,
}

#[derive(Deserialize)]
struct Problem14Input {
    original_input: String,
    chosen_suffix: String,
}

#[derive(Deserialize)]
struct Problem16Input {
    original_hash: String,
    original_len: u64,
    chosen_suffix: String,
}

#[derive(Default, Serialize)]
struct Output {
    problem1: Vec<u32>,
    problem2: Vec<u32>,
    problem3: u32,
    problem4: u32,
    problem5: Vec<u32>,
    problem6: u32,
    problem7: u32,
    problem8: u32,
    problem9: u32,
    problem10: State,
    problem11: State,
    problem12: Vec<String>,
    problem13: Vec<String>,
    problem14: String,
    problem15: State,
    problem16: String,
}

fn main() {
    let input: Input = serde_json::from_reader(std::io::stdin()).expect("parsing JSON failed");
    let mut output = Output::default();

    // Problem 1
    output.problem1 = input.problem1.iter().map(|&(a, b)| add32(a, b)).collect();

    // Problem 2
    output.problem2 = input
        .problem2
        .iter()
        .map(|&(x, n)| rightrotate32(x, n))
        .collect();

    output.problem3 = little_sigma0(input.problem3);

    output.problem4 = little_sigma1(input.problem4);

    output.problem5 = message_schedule(input.problem5.as_bytes().try_into().unwrap()).to_vec();

    output.problem6 = big_sigma0(input.problem6);

    output.problem7 = big_sigma1(input.problem7);

    let (a, b, c) = input.problem8;
    output.problem8 = choice(a, b, c);

    let (a, b, c) = input.problem9;
    output.problem9 = majority(a, b, c);

    output.problem10 = round(
        &input.problem10.state,
        input.problem10.round_constant,
        input.problem10.schedule_word,
    );

    output.problem11 = compress(
        &input.problem11.state,
        input.problem11.block.as_bytes().try_into().unwrap(),
    );

    output.problem12 = input
        .problem12
        .iter()
        .map(|&len| hex::encode(padding(len)))
        .collect();

    output.problem13 = input
        .problem13
        .iter()
        .map(|s| hex::encode(sha256(s.as_bytes())))
        .collect();

    let mut synthetic = Vec::new();
    synthetic.extend_from_slice(input.problem14.original_input.as_bytes());
    synthetic.extend_from_slice(&padding(input.problem14.original_input.len() as u64));
    synthetic.extend_from_slice(input.problem14.chosen_suffix.as_bytes());
    output.problem14 = hex::encode(&synthetic);

    output.problem15 = recover_state(
        hex::decode(input.problem15).unwrap()[..]
            .try_into()
            .unwrap(),
    );

    let original_hash: Hash = hex::decode(input.problem16.original_hash)
        .unwrap()
        .try_into()
        .unwrap();
    output.problem16 = hex::encode(length_extend(
        &original_hash,
        input.problem16.original_len,
        input.problem16.chosen_suffix.as_bytes(),
    ));

    serde_json::to_writer_pretty(std::io::stdout(), &output).expect("output failed");
    println!()
}
