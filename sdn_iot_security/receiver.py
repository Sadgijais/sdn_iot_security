from aes import decrypt
from stego import extract_data
from utils import (
    unpack_encrypted_payload,
    load_replay_state,
    save_replay_state,
    validate_and_update_replay,
)
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Extract and decrypt payload from stego audio")
    parser.add_argument("--stego-file", default="stego.wav", help="Stego audio file path")
    parser.add_argument("--key-file", default="shared_key.bin", help="Shared session key file path")
    parser.add_argument("--replay-state", default="replay_state.json", help="Replay state file path")
    return parser.parse_args()


def main():
    args = parse_args()

    # Load shared key (must be created by sender first)
    if not os.path.exists(args.key_file):
        raise FileNotFoundError(f"{args.key_file} not found. Run sender.py first!")

    with open(args.key_file, "rb") as f:
        shared_key = f.read()

    # Extract data from the built-in length prefix
    payload = extract_data(args.stego_file, stego_key=shared_key)
    parsed = unpack_encrypted_payload(payload)

    replay_state = load_replay_state(args.replay_state)
    accepted, reason = validate_and_update_replay(
        message_id=parsed["message_id"],
        timestamp=parsed["timestamp"],
        state=replay_state,
    )
    if not accepted:
        raise ValueError(f"Packet rejected: {reason}")
    save_replay_state(args.replay_state, replay_state)

    nonce = parsed["nonce"]
    tag = parsed["tag"]
    ciphertext = parsed["ciphertext"]

    # Decrypt
    data = decrypt(nonce, ciphertext, tag, shared_key)

    print("Recovered:", data)

if __name__ == "__main__":
    main()