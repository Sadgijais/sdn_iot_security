# Start Here Guide (Beginner Friendly)

This file is for first-time users who want to run the project without networking background.

## 1) What this project does in simple words

You type a message.
The project encrypts it, hides it inside an audio file, sends that file over UDP, recovers it on receiver side, and decrypts it back.

Main result you should see:
Recovered: b'Your message here'

## 2) Where to run commands

Run all local demo commands in Windows PowerShell from this folder:
C:\Users\sadgi\OneDrive\Desktop\CN Project\sdn_iot_security

If you run SDN Mininet demo, use Ubuntu WSL terminals and the SDN runbooks.

## 3) One-time setup

Open PowerShell and run:

1. cd C:\Users\sadgi\OneDrive\Desktop\CN Project
2. .\venv\Scripts\Activate.ps1
3. cd sdn_iot_security

Optional package check:
python -m pip install -r ..\requirements.txt

## 4) Full project run (recommended order)

Use 2 PowerShell terminals for transfer steps.

### Step A: Create secure stego file

Run in Terminal 1:
python sender.py --message "Hello from beginner guide" --audio-in input.wav --audio-out stego.wav

Expected output:
Data embedded successfully: stego.wav

Meaning:
- Your text was encrypted.
- Encrypted data was packed with metadata.
- Payload was hidden in audio and saved as stego.wav.

### Step B: Start reliable UDP receiver

Run in Terminal 1:
python udp_file_receiver.py --port 6010 --out received_stego.wav --timeout 25 --nack-interval-ms 100

Expected early output:
Listening on 0.0.0.0:6010 ...

Meaning:
- Receiver is waiting for incoming UDP packets.

### Step C: Send file with deterministic packet loss (for demo)

Open Terminal 2 in same folder and run:
python udp_file_sender.py --host 127.0.0.1 --port 6010 --file stego.wav --drop-indices 3,7,11,19 --control-timeout 8

Expected output shape:
Sent file stego.wav to 127.0.0.1:6010 (message_id=..., chunks=..., bytes=..., simulated_drops=4, resent=4, completion_ack=True, elapsed=...s, throughput=... Mbps)

Meaning of each important value:
- simulated_drops=4: sender intentionally skipped 4 chunks on first pass.
- resent=4: receiver asked for missing chunks and sender resent all 4.
- completion_ack=True: receiver confirmed full valid file reconstruction.

Receiver side expected output shape:
Manifest received: message_id=... chunks=... bytes=...
Received file -> received_stego.wav (... nacks_sent=1)

Meaning:
- nacks_sent=1 means receiver detected missing chunks and requested resend.

### Step D: Recover and decrypt message

Run in Terminal 1 after transfer completes:
python receiver.py --stego-file received_stego.wav

Expected output:
Recovered: b'Hello from beginner guide'

Meaning:
- Hidden encrypted payload was extracted.
- Replay checks passed.
- Decryption succeeded.

### Step E: Build metrics summary and graph

Run in Terminal 1:
python plot_transport_metrics.py --metrics transport_metrics.csv --out transport_metrics_plot.png

Expected output includes:
- summary lines with rows, completion ACK count, simulated drops, resent chunks
- Plot written: transport_metrics_plot.png

Meaning:
- transport_metrics.csv has run logs.
- transport_metrics_plot.png is report-ready chart.

### Step F: Run automated experiment (multi-run report)

Run in Terminal 1:
python run_reliability_experiment.py --runs 3 --drop-indices 3,7,11,19 --results experiment_results.csv

Expected output shape:
- Run 1 ... verified=True
- Run 2 ... verified=True
- Run 3 ... verified=True
- Reliability Experiment Summary ...

Meaning:
- verified=True means output file matched input file for that run.
- completion ACK and resend counters show reliability behavior.
- experiment_results.csv is your per-run results table for report.

## 5) How to explain this in viva (simple script)

Say this:
1. Sender encrypts IoT message using ECC-derived AES key.
2. Encrypted envelope is hidden in WAV using steganography.
3. File is sent over UDP as chunks.
4. Receiver requests only missing chunks using NACK control packets.
5. Sender resends missing chunks, receiver verifies digest, then sends COMPLETE ACK.
6. Receiver extracts payload, checks replay defense, decrypts, and prints original message.

## 6) Common issues and quick fixes

Issue: input.wav missing
Fix: run python create_wav.py to generate a base audio file.

Issue: Timeout on receiver
Fix: increase receiver timeout, for example --timeout 40.

Issue: completion_ack=False on sender
Fix:
- ensure receiver started first
- ensure same port is used in both commands
- increase sender --control-timeout

Issue: Plot not generated
Fix: install matplotlib with python -m pip install matplotlib

## 7) SDN run path (optional)

For Mininet and controller-based run, follow:
- SDN_RUNBOOK.md
- WSL_SDN_CHECKLIST.md
- THREE_TERMINAL_LAUNCH.md

Use those after local demo is confirmed working.
