# Kubernetes Worker Nodes

Kubernetes Worker Nodes are the machines that run application pods in Campus Cloud. The control plane schedules work onto these nodes. If a node is too small or missing a required package, pods stay pending or crash.

This page lists the system requirements for Kubernetes Worker Nodes and the steps to join a node to a cluster.

## System requirements

The system requirements for Kubernetes Worker Nodes in staging and production are:

- CPU: 8 vCPU, x86_64 or arm64. Mixed CPU types in one node pool are not supported.
- Memory: 32 GB RAM available to the kubelet after the system reserved 2 GB.
- Disk: 100 GB SSD for the container filesystem. Keep at least 20 GB free.
- Operating system: Ubuntu 22.04 LTS with current security updates.
- Runtime: containerd 1.7 or newer. Docker Engine is not supported as the kubelet runtime.
- Swap: disabled. The kubelet will refuse to start if swap is on.
- Kernel modules: `br_netfilter` and `overlay` must be loaded.
- Sysctl: `net.ipv4.ip_forward=1` and `net.bridge.bridge-nf-call-iptables=1`.
- Ports: allow 10250 from the control plane, and allow the cluster CNI ports listed in the network policy pack.
- Time: NTP must be enabled. Clock drift above one second causes certificate errors.

These system requirements are the same for Linux nodes in staging and production. Sandbox may use 4 vCPU and 16 GB RAM, but that size is not allowed for graded project work.

## Labels and taints

Each Kubernetes Worker Node must have labels for environment, zone, and node pool. Example:

`env=staging`, `zone=a`, `pool=general`

GPU nodes also get `workload=gpu` and a taint `gpu=true:NoSchedule` so ordinary web apps do not land there.

## Joining a node

1. Confirm the machine meets the system requirements for Kubernetes Worker Nodes.
2. Install the node bootstrap package from the internal mirror.
3. Run the join command copied from the cluster page. The token expires in 24 hours.
4. Wait until the node status is Ready.
5. Drain a canary pod onto the node and confirm it starts.

If the node never becomes Ready, check kubelet logs for swap, disk pressure, or a bad containerd config.

## Capacity planning

A general staging pool should keep one spare Kubernetes Worker Node. If CPU use stays above 70 percent for thirty minutes, add a node rather than raising each pod request by guesswork.

## Why the system requirements matter

If a Kubernetes Worker Node has only 16 GB RAM, a few Java or Python services will consume the node and the kubelet will evict pods. If swap is enabled, those evictions happen later and are harder to debug. If containerd is missing, the kubelet cannot start any pod.

When someone asks "What are its system requirements?" after talking about Kubernetes Worker Nodes, the answer is the list on this page: 8 vCPU, 32 GB RAM, 100 GB SSD, Ubuntu 22.04, containerd, no swap, and the kernel settings above.
