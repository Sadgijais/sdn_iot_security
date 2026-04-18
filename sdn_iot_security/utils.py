import struct
import json
import os
import time


ENVELOPE_HEADER_FORMAT = "!BIQHHI"
ENVELOPE_HEADER_SIZE = struct.calcsize(ENVELOPE_HEADER_FORMAT)
LENGTH_PREFIX_SIZE = 4  # bytes used by stego layer to store payload length
REPLAY_WINDOW_SECONDS = 120


def pack_encrypted_payload(message_id, nonce, tag, ciphertext, version=1, timestamp=None):
	if timestamp is None:
		timestamp = int(time.time())

	header = struct.pack(
		ENVELOPE_HEADER_FORMAT,
		version,
		message_id,
		timestamp,
		len(nonce),
		len(tag),
		len(ciphertext),
	)
	return header + nonce + tag + ciphertext


def unpack_encrypted_payload(payload):
	if len(payload) < ENVELOPE_HEADER_SIZE:
		raise ValueError("Payload is too short to contain envelope header")

	version, message_id, timestamp, nonce_len, tag_len, ciphertext_len = struct.unpack(
		ENVELOPE_HEADER_FORMAT,
		payload[:ENVELOPE_HEADER_SIZE],
	)

	expected_size = ENVELOPE_HEADER_SIZE + nonce_len + tag_len + ciphertext_len
	if len(payload) != expected_size:
		raise ValueError("Payload size does not match envelope metadata")

	start = ENVELOPE_HEADER_SIZE
	nonce = payload[start:start + nonce_len]
	start += nonce_len
	tag = payload[start:start + tag_len]
	start += tag_len
	ciphertext = payload[start:start + ciphertext_len]

	return {
		"version": version,
		"message_id": message_id,
		"timestamp": timestamp,
		"nonce": nonce,
		"tag": tag,
		"ciphertext": ciphertext,
	}


def bits_required_for_stego(payload_size_bytes):
	return (LENGTH_PREFIX_SIZE + payload_size_bytes) * 8


def load_replay_state(state_file):
	if not os.path.exists(state_file):
		return {}
	with open(state_file, "r", encoding="utf-8") as file:
		return json.load(file)


def save_replay_state(state_file, state):
	with open(state_file, "w", encoding="utf-8") as file:
		json.dump(state, file)


def validate_and_update_replay(
	message_id,
	timestamp,
	state,
	now=None,
	window_seconds=REPLAY_WINDOW_SECONDS,
):
	if now is None:
		now = int(time.time())

	if abs(now - int(timestamp)) > window_seconds:
		return False, "Stale or future-dated packet timestamp"

	seen = state.setdefault("seen_messages", {})

	# Prune old entries so replay-state size remains bounded.
	expiry_threshold = now - window_seconds
	pruned = {
		str(msg_id): int(ts)
		for msg_id, ts in seen.items()
		if int(ts) >= expiry_threshold
	}
	state["seen_messages"] = pruned

	key = str(int(message_id))
	if key in state["seen_messages"]:
		return False, "Replay detected: duplicate message_id in active window"

	state["seen_messages"][key] = int(timestamp)
	return True, "Packet accepted"
