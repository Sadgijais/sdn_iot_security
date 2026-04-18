# Live Demo Script - SDN IoT Security Project
## Exact Commands + Speaker Notes (Follow This Word-For-Word)

---

## PRE-DEMO SETUP (Do this 5 minutes before panel starts)

### On Windows:
1. Open PowerShell as Administrator
2. Navigate to project:
```
cd "c:\Users\user_name\OneDrive\Desktop\CN Project\sdn_iot_security"
```
3. Activate Python venv:
```
& "c:\Users\user_name\OneDrive\Desktop\CN Project\venv\Scripts\Activate.ps1"
```

### On Ubuntu WSL:
1. Open 3 separate Ubuntu terminal windows
2. In each terminal run:
```
cd "/mnt/c/Users/user_name/OneDrive/Desktop/CN Project/sdn_iot_security"
```
3. In one terminal, verify OS-Ken is installed:
```
python3 -c "import os_ken; print('OS-Ken Ready')"
```
If this fails, run (it needs your password):
```
sudo apt update
sudo apt install -y python3-os-ken
```

---

## PART A: LOCAL PROOF (5 minutes) - Run on Windows PowerShell
**Say this to panel:**
"First, let me show you the complete working pipeline locally on this machine. This proves all cryptographic layers, steganography, and replay defense are functioning correctly before we go to the live network demo."

### Step 1: Full End-to-End Demo
**Command:**
```
python main.py
```

**Expected Output:**
```
==================================================
SDN IoT Security Project - Full Demo
==================================================

[1] Generating ECC key pairs...
✓ Keys generated successfully

[2] Generating shared secret key...
✓ Shared key generated: 32 bytes

==================================================
SENDER SIDE - Encrypting & Embedding Data
==================================================

[3] Original data: b'Secret IoT Data'

[4] Encrypting data with AES-GCM...
✓ Encryption successful
  - Nonce: 16 bytes
  - Ciphertext: 15 bytes
  - Auth Tag: 16 bytes
  - Message ID: [SOME_NUMBER]
  - Timestamp: [UNIX_TIME]
  - Total payload: 68 bytes

[5] Embedding encrypted data into audio file...
✓ Data embedded successfully in stego.wav

==================================================
RECEIVER SIDE - Extracting & Decrypting Data
==================================================

[6] Extracting payload from audio...
✓ Data extracted successfully
  - Extracted nonce: 16 bytes
  - Extracted tag: 16 bytes
  - Extracted ciphertext: 15 bytes

[7] Decrypting data with AES-GCM...
✓ Decryption successful!
✓ Recovered data: b'Secret IoT Data'

==================================================
SUCCESS! Data integrity verified ✓
==================================================

[8] Replay defense check (same packet re-processed)...
✓ Replay blocked successfully: Replay detected: duplicate message_id in active window
```

**What to say:**
"Notice the output shows:
1. ECC key generation - this creates the initial key pair.
2. Shared secret key - derived from ECC and HKDF, 32 bytes.
3. Original plaintext - 'Secret IoT Data'.
4. AES-GCM encryption - we get nonce, ciphertext, and auth tag.
5. Stego embedding - payload hidden in WAV file.
6. Extraction - payload recovered from WAV.
7. Decryption - original plaintext recovered.
8. Replay test - duplicate packet rejected successfully.
This proves our multi-layer security works end-to-end."

---

### Step 2: Generate Sender Payload for SDN Test
**Say this:**
"Now let me generate the exact payload we will use in the live SDN network demonstration."

**Command:**
```
python sender.py --message "WSL SDN test payload" --audio-in input.wav --audio-out stego_sdn.wav
```

**Expected Output:**
```
Data embedded successfully: stego_sdn.wav
```

**What to say:**
"The sender has now created a stego_sdn.wav file. This file contains our test message 'WSL SDN test payload' encrypted with AES-GCM and hidden in audio using pseudo-random LSB matching. We will now transfer this over our SDN network."

---

### Step 3: Verify Sender Output Works Locally
**Say this:**
"Let me quickly verify the generated stego file can be decrypted correctly on this machine."

**Command:**
```
python receiver.py --stego-file stego_sdn.wav --key-file shared_key.bin --replay-state replay_state_demo.json
```

**Expected Output:**
```
Recovered: b'WSL SDN test payload'
```

**What to say:**
"Perfect. The receiver extracted and decrypted the payload successfully. Now we move to the SDN network layer."

---

## PART B: LIVE SDN DEMO (8 minutes) - Ubuntu WSL
**Say this to panel:**
"Now we run the exact same payload through a live Software-Defined Network topology using Mininet and an OpenFlow controller. This demonstrates how the secure payload traverses a programmable network with adaptive path selection based on link utilization."

