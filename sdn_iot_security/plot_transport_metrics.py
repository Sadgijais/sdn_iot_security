import argparse
import csv
from pathlib import Path


def parse_note_field(note):
    result = {}
    if not note:
        return result

    parts = [p.strip() for p in note.split(";") if p.strip()]
    for part in parts:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def parse_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


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


def load_rows(metrics_path):
    rows = []
    with open(metrics_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            note_data = parse_note_field(row.get("note", ""))
            rows.append(
                {
                    "timestamp": to_int(row.get("timestamp", 0)),
                    "role": row.get("role", ""),
                    "status": row.get("status", ""),
                    "message_id": row.get("message_id", ""),
                    "bytes": to_int(row.get("bytes", 0)),
                    "chunks": to_int(row.get("chunks", 0)),
                    "packets": to_int(row.get("packets", 0)),
                    "elapsed_s": to_float(row.get("elapsed_s", 0.0)),
                    "throughput_mbps": to_float(row.get("throughput_mbps", 0.0)),
                    "nack_packets": to_int(note_data.get("nack_packets", 0)),
                    "resent_chunks": to_int(note_data.get("resent_chunks", 0)),
                    "simulated_drops": to_int(note_data.get("simulated_drops", 0)),
                    "nacks_sent": to_int(note_data.get("nacks_sent", 0)),
                    "completion_ack": parse_bool(note_data.get("completion_ack", "false")),
                }
            )
    return rows


def print_summary(rows):
    sender_rows = [r for r in rows if r["role"] == "sender"]
    receiver_rows = [r for r in rows if r["role"] == "receiver"]

    total_runs = len(rows)
    sender_ok = sum(1 for r in sender_rows if r["status"] == "ok")
    receiver_ok = sum(1 for r in receiver_rows if r["status"] == "ok")

    total_resent = sum(r["resent_chunks"] for r in sender_rows)
    total_simulated_drops = sum(r["simulated_drops"] for r in sender_rows)
    total_nack_packets = sum(r["nack_packets"] for r in sender_rows)
    total_nacks_sent = sum(r["nacks_sent"] for r in receiver_rows)

    avg_sender_tp = (
        sum(r["throughput_mbps"] for r in sender_rows) / len(sender_rows)
        if sender_rows
        else 0.0
    )
    avg_receiver_tp = (
        sum(r["throughput_mbps"] for r in receiver_rows) / len(receiver_rows)
        if receiver_rows
        else 0.0
    )

    completion_acks = sum(1 for r in sender_rows if r["completion_ack"])

    print("=== Transport Metrics Summary ===")
    print(f"Rows: {total_runs}")
    print(f"Sender rows: {len(sender_rows)} (ok={sender_ok})")
    print(f"Receiver rows: {len(receiver_rows)} (ok={receiver_ok})")
    print(f"Completion ACKs seen by sender: {completion_acks}/{len(sender_rows) if sender_rows else 0}")
    print(f"Total simulated drops: {total_simulated_drops}")
    print(f"Total resent chunks: {total_resent}")
    print(f"Total NACK packets received by sender: {total_nack_packets}")
    print(f"Total NACK packets sent by receiver: {total_nacks_sent}")
    print(f"Average sender throughput: {avg_sender_tp:.3f} Mbps")
    print(f"Average receiver throughput: {avg_receiver_tp:.3f} Mbps")


def save_plot(rows, out_png):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover
        print("Matplotlib is not installed; skipping plot generation.")
        print(f"Reason: {exc}")
        print("Install it with: pip install matplotlib")
        return False

    sender_rows = [r for r in rows if r["role"] == "sender"]
    receiver_rows = [r for r in rows if r["role"] == "receiver"]

    sender_x = list(range(1, len(sender_rows) + 1))
    receiver_x = list(range(1, len(receiver_rows) + 1))

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), constrained_layout=True)

    axes[0].plot(
        sender_x,
        [r["throughput_mbps"] for r in sender_rows],
        marker="o",
        label="Sender throughput (Mbps)",
    )
    axes[0].plot(
        receiver_x,
        [r["throughput_mbps"] for r in receiver_rows],
        marker="s",
        label="Receiver throughput (Mbps)",
    )
    axes[0].set_title("Transport Throughput by Run")
    axes[0].set_xlabel("Run index")
    axes[0].set_ylabel("Mbps")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    axes[1].bar(
        sender_x,
        [r["simulated_drops"] for r in sender_rows],
        alpha=0.7,
        label="Simulated drops",
    )
    axes[1].bar(
        sender_x,
        [r["resent_chunks"] for r in sender_rows],
        alpha=0.7,
        label="Resent chunks",
    )
    axes[1].plot(
        sender_x,
        [r["nack_packets"] for r in sender_rows],
        marker="^",
        linewidth=1.5,
        label="NACK packets",
    )
    axes[1].set_title("Reliability Events by Run")
    axes[1].set_xlabel("Sender run index")
    axes[1].set_ylabel("Count")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    return True


def parse_args():
    parser = argparse.ArgumentParser(description="Summarize and plot UDP transport reliability metrics")
    parser.add_argument("--metrics", default="transport_metrics.csv", help="Path to metrics CSV")
    parser.add_argument("--out", default="transport_metrics_plot.png", help="Path to output PNG plot")
    return parser.parse_args()


def main():
    args = parse_args()
    metrics_path = Path(args.metrics)
    out_png = Path(args.out)

    if not metrics_path.exists():
        raise FileNotFoundError(f"Metrics file not found: {metrics_path}")

    rows = load_rows(metrics_path)
    if not rows:
        raise RuntimeError("Metrics file has no data rows")

    print_summary(rows)
    created = save_plot(rows, out_png)
    if created:
        print(f"Plot written: {out_png}")


if __name__ == "__main__":
    main()
