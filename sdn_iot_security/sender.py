from ecc import generate_keys, generate_shared_key
from aes import encrypt
from stego import embed_data
from utils import pack_encrypted_payload
import os
import time
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Encrypt payload and embed into audio stego file")
    parser.add_argument("--message", default="Secret IoT Data", help="Message to encrypt")
    parser.add_argument("--audio-in", default="input.wav", help="Cover audio input path")
    parser.add_argument("--audio-out", default="stego.wav", help="Stego audio output path")
    parser.add_argument("--key-file", default="shared_key.bin", help="Shared session key file path")
    return parser.parse_args()


def main():
    args = parse_args()

    # Generate or load shared key
    if os.path.exists(args.key_file):
        with open(args.key_file, "rb") as f:
            shared_key = f.read()
    else:
        # Generate ECC keys and derive shared key
        priv1, pub1 = generate_keys()
        priv2, pub2 = generate_keys()
        shared_key = generate_shared_key(priv1, pub2)
        # Save for receiver to use
        with open(args.key_file, "wb") as f:
            f.write(shared_key)

    data = args.message.encode("utf-8")

    # Encrypt and package payload
    nonce, ciphertext, tag = encrypt(data, shared_key)
    message_id = int(time.time_ns() & 0xFFFFFFFF)
    timestamp = int(time.time())

    payload = pack_encrypted_payload(
        message_id=message_id,
        nonce=nonce,
        tag=tag,
        ciphertext=ciphertext,
        timestamp=timestamp,
    )

    # Embed into audio
    embed_data(args.audio_in, args.audio_out, payload, stego_key=shared_key)
    print(f"Data embedded successfully: {args.audio_out}")


if __name__ == "__main__":
    main()