---

### Terminal 1: Start SDN Controller
**Say this before running:**
"First, I'll start the OpenFlow controller. This software-defined networking controller will monitor port statistics and choose the least-loaded path for our data transfer."

**Window: Ubuntu Terminal 1**
**Command:**
```
cd "/mnt/c/Users/user_name/OneDrive/Desktop/CN Project/sdn_iot_security"
osken-manager ryu_multipath_controller.py
```

**Expected Output:**
```
loading app ryu_multipath_controller
loading app ryu.controller.ofp_event
creating context ryu.controllers.ofp_event
instantiating app ryu_multipath_controller of MultipathController
```

**What to say:**
"The controller is now running. It's listening for OpenFlow messages from the network switches and will handle all packet-forwarding decisions."

---

### Terminal 2: Start Mininet Topology
**Say this before running:**
"In a second terminal, I'll start the Mininet topology. This creates a virtual network with two hosts (h1 as sender, h2 as receiver) connected through three switches with two possible paths between them."

**Window: Ubuntu Terminal 2**
**Command:**
```
cd "/mnt/c/Users/user_name/OneDrive/Desktop/CN Project/sdn_iot_security"
sudo python3 sdn_topology.py
```

**Expected Output:**
```
Topology started. Hosts: h1(10.0.0.1), h2(10.0.0.2)
mininet>
```

**What to say:**
"The Mininet topology is now live. We have hosts h1 and h2 connected through a network with two possible paths. Let me run a connectivity test."

---

### Terminal 2: Connectivity Test
**Say this:**
"I'll run 'pingall' to verify all hosts can reach each other through the SDN switches and controller."

**Command in Mininet prompt:**
```
pingall
```

**Expected Output:**
```
h1 -> h2
h2 -> h1
Results: 0% dropped (2/2 received)
```

**What to say:**
"Excellent. All connectivity tests pass. The SDN network is operational with controller managing all path decisions."

---

### Terminal 3: Start UDP Receiver on h2
**Say this before running:**
"Now I'll start the receiver process on host h2. It will listen on port 6000 and wait to receive the chunked stego audio file."

**Window: Ubuntu Terminal 3 (or type in Mininet)**
**Command in Mininet prompt:**
```
h2 bash -lc 'cd /mnt/c/Users/user_name/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 udp_file_receiver.py --bind-host 0.0.0.0 --port 6000 --out /tmp/received_stego_sdn.wav --timeout 30 --metrics-file /tmp/transport_metrics.csv'
```

**Expected Output:**
```
Listening on 0.0.0.0:6000 ...
```

**What to say:**
"The receiver is now listening. It's ready to accept UDP packets containing our stego audio file."

---

### Terminal 2: Send File from h1 to h2
**Say this before running:**
"Now I'll send the stego audio file from host h1 to host h2. The file will be split into 1024-byte chunks, sent via UDP, and the receiver will verify integrity using SHA-256."

**Command in Mininet prompt (same terminal, new line):**
```
h1 bash -lc 'cd /mnt/c/Users/user_name/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 udp_file_sender.py --host 10.0.0.2 --port 6000 --file stego_sdn.wav --chunk-size 1024 --metrics-file /tmp/transport_metrics.csv'
```

**Expected Output (appears in seconds):**
```
Sent file stego_sdn.wav to 10.0.0.2:6000 (message_id=XXXXXXXXX, chunks=173, bytes=176444, elapsed=X.XXs, throughput=X.XX Mbps)
```

**What to say:**
"The file has been transmitted successfully. It took approximately X seconds to send, at roughly X Mbps throughput. The receiver has now reassembled all 173 chunks and verified the SHA-256 digest."

---

### Check Receiver Output
**Say this:**
"Let me check the output from the receiver to confirm it received and verified the file successfully."

**Look at Terminal 3 output (should now show):**
```
Manifest received: message_id=XXXXXXXXX chunks=173 bytes=176444
Received file -> /tmp/received_stego_sdn.wav (packets=175, chunks=173, elapsed=X.XXs, throughput=X.XX Mbps)
```

**What to say:**
"Perfect! The receiver successfully reassembled all 173 chunks from 175 packets. Digest verification passed, which means no data corruption occurred during transport."

---

### Terminal 2: Decrypt on h2
**Say this before running:**
"Now for the final critical step: the receiver will extract the encrypted payload from the received stego audio file, validate the replay window, and decrypt it using AES-GCM."

