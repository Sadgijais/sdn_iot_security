import argparse
import socket
import time

from udp_transport import (
    MANIFEST_SIZE,
    parse_manifest_packet,
    parse_data_packet,
    assemble_chunks,
    verify_file_digest,
    TransportError,
)
from net_metrics import append_transport_metric


def parse_args():
    parser = argparse.ArgumentParser(description="Receive stego file over UDP and reassemble")
    parser.add_argument("--bind-host", default="0.0.0.0", help="Bind host")
    parser.add_argument("--port", type=int, default=6000, help="UDP listen port")
    parser.add_argument("--out", default="received_stego.wav", help="Output file path")
    parser.add_argument("--timeout", type=float, default=30.0, help="Total receive timeout in seconds")
    parser.add_argument("--metrics-file", default="transport_metrics.csv", help="CSV file to append receiver metrics")
    return parser.parse_args()


def main():
    args = parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.bind_host, args.port))
    sock.settimeout(1.0)

    start = time.time()
    manifest = None
    chunks = {}
    packet_count = 0

    print(f"Listening on {args.bind_host}:{args.port} ...")

    try:
        while time.time() - start < args.timeout:
            try:
                packet, _ = sock.recvfrom(65535)
            except socket.timeout:
                continue

            packet_count += 1

            try:
                if len(packet) == MANIFEST_SIZE:
                    parsed_manifest = parse_manifest_packet(packet)
                    if manifest is None:
                        manifest = parsed_manifest
                        print(
                            f"Manifest received: message_id={manifest['message_id']} "
                            f"chunks={manifest['total_chunks']} bytes={manifest['file_size']}"
                        )
                    continue

                data = parse_data_packet(packet)
            except TransportError:
                continue

            if manifest is None:
                continue

            if data["message_id"] != manifest["message_id"]:
                continue

            if data["total_chunks"] != manifest["total_chunks"]:
                continue

            chunks[data["chunk_index"]] = data["chunk"]

            if len(chunks) >= manifest["total_chunks"]:
                break

        if manifest is None:
            append_transport_metric(
                args.metrics_file,
                {
                    "role": "receiver",
                    "status": "error",
                    "message_id": "",
                    "file_path": args.out,
                    "bytes": 0,
                    "chunks": 0,
                    "packets": packet_count,
                    "elapsed_s": time.time() - start,
                    "throughput_mbps": 0.0,
                    "note": "No manifest packet received",
                },
            )
            raise RuntimeError("No manifest packet received")

        file_bytes = assemble_chunks(chunks, manifest["total_chunks"])
        file_bytes = file_bytes[: manifest["file_size"]]

        if not verify_file_digest(file_bytes, manifest["digest"]):
            raise RuntimeError("Digest verification failed for received file")

        with open(args.out, "wb") as f:
            f.write(file_bytes)

        elapsed = time.time() - start
        throughput_mbps = (len(file_bytes) * 8) / (max(elapsed, 1e-9) * 1_000_000)
        append_transport_metric(
            args.metrics_file,
            {
                "role": "receiver",
                "status": "ok",
                "message_id": manifest["message_id"],
                "file_path": args.out,
                "bytes": len(file_bytes),
                "chunks": len(chunks),
                "packets": packet_count,
                "elapsed_s": elapsed,
                "throughput_mbps": throughput_mbps,
            },
        )
        print(
            f"Received file -> {args.out} "
            f"(packets={packet_count}, chunks={len(chunks)}, elapsed={elapsed:.2f}s, "
            f"throughput={throughput_mbps:.2f} Mbps)"
        )
    finally:
        sock.close()


if __name__ == "__main__":
    main()
