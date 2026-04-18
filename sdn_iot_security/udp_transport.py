import hashlib
import struct

MANIFEST_MAGIC = b"STGM"
DATA_MAGIC = b"STGD"
VERSION = 1

MANIFEST_FORMAT = "!4sBIIQ32s"
MANIFEST_SIZE = struct.calcsize(MANIFEST_FORMAT)

DATA_HEADER_FORMAT = "!4sBIIIH"
DATA_HEADER_SIZE = struct.calcsize(DATA_HEADER_FORMAT)


class TransportError(Exception):
    pass


def chunk_bytes(data, chunk_size):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]


def build_manifest_packet_with_chunks(message_id, file_bytes, chunk_size):
    chunks = chunk_bytes(file_bytes, chunk_size)
    total_chunks = len(chunks)
    digest = hashlib.sha256(file_bytes).digest()
    packet = struct.pack(
        MANIFEST_FORMAT,
        MANIFEST_MAGIC,
        VERSION,
        message_id,
        total_chunks,
        len(file_bytes),
        digest,
    )
    return packet, chunks


def parse_manifest_packet(packet):
    if len(packet) != MANIFEST_SIZE:
        raise TransportError("Invalid manifest packet size")
    magic, version, message_id, total_chunks, file_size, digest = struct.unpack(MANIFEST_FORMAT, packet)
    if magic != MANIFEST_MAGIC:
        raise TransportError("Invalid manifest magic")
    if version != VERSION:
        raise TransportError("Unsupported transport version")
    return {
        "message_id": message_id,
        "total_chunks": total_chunks,
        "file_size": file_size,
        "digest": digest,
    }


def build_data_packet(message_id, chunk_index, total_chunks, chunk):
    return struct.pack(
        DATA_HEADER_FORMAT,
        DATA_MAGIC,
        VERSION,
        message_id,
        chunk_index,
        total_chunks,
        len(chunk),
    ) + chunk


def parse_data_packet(packet):
    if len(packet) < DATA_HEADER_SIZE:
        raise TransportError("Data packet too short")

    header = packet[:DATA_HEADER_SIZE]
    payload = packet[DATA_HEADER_SIZE:]

    magic, version, message_id, chunk_index, total_chunks, chunk_len = struct.unpack(DATA_HEADER_FORMAT, header)

    if magic != DATA_MAGIC:
        raise TransportError("Invalid data magic")
    if version != VERSION:
        raise TransportError("Unsupported transport version")
    if chunk_len != len(payload):
        raise TransportError("Data packet chunk length mismatch")

    return {
        "message_id": message_id,
        "chunk_index": chunk_index,
        "total_chunks": total_chunks,
        "chunk": payload,
    }


def assemble_chunks(chunks_by_index, total_chunks):
    missing = [i for i in range(total_chunks) if i not in chunks_by_index]
    if missing:
        raise TransportError(f"Missing chunks: {missing[:10]}")
    return b"".join(chunks_by_index[i] for i in range(total_chunks))


def verify_file_digest(file_bytes, expected_digest):
    return hashlib.sha256(file_bytes).digest() == expected_digest
