import argparse
import socket
import time

from udp_transport import (
    build_manifest_packet_with_chunks,
    build_data_packet,
    parse_control_packet,
    TransportError,
    CONTROL_TYPE_NACK,
    CONTROL_TYPE_COMPLETE,
)
from net_metrics import append_transport_metric


def parse_args():
    parser = argparse.ArgumentParser(description="Send stego file over UDP with chunking")
    parser.add_argument("--host", default="127.0.0.1", help="Destination host")
    parser.add_argument("--port", type=int, default=6000, help="Destination UDP port")
    parser.add_argument("--file", default="stego.wav", help="File to send")
    parser.add_argument("--chunk-size", type=int, default=1024, help="Chunk payload size")
    parser.add_argument("--message-id", type=int, default=None, help="Optional fixed message id")
    parser.add_argument("--manifest-repeats", type=int, default=3, help="How many times to send manifest")
    parser.add_argument("--inter-packet-ms", type=float, default=1.0, help="Delay between packets")
    parser.add_argument("--control-timeout", type=float, default=15.0, help="How long to wait for retransmit control packets")
    parser.add_argument("--socket-timeout", type=float, default=0.25, help="Socket timeout while waiting for control packets")
    parser.add_argument("--drop-every", type=int, default=0, help="Simulate loss by skipping every Nth chunk on first pass")
    parser.add_argument("--drop-first", type=int, default=0, help="Simulate loss by skipping first K chunks on first pass")
    parser.add_argument(
        "--drop-indices",
        default="",
        help="Comma-separated 0-based chunk indices to drop on first pass (deterministic demo)",
    )
    parser.add_argument("--metrics-file", default="transport_metrics.csv", help="CSV file to append sender metrics")
    return parser.parse_args()


def parse_drop_indices(raw):
    if not raw:
        return set()

    indices = set()
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            idx = int(token)
        except ValueError as exc:
            raise ValueError(f"Invalid --drop-indices value: {token}") from exc
        if idx < 0:
            raise ValueError("--drop-indices only accepts non-negative integers")
        indices.add(idx)

    return indices


def main():
    args = parse_args()
    drop_indices = parse_drop_indices(args.drop_indices)

    with open(args.file, "rb") as f:
        file_bytes = f.read()

    message_id = args.message_id if args.message_id is not None else int(time.time_ns() & 0xFFFFFFFF)
    manifest, chunks = build_manifest_packet_with_chunks(message_id, file_bytes, args.chunk_size)

    addr = (args.host, args.port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(max(0.05, args.socket_timeout))
    start = time.time()
    resent_chunks = 0
    nack_packets = 0
    completion_received = False
    simulated_drops = 0

    try:
        for _ in range(max(1, args.manifest_repeats)):
            sock.sendto(manifest, addr)
            if args.inter_packet_ms > 0:
                time.sleep(args.inter_packet_ms / 1000.0)

        total_chunks = len(chunks)
        for idx, chunk in enumerate(chunks):
            drop_on_first_pass = False
            if args.drop_first > 0 and idx < args.drop_first:
                drop_on_first_pass = True
            elif args.drop_every > 0 and (idx + 1) % args.drop_every == 0:
                drop_on_first_pass = True
            elif idx in drop_indices:
                drop_on_first_pass = True

            if drop_on_first_pass:
                simulated_drops += 1
                continue

            packet = build_data_packet(message_id, idx, total_chunks, chunk)
            sock.sendto(packet, addr)
            if args.inter_packet_ms > 0:
                time.sleep(args.inter_packet_ms / 1000.0)

        control_start = time.time()
        while time.time() - control_start < max(0.0, args.control_timeout):
            try:
                control_packet, _ = sock.recvfrom(65535)
            except socket.timeout:
                continue

            try:
                control = parse_control_packet(control_packet)
            except TransportError:
                continue

            if control["message_id"] != message_id:
                continue

            if control["control_type"] == CONTROL_TYPE_COMPLETE:
                completion_received = True
                break

            if control["control_type"] == CONTROL_TYPE_NACK:
                nack_packets += 1
                missing = control["chunk_indices"]
                for idx in missing:
                    if idx >= total_chunks:
                        continue
                    resend_packet = build_data_packet(message_id, idx, total_chunks, chunks[idx])
                    sock.sendto(resend_packet, addr)
                    resent_chunks += 1
                    if args.inter_packet_ms > 0:
                        time.sleep(args.inter_packet_ms / 1000.0)

        elapsed = max(time.time() - start, 1e-9)
        throughput_mbps = (len(file_bytes) * 8) / (elapsed * 1_000_000)
        total_packets = max(1, args.manifest_repeats) + total_chunks + resent_chunks
        status = "ok" if completion_received else "warning"
        note = (
            f"completion_ack={completion_received};"
            f"nack_packets={nack_packets};resent_chunks={resent_chunks};"
            f"simulated_drops={simulated_drops}"
        )

        append_transport_metric(
            args.metrics_file,
            {
                "role": "sender",
                "status": status,
                "message_id": message_id,
                "file_path": args.file,
                "bytes": len(file_bytes),
                "chunks": total_chunks,
                "packets": total_packets,
                "elapsed_s": elapsed,
                "throughput_mbps": throughput_mbps,
                "note": note,
            },
        )

        print(
            f"Sent file {args.file} to {args.host}:{args.port} "
            f"(message_id={message_id}, chunks={total_chunks}, bytes={len(file_bytes)}, "
            f"simulated_drops={simulated_drops}, resent={resent_chunks}, "
            f"completion_ack={completion_received}, "
            f"elapsed={elapsed:.2f}s, throughput={throughput_mbps:.2f} Mbps)"
        )
    finally:
        sock.close()


if __name__ == "__main__":
    main()
