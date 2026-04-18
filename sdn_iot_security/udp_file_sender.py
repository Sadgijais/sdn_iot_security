import argparse
import socket
import time

from udp_transport import build_manifest_packet_with_chunks, build_data_packet
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
    parser.add_argument("--metrics-file", default="transport_metrics.csv", help="CSV file to append sender metrics")
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.file, "rb") as f:
        file_bytes = f.read()

    message_id = args.message_id if args.message_id is not None else int(time.time_ns() & 0xFFFFFFFF)
    manifest, chunks = build_manifest_packet_with_chunks(message_id, file_bytes, args.chunk_size)

    addr = (args.host, args.port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start = time.time()

    try:
        for _ in range(max(1, args.manifest_repeats)):
            sock.sendto(manifest, addr)
            if args.inter_packet_ms > 0:
                time.sleep(args.inter_packet_ms / 1000.0)

        total_chunks = len(chunks)
        for idx, chunk in enumerate(chunks):
            packet = build_data_packet(message_id, idx, total_chunks, chunk)
            sock.sendto(packet, addr)
            if args.inter_packet_ms > 0:
                time.sleep(args.inter_packet_ms / 1000.0)

        elapsed = max(time.time() - start, 1e-9)
        throughput_mbps = (len(file_bytes) * 8) / (elapsed * 1_000_000)
        total_packets = max(1, args.manifest_repeats) + total_chunks

        append_transport_metric(
            args.metrics_file,
            {
                "role": "sender",
                "status": "ok",
                "message_id": message_id,
                "file_path": args.file,
                "bytes": len(file_bytes),
                "chunks": total_chunks,
                "packets": total_packets,
                "elapsed_s": elapsed,
                "throughput_mbps": throughput_mbps,
            },
        )

        print(
            f"Sent file {args.file} to {args.host}:{args.port} "
            f"(message_id={message_id}, chunks={total_chunks}, bytes={len(file_bytes)}, "
            f"elapsed={elapsed:.2f}s, throughput={throughput_mbps:.2f} Mbps)"
        )
    finally:
        sock.close()


if __name__ == "__main__":
    main()
