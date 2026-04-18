import wave
import hashlib
import numpy as np

from utils import bits_required_for_stego

def _seed_from_key(stego_key, purpose):
    if stego_key is None:
        return None
    digest = hashlib.sha256(stego_key + purpose).digest()
    return int.from_bytes(digest[:8], byteorder='big', signed=False)


def _select_indices(frame_count, bit_count, stego_key, purpose, exclude=None):
    if exclude is None:
        exclude = np.array([], dtype=np.int64)

    if stego_key is None:
        # Sequential fallback for compatibility.
        base_indices = np.arange(frame_count, dtype=np.int64)
        if exclude.size > 0:
            mask = np.ones(frame_count, dtype=bool)
            mask[exclude] = False
            base_indices = base_indices[mask]
        if bit_count > len(base_indices):
            raise ValueError("Insufficient indices for embedding")
        return base_indices[:bit_count]

    available = np.arange(frame_count, dtype=np.int64)
    if exclude.size > 0:
        mask = np.ones(frame_count, dtype=bool)
        mask[exclude] = False
        available = available[mask]

    if bit_count > len(available):
        raise ValueError("Insufficient indices for embedding")

    rng = np.random.default_rng(_seed_from_key(stego_key, purpose))
    return rng.choice(available, size=bit_count, replace=False)


def _apply_lsb_matching(samples, bits, stego_key):
    if stego_key is None:
        return (samples & ~1) | bits

    rng = np.random.default_rng(_seed_from_key(stego_key, b"lsb-match"))
    modified = samples.copy()

    mismatch = (modified & 1) != bits
    mismatch_positions = np.where(mismatch)[0]
    if mismatch_positions.size == 0:
        return modified

    direction = rng.integers(0, 2, size=mismatch_positions.size)
    for i, pos in enumerate(mismatch_positions):
        value = int(modified[pos])
        if direction[i] == 0:
            value = value + 1 if value < 32767 else value - 1
        else:
            value = value - 1 if value > -32768 else value + 1
        modified[pos] = value

    return modified


def embed_data(audio_in, audio_out, data, stego_key=None):
    audio = wave.open(audio_in, 'rb')
    frames = np.frombuffer(audio.readframes(audio.getnframes()), dtype=np.int16).copy()

    payload = len(data).to_bytes(4, byteorder='big') + data
    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))

    required_bits = bits_required_for_stego(len(data))
    if required_bits > len(frames):
        audio.close()
        raise ValueError(
            f"Insufficient audio capacity: need {required_bits} samples, have {len(frames)}"
        )

    length_bits = bits[:32]
    payload_bits = bits[32:]

    length_indices = _select_indices(
        len(frames),
        len(length_bits),
        stego_key,
        b"length",
    )
    payload_indices = _select_indices(
        len(frames),
        len(payload_bits),
        stego_key,
        b"payload",
        exclude=length_indices,
    )

    frames[length_indices] = _apply_lsb_matching(frames[length_indices], length_bits, stego_key)
    frames[payload_indices] = _apply_lsb_matching(frames[payload_indices], payload_bits, stego_key)

    modified = frames.tobytes()

    out = wave.open(audio_out, 'wb')
    out.setparams(audio.getparams())
    out.writeframes(modified)
    audio.close()
    out.close()

def extract_data(audio_file, length=None, stego_key=None):
    audio = wave.open(audio_file, 'rb')
    frames = np.frombuffer(audio.readframes(audio.getnframes()), dtype=np.int16)

    if length is None:
        length_indices = _select_indices(len(frames), 32, stego_key, b"length")
        length_bits = (frames[length_indices] & 1).astype(np.uint8)
        payload_length = int.from_bytes(np.packbits(length_bits).tobytes(), byteorder='big')

        total_bits = 32 + (payload_length * 8)
        if total_bits > len(frames):
            audio.close()
            raise ValueError("Invalid payload length in stego file")

        payload_indices = _select_indices(
            len(frames),
            payload_length * 8,
            stego_key,
            b"payload",
            exclude=length_indices,
        )
        payload_bits = (frames[payload_indices] & 1).astype(np.uint8)
        audio.close()
        return np.packbits(payload_bits).tobytes()

    length_indices = _select_indices(len(frames), 32, stego_key, b"length")
    indices = _select_indices(
        len(frames),
        length * 8,
        stego_key,
        b"payload",
        exclude=length_indices,
    )
    bits = (frames[indices] & 1).astype(np.uint8)

    audio.close()
    return np.packbits(bits).tobytes()