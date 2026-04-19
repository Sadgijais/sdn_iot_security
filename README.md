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
