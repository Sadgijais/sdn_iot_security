SDN Integration Runbook

Prerequisites
- Linux environment (native Linux or WSL2) with Mininet and Open vSwitch installed.
- Python environment containing Ryu or OS-Ken.

1) Start Ryu controller
- Command:
  osken-manager ryu_multipath_controller.py

- If Ryu is installed instead, use:
  ryu-manager ryu_multipath_controller.py

2) Start Mininet topology in another terminal
- Command:
  sudo python3 sdn_topology.py

3) Validate connectivity from Mininet CLI
- Commands:
  pingall
  h1 iperf -s -u -p 5001 &
  h2 iperf -c 10.0.0.1 -u -b 2M -t 10

4) Generate secure stego payload in project
- Command from project directory:
  python3 sender.py --audio-in input.wav --audio-out stego.wav

5) Start UDP file receiver on destination host
- From Mininet CLI:
  h2 python3 udp_file_receiver.py --bind-host 0.0.0.0 --port 6000 --out /tmp/received_stego.wav --timeout 30 --metrics-file /tmp/transport_metrics.csv

6) Send stego.wav from source host
- From Mininet CLI in another command window:
  h1 python3 udp_file_sender.py --host 10.0.0.2 --port 6000 --file stego.wav --chunk-size 1024 --metrics-file /tmp/transport_metrics.csv

7) Recover plaintext at receiver side
- On destination host:
  h2 python3 receiver.py --stego-file /tmp/received_stego.wav --key-file shared_key.bin --replay-state /tmp/replay_state.json

Notes
- Controller app uses adaptive least-loaded path selection on switch s1 (ports 2/3) based on OpenFlow port tx_bytes.
- UDP transport uses manifest + chunk packets with SHA-256 integrity verification before file write.
- Transport scripts append per-run metrics (elapsed time and throughput) to CSV for report generation.
