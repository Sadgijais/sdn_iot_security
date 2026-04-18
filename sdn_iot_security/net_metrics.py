import csv
import os
import time


def append_transport_metric(metrics_file, row):
    if not metrics_file:
        return

    fields = [
        "timestamp",
        "role",
        "status",
        "message_id",
        "file_path",
        "bytes",
        "chunks",
        "packets",
        "elapsed_s",
        "throughput_mbps",
        "note",
    ]

    exists = os.path.exists(metrics_file)
    with open(metrics_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not exists:
            writer.writeheader()

        payload = {
            "timestamp": int(time.time()),
            "role": row.get("role", "unknown"),
            "status": row.get("status", "ok"),
            "message_id": row.get("message_id", ""),
            "file_path": row.get("file_path", ""),
            "bytes": row.get("bytes", 0),
            "chunks": row.get("chunks", 0),
            "packets": row.get("packets", 0),
            "elapsed_s": f"{float(row.get('elapsed_s', 0.0)):.6f}",
            "throughput_mbps": f"{float(row.get('throughput_mbps', 0.0)):.6f}",
            "note": row.get("note", ""),
        }
        writer.writerow(payload)
