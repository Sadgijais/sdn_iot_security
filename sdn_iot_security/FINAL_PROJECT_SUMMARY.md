Final Project Summary

Project goal
- Secure IoT data using ECC, AES-256 GCM, audio steganography, UDP file transport, replay protection, and SDN routing.

What was implemented
1. ECC key exchange
- ECDH creates a shared secret.
- HKDF-SHA256 derives a 32-byte session key.

2. AES security
- AES-GCM encrypts the IoT message.
- Authentication tag ensures tamper detection.

3. Audio steganography
- The encrypted payload is hidden inside a WAV file.
- Pseudo-random LSB matching is used instead of sequential LSB embedding.

4. Replay protection
- Each payload contains message_id and timestamp.
- Receiver rejects stale or duplicate packets using replay_state.json.

5. UDP transport
- Stego WAV files are split into UDP chunks.
- A manifest packet describes file size, chunk count, and SHA-256 digest.
- Receiver reassembles chunks and verifies integrity before saving.

6. Metrics and evaluation
- Sender and receiver write timing and throughput to CSV.
- This can be used for report graphs and comparison tables.

7. SDN setup
- Mininet topology file is ready.
- Controller file is ready and supports both Ryu and OS-Ken module namespaces.
- Controller chooses a less-loaded path using port statistics.

What was verified
- main.py runs end to end successfully.
- sender.py works.
- receiver.py works.
- UDP file sender and receiver work.
- Replay rejection works.
- Metrics CSV is produced.
- Python syntax checks passed.
- WSL Ubuntu + Mininet availability was validated.
- A full local transport round trip recovered: Recovered: b"WSL SDN test payload".

What is still required for a full live SDN demo
- Install controller runtime in Ubuntu WSL (recommended: python3-os-ken).
- Start the topology and controller.
- Run the UDP sender and receiver inside Mininet hosts.
- Capture the console outputs for your report.

Exact final status
- Code prototype: complete and working.
- Full SDN lab deployment: still needs Linux/WSL execution.

Recommended command flow
1. Start controller (osken-manager or ryu-manager)
2. Start Mininet topology
3. Run pingall
4. Generate stego payload with sender.py
5. Run udp_file_receiver.py on h2
6. Run udp_file_sender.py on h1
7. Run receiver.py on h2

Expected final plaintext
- Recovered: b"WSL SDN test payload"
