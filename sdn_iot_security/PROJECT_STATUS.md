Project Status

What is already done
- ECC key exchange uses HKDF-derived 32-byte session keys.
- AES-GCM encrypts and authenticates the IoT payload.
- Audio steganography hides the encrypted envelope in a WAV file.
- Pseudo-random LSB matching is used instead of sequential embedding.
- Replay protection blocks duplicate message_id values inside the active window.
- UDP transport scripts chunk and reassemble stego files with SHA-256 verification.
- Transport metrics are written to CSV for sender and receiver runs.
- SDN starter files exist for Mininet topology and a Ryu controller.
- Runbooks exist for both full WSL execution and a 3-terminal quick launch.
- Controller source now supports both Ryu and OS-Ken imports for Ubuntu compatibility.

What was verified
- main.py runs end to end successfully.
- sender.py and receiver.py run successfully.
- UDP file sender and receiver transfer a stego WAV successfully.
- Reassembled file decrypts back to the original plaintext.
- Replay check correctly rejects a repeated packet.
- Transport metrics CSV is produced and populated.
- Python syntax checks passed on the updated modules.
- WSL environment check confirms Ubuntu and Mininet are available.
- Local end-to-end transport test with payload "WSL SDN test payload" succeeds.

What still needs your help
- Install and run controller runtime inside WSL using sudo privileges.
- Start Mininet topology and run final live SDN transfer inside hosts.
- Capture output logs and CSV for final presentation evidence.

Exact next step for you
1. Open Ubuntu WSL.
2. Run: sudo apt install -y python3-os-ken
3. Start controller with: osken-manager ryu_multipath_controller.py
4. Start topology with: sudo python3 sdn_topology.py
5. Run transfer commands in Mininet and share terminal output.

Expected final result
- The receiver prints: Recovered: b"WSL SDN test payload"
