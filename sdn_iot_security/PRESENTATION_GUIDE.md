Presentation Guide - SDN IoT Security Project

1) One-line project statement
- We built a secure IoT communication pipeline that encrypts sensor data, hides it inside audio, transports it over UDP in an SDN network, and verifies integrity plus replay protection at the receiver.

2) Problem statement
- IoT messages are lightweight but vulnerable to eavesdropping, tampering, and replay attacks.
- Traditional single-layer security can be bypassed if one control fails.
- We designed a defense-in-depth system combining cryptography, steganography, transport integrity, and SDN-aware routing.

3) Objectives
- Confidentiality: prevent plaintext exposure.
- Integrity: detect any packet or payload tampering.
- Anti-replay: reject duplicate or stale packets.
- Covert transport: hide ciphertext in an audio carrier.
- SDN demonstration: show software-controlled forwarding over multiple paths.

4) High-level architecture
- Sender side:
  1. ECC key agreement -> shared secret
  2. HKDF -> 32-byte AES session key
  3. AES-GCM encryption -> nonce + ciphertext + tag
  4. Envelope pack -> version/message_id/timestamp/length fields
  5. Stego embed -> payload bits hidden in WAV LSBs
  6. Optional UDP chunk transport -> manifest + data chunks
- Receiver side:
  1. UDP reassembly + SHA-256 digest verify
  2. Stego extraction from WAV
  3. Envelope unpack
  4. Replay validation
  5. AES-GCM decrypt + verify tag
  6. Recovered plaintext output

5) Module-by-module explanation
- ecc.py
  - Generates EC key pairs using secp256k1.
  - Uses ECDH to derive shared secret.
  - HKDF-SHA256 derives a fixed 32-byte session key.

- aes.py
  - Encrypts with AES-GCM (authenticated encryption).
  - Returns nonce, ciphertext, and auth tag.
  - Decrypt verifies tag before returning plaintext.

- utils.py
  - Defines envelope format and parser.
  - Adds metadata: version, message_id, timestamp, field lengths.
  - Implements replay window with message_id tracking.

- stego.py
  - Embeds encrypted payload in WAV samples.
  - Uses pseudo-random index selection from shared key.
  - Uses LSB matching to reduce obvious sequential patterns.

- udp_transport.py
  - Defines manifest packet and data packet formats.
  - Splits large files into chunks and reassembles at receiver.
  - Uses SHA-256 digest to verify reconstructed file bytes.

- udp_file_sender.py / udp_file_receiver.py
  - Sender transmits manifest and chunk packets.
  - Receiver waits, validates, reassembles, and writes output file.
  - Both log metrics (elapsed time, throughput, packets, chunks).

- ryu_multipath_controller.py
  - OpenFlow 1.3 controller logic for learning switch behavior.
  - Polls port statistics and chooses less-loaded candidate egress.
  - Works with either Ryu imports or OS-Ken imports.

- sdn_topology.py
  - Creates hosts h1 and h2 with switches s1, s2, s3.
  - Provides two possible paths between edge switches.
  - Used with Mininet + remote controller.

6) Security design rationale
- Why ECC + HKDF:
  - ECDH gives shared secret without key transfer.
  - HKDF normalizes key material into cryptographically strong session key.

- Why AES-GCM:
  - Confidentiality and integrity in one primitive.
  - Built-in auth tag detects tampering.

- Why replay defense:
  - Attackers can re-send valid old packets.
  - timestamp + message_id + active time window blocks duplicates/stale payloads.

- Why steganography:
  - Makes encrypted payload less conspicuous than raw encrypted packets.
  - Adds a covert layer beyond classical encryption.

7) What has been completed and validated
- Complete Python pipeline is implemented.
- Full local end-to-end flow passes.
- Replay rejection passes.
- UDP chunk transfer + digest verification passes.
- Metrics CSV generation passes.
- Controller source compatibility updated for Ubuntu (Ryu or OS-Ken).