**Command in Mininet prompt:**
```
h2 bash -lc 'cd /mnt/c/Users/user_name/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 receiver.py --stego-file /tmp/received_stego_sdn.wav --key-file shared_key.bin --replay-state /tmp/replay_state_sdn.json'
```

**MOST IMPORTANT - Expected Output:**
```
Recovered: b'WSL SDN test payload'
```

**What to say (point to output):**
"There it is! The original plaintext message has been successfully recovered after traveling through the entire pipeline:
1. Encrypted with AES-GCM ✓
2. Hidden in audio steganography ✓
3. Fragmented into UDP chunks ✓
4. Routed through the SDN network ✓
5. Reassembled with integrity verification ✓
6. Decrypted and replay-validated ✓

The exact message 'WSL SDN test payload' is now visible."

---

### Show Transport Metrics
**Say this:**
"Let me show you the performance metrics captured during the transfer."

**Command in Mininet prompt:**
```
h2 cat /tmp/transport_metrics.csv
```

**Expected Output:**
```
timestamp,role,status,message_id,file_path,bytes,chunks,packets,elapsed_s,throughput_mbps,note
1776499457,receiver,ok,2981378644,/tmp/received_stego_sdn.wav,176444,173,175,12.084305,0.116809,
1776499457,sender,ok,2981378644,stego_sdn.wav,176444,173,176,1.664180,0.848197,
```

**What to say:**
"The CSV shows:
- Sender sent 176,444 bytes in 173 chunks across 176 packets in 1.66 seconds (0.85 Mbps)
- Receiver received all data in 12.08 seconds at 0.12 Mbps (includes wait time)
- Both operations completed successfully with matching message IDs
These metrics demonstrate reliable transport over the SDN network."

---

## CLOSING STATEMENT (1 minute)

**What to say:**
"In summary, we demonstrated:

1. **Cryptography layer**: ECC key agreement generating a shared 32-byte session key via HKDF-SHA256.

2. **Encryption layer**: AES-GCM providing confidentiality (encryption) and authenticity (auth tag).

3. **Steganography layer**: Encrypted payload hiding in WAV audio using pseudo-random LSB matching.

4. **Replay protection**: Message ID and timestamp validation blocking duplicate or stale packets.

5. **Reliable transport**: UDP chunking with manifest and SHA-256 digest verification.

6. **SDN control**: OpenFlow controller managing multi-path forwarding based on port statistics.

All layers worked correctly, and the original plaintext message was successfully recovered after traversing the complete secure pipeline end-to-end through a live software-defined network. Thank you."

---

## TROUBLESHOOTING (If Something Goes Wrong)

### Problem: osken-manager command not found
**Solution:**
Use Ryu instead:
```
ryu-manager ryu_multipath_controller.py
```

### Problem: UDP receiver times out (no packets received)
**Cause:** Sender and receiver may be out of sync
**Solution:**
1. Stop receiver (Ctrl+C in Mininet)
2. Increase timeout and restart: `--timeout 60`
3. Restart sender immediately after

### Problem: Replay rejected unexpectedly
**Cause:** Using same replay_state file twice
**Solution:**
Use a new replay state filename:
```
python3 receiver.py --stego-file /tmp/received_stego_sdn.wav --key-file shared_key.bin --replay-state /tmp/replay_state_fresh.json
```

### Problem: SDN network connectivity fails (pingall shows drops)
**Cause:** Controller not connected to switches
**Solution:**
1. Verify controller is running in Terminal 1
2. Check Terminal 1 shows "EventOFPSwitchFeatures" messages
3. Restart Mininet topology: exit Mininet, rerun sudo python3 sdn_topology.py

### Problem: Received file doesn't match original
**Solution (Unlikely - SHA-256 verification prevents this):**
1. Delete received file and retry
2. Increase chunk size: `--chunk-size 2048`

### FALLBACK: If SDN demo fails, show local proof
If the live Mininet demo fails unexpectedly, immediately say:
"Let me show you the locally validated run that we recorded earlier:"
```
cat transport_metrics_sdn_local.csv
```
This proves the concept works; the failure is environmental only.

---

## Key Files To Reference During Q&A

If panel asks about:
- **Key exchange**: Point to `ecc.py`
- **Encryption**: Point to `aes.py`
- **Steganography**: Point to `stego.py`
- **Replay defense**: Point to `utils.py` (validate_and_update_replay function)
- **UDP transport**: Point to `udp_transport.py` and `udp_file_sender.py` / `udp_file_receiver.py`
- **Metrics**: Point to `net_metrics.py`
- **SDN controller logic**: Point to `ryu_multipath_controller.py` (choose_best_egress function)
- **Full architecture**: Point to `PRESENTATION_GUIDE.md`
