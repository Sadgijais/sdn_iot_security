from ecc import generate_keys, generate_shared_key
from aes import encrypt, decrypt
from stego import embed_data, extract_data
from utils import (
    pack_encrypted_payload,
    unpack_encrypted_payload,
    validate_and_update_replay,
)
import time

print("=" * 50)
print("SDN IoT Security Project - Full Demo")
print("=" * 50)

# Step 1: Generate ECC keys (one-time setup)
print("\n[1] Generating ECC key pairs...")
priv1, pub1 = generate_keys()
priv2, pub2 = generate_keys()
print("✓ Keys generated successfully")

# Step 2: Generate shared key
print("\n[2] Generating shared secret key...")
shared_key = generate_shared_key(priv1, pub2)
print(f"✓ Shared key generated: {len(shared_key)} bytes")

# ===== SENDER SIDE =====
print("\n" + "=" * 50)
print("SENDER SIDE - Encrypting & Embedding Data")
print("=" * 50)

# Step 3: Data to be encrypted
data = b"Secret IoT Data"
print(f"\n[3] Original data: {data}")

# Step 4: Encrypt the data
print("\n[4] Encrypting data with AES-GCM...")
nonce, ciphertext, tag = encrypt(data, shared_key)
message_id = int(time.time_ns() & 0xFFFFFFFF)
timestamp = int(time.time())
print(f"✓ Encryption successful")
print(f"  - Nonce: {len(nonce)} bytes")
print(f"  - Ciphertext: {len(ciphertext)} bytes")
print(f"  - Auth Tag: {len(tag)} bytes")
print(f"  - Message ID: {message_id}")
print(f"  - Timestamp: {timestamp}")

# Combine everything
payload = pack_encrypted_payload(
    message_id=message_id,
    nonce=nonce,
    tag=tag,
    ciphertext=ciphertext,
    timestamp=timestamp,
)
print(f"  - Total payload: {len(payload)} bytes")

# Step 5: Embed into audio
print("\n[5] Embedding encrypted data into audio file...")
embed_data("input.wav", "stego.wav", payload, stego_key=shared_key)
print("✓ Data embedded successfully in stego.wav")

# ===== RECEIVER SIDE =====
print("\n" + "=" * 50)
print("RECEIVER SIDE - Extracting & Decrypting Data")
print("=" * 50)

# Step 6: Extract data from audio
print("\n[6] Extracting payload from audio...")
extracted_payload = extract_data("stego.wav", stego_key=shared_key)
print("✓ Data extracted successfully")

# Parse the payload
parsed = unpack_encrypted_payload(extracted_payload)
replay_state = {}
accepted, reason = validate_and_update_replay(
    message_id=parsed["message_id"],
    timestamp=parsed["timestamp"],
    state=replay_state,
)
if not accepted:
    raise ValueError(f"Packet rejected: {reason}")

nonce_extracted = parsed["nonce"]
tag_extracted = parsed["tag"]
ciphertext_extracted = parsed["ciphertext"]

print(f"  - Extracted nonce: {len(nonce_extracted)} bytes")
print(f"  - Extracted tag: {len(tag_extracted)} bytes")
print(f"  - Extracted ciphertext: {len(ciphertext_extracted)} bytes")

# Step 7: Decrypt
print("\n[7] Decrypting data with AES-GCM...")
try:
    recovered_data = decrypt(nonce_extracted, ciphertext_extracted, tag_extracted, shared_key)
    print("✓ Decryption successful!")
    print(f"✓ Recovered data: {recovered_data}")
    
    if recovered_data == data:
        print("\n" + "=" * 50)
        print("SUCCESS! Data integrity verified ✓")
        print("=" * 50)

        print("\n[8] Replay defense check (same packet re-processed)...")
        accepted_replay, replay_reason = validate_and_update_replay(
            message_id=parsed["message_id"],
            timestamp=parsed["timestamp"],
            state=replay_state,
        )
        if accepted_replay:
            print("✗ Replay test failed: duplicate packet was accepted")
        else:
            print(f"✓ Replay blocked successfully: {replay_reason}")
    else:
        print("\n⚠ Warning: Recovered data doesn't match original")
except ValueError as e:
    print(f"✗ Decryption failed: {e}")
    print("  This usually means the shared key is incorrect")
