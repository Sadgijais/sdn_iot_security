WSL SDN Checklist (Only Steps Requiring User Action)

Why your help is needed
- Mininet and Open vSwitch require Linux kernel networking features.
- Ryu + Mininet topology execution must run inside WSL Ubuntu (or native Linux).

A) One-time setup in Ubuntu (WSL)
1. Open Ubuntu terminal.
2. Run:
   sudo apt update
   sudo apt install -y mininet openvswitch-switch python3-pip iperf python3-os-ken

   If you already have a working Ryu installation, that is also supported.

B) Go to project folder in WSL
1. Run:
   cd "/mnt/c/Users/sadgi/OneDrive/Desktop/CN Project/sdn_iot_security"

C) Start controller (Terminal 1)
1. Run:
   osken-manager ryu_multipath_controller.py

   If Ryu is installed instead of OS-Ken, use:
   ryu-manager ryu_multipath_controller.py

D) Start Mininet topology (Terminal 2)
1. Run:
   sudo python3 sdn_topology.py
2. In Mininet CLI run:
   pingall

E) Create secure stego payload (Terminal 3)
1. Run:
   cd "/mnt/c/Users/sadgi/OneDrive/Desktop/CN Project/sdn_iot_security"
   python3 sender.py --message "WSL SDN test payload" --audio-in input.wav --audio-out stego_sdn.wav

F) Transfer file over SDN path
1. In Mininet CLI start receiver on h2:
   h2 bash -lc 'cd /mnt/c/Users/sadgi/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 udp_file_receiver.py --bind-host 0.0.0.0 --port 6000 --out /tmp/received_stego_sdn.wav --timeout 30 --metrics-file /tmp/transport_metrics.csv'
2. In Mininet CLI send from h1:
   h1 bash -lc 'cd /mnt/c/Users/sadgi/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 udp_file_sender.py --host 10.0.0.2 --port 6000 --file stego_sdn.wav --chunk-size 1024 --metrics-file /tmp/transport_metrics.csv'

G) Decrypt on destination host
1. In Mininet CLI run on h2:
   h2 bash -lc 'cd /mnt/c/Users/sadgi/OneDrive/Desktop/CN\ Project/sdn_iot_security; python3 receiver.py --stego-file /tmp/received_stego_sdn.wav --key-file shared_key.bin --replay-state /tmp/replay_state_sdn.json'

H) Collect report artifacts
1. In Mininet CLI on h2:
   h2 cat /tmp/transport_metrics.csv
2. Controller logs in Terminal 1 show packet handling and adaptive path behavior.

Expected success output
- receiver.py prints: Recovered: b"WSL SDN test payload"
- udp_file_receiver.py prints chunks/elapsed/throughput
- transport_metrics.csv has sender and receiver rows
