import argparse
import csv
import os
import subprocess
import sys
import time
from pathlib import Path


def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_note_field(note):
    out = {}
    if not note:
        return out
    for part in note.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def parse_metrics(metrics_file):
    sender = None
    receiver = None

    with open(metrics_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            role = row.get("role", "")
            note = parse_note_field(row.get("note", ""))
            normalized = {
                "status": row.get("status", ""),
                "bytes": to_int(row.get("bytes", 0)),
                "chunks": to_int(row.get("chunks", 0)),
                "packets": to_int(row.get("packets", 0)),
                "elapsed_s": to_float(row.get("elapsed_s", 0.0)),
                "throughput_mbps": to_float(row.get("throughput_mbps", 0.0)),
                "completion_ack": str(note.get("completion_ack", "false")).lower() == "true",
                "nack_packets": to_int(note.get("nack_packets", 0)),
                "resent_chunks": to_int(note.get("resent_chunks", 0)),
                "simulated_drops": to_int(note.get("simulated_drops", 0)),
                "nacks_sent": to_int(note.get("nacks_sent", 0)),
            }
            if role == "sender":
                sender = normalized
            elif role == "receiver":
                receiver = normalized

    return sender, receiver


def write_run_csv(rows, out_file):
    fields = [
        "run",
        "sender_status",
        "receiver_status",
        "completion_ack",
        "simulated_drops",
        "resent_chunks",
        "nack_packets",
        "nacks_sent",
        "sender_throughput_mbps",
        "receiver_throughput_mbps",
        "file_verified",
    ]

    with open(out_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def print_summary(rows):
    if not rows:
        print("No experiment rows generated")
        return

    ok_runs = sum(1 for r in rows if r["file_verified"] == 1)
    completion_acks = sum(1 for r in rows if r["completion_ack"] == 1)
    total_drops = sum(r["simulated_drops"] for r in rows)
    total_resent = sum(r["resent_chunks"] for r in rows)
    total_nack_packets = sum(r["nack_packets"] for r in rows)
    total_nacks_sent = sum(r["nacks_sent"] for r in rows)
    avg_sender_tp = sum(r["sender_throughput_mbps"] for r in rows) / len(rows)
    avg_receiver_tp = sum(r["receiver_throughput_mbps"] for r in rows) / len(rows)

    print("=== Reliability Experiment Summary ===")
    print(f"Runs: {len(rows)}")
    print(f"Verified runs (file match): {ok_runs}/{len(rows)}")
    print(f"Completion ACK observed: {completion_acks}/{len(rows)}")
    print(f"Total simulated drops: {total_drops}")
    print(f"Total resent chunks: {total_resent}")
    print(f"Total NACK packets (sender view): {total_nack_packets}")
    print(f"Total NACK packets (receiver view): {total_nacks_sent}")
    print(f"Average sender throughput: {avg_sender_tp:.3f} Mbps")
    print(f"Average receiver throughput: {avg_receiver_tp:.3f} Mbps")


def parse_args():
    parser = argparse.ArgumentParser(description="Run repeatable UDP reliability experiments")
    parser.add_argument("--runs", type=int, default=3, help="Number of experiment runs")
    parser.add_argument("--base-port", type=int, default=6200, help="Base UDP port used for run 1")
    parser.add_argument("--file-size", type=int, default=120000, help="Random payload size in bytes")
    parser.add_argument("--chunk-size", type=int, default=800, help="Chunk size for sender")
    parser.add_argument("--timeout", type=float, default=15.0, help="Receiver timeout in seconds")
    parser.add_argument("--nack-interval-ms", type=float, default=80.0, help="Receiver NACK interval")
    parser.add_argument("--drop-every", type=int, default=0, help="Sender drop-every mode")
    parser.add_argument("--drop-first", type=int, default=0, help="Sender drop-first mode")
    parser.add_argument("--drop-indices", default="3,7,11", help="Sender deterministic drop indices")
    parser.add_argument("--inter-packet-ms", type=float, default=0.0, help="Sender inter-packet delay")
    parser.add_argument("--control-timeout", type=float, default=5.0, help="Sender control wait timeout")
    parser.add_argument("--results", default="experiment_results.csv", help="Output CSV for per-run summary")
    parser.add_argument("--keep-artifacts", action="store_true", help="Keep temporary payload/output/metric files")
    return parser.parse_args()


def main():
    args = parse_args()
    base = Path(__file__).resolve().parent
    rows = []

    for run_id in range(1, args.runs + 1):
        port = args.base_port + run_id - 1

        src = base / f"_exp_src_{run_id}.bin"
        out = base / f"_exp_out_{run_id}.bin"
        metrics = base / f"_exp_metrics_{run_id}.csv"

        for p in (src, out, metrics):
            if p.exists():
                p.unlink()

        src.write_bytes(os.urandom(args.file_size))

        receiver_cmd = [
            sys.executable,
            "udp_file_receiver.py",
            "--port",
            str(port),
            "--out",
            out.name,
            "--timeout",
            str(args.timeout),
            "--nack-interval-ms",
            str(args.nack_interval_ms),
            "--metrics-file",
            metrics.name,
        ]

        sender_cmd = [
            sys.executable,
            "udp_file_sender.py",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--file",
            src.name,
            "--chunk-size",
            str(args.chunk_size),
            "--inter-packet-ms",
            str(args.inter_packet_ms),
            "--control-timeout",
            str(args.control_timeout),
            "--drop-every",
            str(args.drop_every),
            "--drop-first",
            str(args.drop_first),
            "--drop-indices",
            args.drop_indices,
            "--metrics-file",
            metrics.name,
        ]

        receiver = subprocess.Popen(
            receiver_cmd,
            cwd=base,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        time.sleep(0.4)

        sender = subprocess.Popen(
            sender_cmd,
            cwd=base,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        sender_out, sender_err = sender.communicate(timeout=max(20, int(args.timeout) + 10))
        receiver_out, receiver_err = receiver.communicate(timeout=max(20, int(args.timeout) + 10))

        sender_data, receiver_data = parse_metrics(metrics)

        file_verified = int(out.exists() and src.read_bytes() == out.read_bytes())

        row = {
            "run": run_id,
            "sender_status": (sender_data or {}).get("status", "error"),
            "receiver_status": (receiver_data or {}).get("status", "error"),
            "completion_ack": int((sender_data or {}).get("completion_ack", False)),
            "simulated_drops": (sender_data or {}).get("simulated_drops", 0),
            "resent_chunks": (sender_data or {}).get("resent_chunks", 0),
            "nack_packets": (sender_data or {}).get("nack_packets", 0),
            "nacks_sent": (receiver_data or {}).get("nacks_sent", 0),
            "sender_throughput_mbps": (sender_data or {}).get("throughput_mbps", 0.0),
            "receiver_throughput_mbps": (receiver_data or {}).get("throughput_mbps", 0.0),
            "file_verified": file_verified,
        }
        rows.append(row)

        print(f"Run {run_id} sender rc={sender.returncode} receiver rc={receiver.returncode} verified={bool(file_verified)}")
        if sender_out.strip():
            print(f"  sender: {sender_out.strip()}")
        if receiver_out.strip():
            print(f"  receiver: {receiver_out.strip()}")
        if sender_err.strip():
            print(f"  sender err: {sender_err.strip()}")
        if receiver_err.strip():
            print(f"  receiver err: {receiver_err.strip()}")

        if not args.keep_artifacts:
            for p in (src, out, metrics):
                if p.exists():
                    p.unlink()

    out_file = base / args.results
    write_run_csv(rows, out_file)
    print(f"Per-run results written: {out_file}")
    print_summary(rows)


if __name__ == "__main__":
    main()
