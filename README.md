# SDN IoT Security Project

This repository contains a secure IoT communication prototype that combines cryptography, steganography, replay protection, UDP file transport, and SDN routing components.

## What This Project Demonstrates

- ECC key exchange (ECDH) with HKDF-SHA256 key derivation
- AES-256-GCM encryption with authentication
- WAV audio steganography (pseudo-random LSB matching)
- Replay protection using message IDs and timestamps
- UDP chunked file transport with integrity verification (SHA-256)
- Transport metrics logging for evaluation
- SDN-ready topology and multipath controller for Mininet/WSL

## Repository Layout

- `sdn_iot_security/`: main project source and runbooks
- `.gitignore`: repository-level ignore rules

## Beginner Entry Point

If you are new to the project, start with:

- `sdn_iot_security/START_HERE_GUIDE.md`

## Quick Start

### 1) Open the project directory

```powershell
cd "C:\Users\user_name\OneDrive\Desktop\CN Project"
```

### 2) Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 3) Run local end-to-end demo

```powershell
cd sdn_iot_security
python main.py
```

## Useful Scripts (inside sdn_iot_security)

- `sender.py` and `receiver.py`: secure payload generation and recovery
- `udp_file_sender.py` and `udp_file_receiver.py`: UDP transport for stego files
- `sdn_topology.py`: Mininet topology
- `ryu_multipath_controller.py`: SDN controller logic (Ryu/OS-Ken compatible)

## Reliable UDP Transfer (New)

The UDP file transport now includes a control channel for reliability:

- Receiver sends `NACK` packets listing missing chunk indices.
- Sender retransmits only requested missing chunks.
- Receiver sends `COMPLETE` ACK after digest verification.

Example local run:

```powershell
cd sdn_iot_security

# Terminal 1
python udp_file_receiver.py --port 6000 --out received_stego.wav --timeout 30 --nack-interval-ms 200

# Terminal 2
python udp_file_sender.py --host 127.0.0.1 --port 6000 --file stego.wav --control-timeout 15
```

### Forced Loss Demo (Shows Retransmission)

Use sender-side loss simulation to force NACK and resend behavior:

```powershell
cd sdn_iot_security

# Terminal 1
python udp_file_receiver.py --port 6000 --out received_stego.wav --timeout 30 --nack-interval-ms 100

# Terminal 2
python udp_file_sender.py --host 127.0.0.1 --port 6000 --file stego.wav --drop-every 10 --control-timeout 15
```

Expected sender output includes non-zero `simulated_drops` and `resent` values.

### Deterministic Loss Demo (Repeatable Screenshots)

Use fixed chunk indices for consistent retransmission behavior across runs:

```powershell
cd sdn_iot_security

# Terminal 1
python udp_file_receiver.py --port 6000 --out received_stego.wav --timeout 30 --nack-interval-ms 100

# Terminal 2
python udp_file_sender.py --host 127.0.0.1 --port 6000 --file stego.wav --drop-indices 3,7,11,19 --control-timeout 15
```

### Metrics Plotting

After one or more runs, generate a summary and plot from `transport_metrics.csv`:

```powershell
cd sdn_iot_security
python plot_transport_metrics.py --metrics transport_metrics.csv --out transport_metrics_plot.png
```

If Matplotlib is missing, install it:

```powershell
pip install matplotlib
```

### Automated Reliability Experiment (Multi-run)

Run repeatable experiments and export a per-run results table:

```powershell
cd sdn_iot_security
python run_reliability_experiment.py --runs 5 --drop-indices 3,7,11,19 --results experiment_results.csv
```

This writes `experiment_results.csv` and prints a summary including completion ACK count, total resent chunks, and average throughput.

## SDN Demo Notes

A complete live SDN demo requires Ubuntu WSL/Mininet controller runtime setup. See project runbooks in `sdn_iot_security/`:

- `SDN_RUNBOOK.md`
- `WSL_SDN_CHECKLIST.md`
- `THREE_TERMINAL_LAUNCH.md`

## Requirements

Use `requirements.txt` at repository root to recreate the current Python environment:

```powershell
pip install -r requirements.txt
```
