3-Terminal Launch Plan

Run everything below in Ubuntu WSL, not PowerShell.

1) Terminal 1: Controller
cd "/mnt/c/Users/user_name/OneDrive/Desktop/CN Project/sdn_iot_security"
ryu-manager ryu_multipath_controller.py

2) Terminal 2: Mininet topology
cd "/mnt/c/Users/user_name/OneDrive/Desktop/CN Project/sdn_iot_security"
sudo python3 sdn_topology.py

Inside the Mininet prompt, run:
pingall

3) Terminal 3: Payload creation and transfer
cd "/mnt/c/Users/user_name/OneDrive/Desktop/CN Project/sdn_iot_security"
python3 sender.py --message "WSL SDN test payload" --audio-in input.wav --audio-out stego_sdn.wav

Then inside the Mininet prompt use these two commands in order:
h2 bash -lc 'cd /mnt/c/Users/user_name/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 udp_file_receiver.py --bind-host 0.0.0.0 --port 6000 --out /tmp/received_stego_sdn.wav --timeout 30 --metrics-file /tmp/transport_metrics.csv'
h1 bash -lc 'cd /mnt/c/Users/user_name/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 udp_file_sender.py --host 10.0.0.2 --port 6000 --file stego_sdn.wav --chunk-size 1024 --metrics-file /tmp/transport_metrics.csv'

4) Final recovery command
h2 bash -lc 'cd /mnt/c/Users/user_name/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 receiver.py --stego-file /tmp/received_stego_sdn.wav --key-file shared_key.bin --replay-state /tmp/replay_state_sdn.json'

Expected result
Recovered: b"WSL SDN test payload"