8) What is pending for final live SDN demonstration
- Run controller in Ubuntu WSL with sudo-installed package.
- Run Mininet topology and execute host-level UDP transfer in CLI.
- Capture final controller logs, pingall output, and receiver plaintext output.

9) Final live demo commands (Ubuntu WSL)
- Terminal 1:
  cd "/mnt/c/Users/user_name/OneDrive/Desktop/CN Project/sdn_iot_security"
  osken-manager ryu_multipath_controller.py

- Terminal 2:
  cd "/mnt/c/Users/user_name/OneDrive/Desktop/CN Project/sdn_iot_security"
  sudo python3 sdn_topology.py
  # in Mininet
  pingall

- Terminal 3:
  cd "/mnt/c/Users/user_name/OneDrive/Desktop/CN Project/sdn_iot_security"
  python3 sender.py --message "WSL SDN test payload" --audio-in input.wav --audio-out stego_sdn.wav

- In Mininet CLI:
  h2 bash -lc 'cd /mnt/c/Users/user_name/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 udp_file_receiver.py --bind-host 0.0.0.0 --port 6000 --out /tmp/received_stego_sdn.wav --timeout 30 --metrics-file /tmp/transport_metrics.csv'
  h1 bash -lc 'cd /mnt/c/Users/user_name/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 udp_file_sender.py --host 10.0.0.2 --port 6000 --file stego_sdn.wav --chunk-size 1024 --metrics-file /tmp/transport_metrics.csv'
  h2 bash -lc 'cd /mnt/c/Users/user_name/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 receiver.py --stego-file /tmp/received_stego_sdn.wav --key-file shared_key.bin --replay-state /tmp/replay_state_sdn.json'

10) Expected outputs to show in presentation
- Recovered: b"WSL SDN test payload"
- UDP receiver summary with packets/chunks/throughput.
- transport_metrics.csv rows for sender and receiver.
- pingall success result.
- Controller terminal logs for packet handling and forwarding behavior.

11) Suggested slide flow (10-12 slides)
1. Title and problem statement
2. Threat model and goals
3. System architecture diagram
4. Crypto pipeline (ECC -> HKDF -> AES-GCM)
5. Stego embedding and extraction logic
6. Replay defense model
7. UDP manifest/chunk transport design
8. SDN topology and controller logic
9. Results and metrics
10. Limitations and future work
11. Conclusion
12. Q&A

12) Limitations and future work
- Add key rotation and session expiration policies.
- Add packet loss recovery (ACK/NACK or FEC) for UDP.
- Add larger topology with dynamic path cost function.
- Add visualization dashboard for controller and transport metrics.
- Add automated test suite for all modules and attack simulations.

13) 2-minute spoken summary
- We secure IoT payloads in multiple layers. First, sender and receiver derive a shared key with ECC and HKDF. Then payload is encrypted using AES-GCM for confidentiality and authenticity. The encrypted envelope is hidden in WAV audio using pseudo-random LSB matching. For network delivery, we split the stego file into UDP chunks and include a manifest with SHA-256 digest for integrity. On the receiver side, chunks are reassembled, digest is verified, stego payload is extracted, replay checks reject stale or duplicate IDs, and AES-GCM decrypt recovers original plaintext. We integrated this with an SDN topology and adaptive controller logic for controlled forwarding. Local validation is complete and the final live WSL SDN run is the last demonstration step.

14) Common viva questions with concise answers
- Why use both encryption and steganography?
  - Encryption secures content; stego hides the existence of sensitive payload. Together they provide layered defense.

- Why AES-GCM instead of CBC?
  - GCM provides authenticated encryption with integrity check via tag, while CBC needs separate MAC.

- How is replay prevented?
  - Receiver stores recent message_id values in a time window and rejects duplicates or stale timestamps.

- Why UDP for transport?
  - Lightweight and suitable for IoT-like constrained networks; custom chunking and digest were added to recover reliability/integrity at application layer.

- What does SDN add here?
  - Programmable forwarding and path selection based on controller logic and observed link/port statistics.
