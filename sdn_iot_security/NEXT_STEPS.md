Next Steps To Finish The Project

Current status
- The Python implementation is complete and verified.
- The missing piece is the live SDN experiment in Ubuntu WSL with Mininet and controller runtime.

Step 1: Open Ubuntu WSL
- Launch Ubuntu from Start menu.
- Make sure the distro is running.

Step 2: Install controller runtime (one-time)
- Run:
  sudo apt update
  sudo apt install -y python3-os-ken

Step 3: Start the SDN controller
- Run:
  cd "/mnt/c/Users/sadgi/OneDrive/Desktop/CN Project/sdn_iot_security"
  osken-manager ryu_multipath_controller.py

- If Ryu is already installed instead:
  ryu-manager ryu_multipath_controller.py

Step 4: Start the Mininet topology
- In a second Ubuntu terminal, run:
  cd "/mnt/c/Users/sadgi/OneDrive/Desktop/CN Project/sdn_iot_security"
  sudo python3 sdn_topology.py

Step 5: Verify network connectivity
- In the Mininet prompt, run:
  pingall

Step 6: Generate the stego payload
- In a third Ubuntu terminal, run:
  cd "/mnt/c/Users/sadgi/OneDrive/Desktop/CN Project/sdn_iot_security"
  python3 sender.py --message "WSL SDN test payload" --audio-in input.wav --audio-out stego_sdn.wav

Step 7: Receive the file on h2
- In the Mininet prompt, run:
  h2 bash -lc 'cd /mnt/c/Users/sadgi/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 udp_file_receiver.py --bind-host 0.0.0.0 --port 6000 --out /tmp/received_stego_sdn.wav --timeout 30 --metrics-file /tmp/transport_metrics.csv'

Step 8: Send the file from h1
- In the Mininet prompt, run:
  h1 bash -lc 'cd /mnt/c/Users/sadgi/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 udp_file_sender.py --host 10.0.0.2 --port 6000 --file stego_sdn.wav --chunk-size 1024 --metrics-file /tmp/transport_metrics.csv'

Step 9: Decrypt on h2
- In the Mininet prompt, run:
  h2 bash -lc 'cd /mnt/c/Users/sadgi/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 receiver.py --stego-file /tmp/received_stego_sdn.wav --key-file shared_key.bin --replay-state /tmp/replay_state_sdn.json'

Expected output
- pingall succeeds.
- UDP receiver prints manifest received and file received.
- receiver.py prints:
  Recovered: b"WSL SDN test payload"

What to save for your report
- Controller output from Ryu terminal.
- pingall result.
- UDP sender and receiver metrics output.
- receiver.py recovered plaintext output.
- transport_metrics.csv contents.

If something fails
- If pingall fails, the Mininet topology or controller is not connected correctly.
- If UDP receive times out, increase --timeout to 45 or 60 seconds.
- If receiver.py rejects replay, delete the replay_state file and run once more.
