---
title: "Facilities description"
description: "Boilerplate facilities description for grant proposals: clusters, storage, networking, and the data center."
type: Reference
tags:
  - About
  - Grants
stale_after: "2027-08-31T00:00:00Z"
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: carc-facilities
    resource: "https://carc.unm.edu/about-carc/facilities-description.html"
    title: "Facilities description (carc.unm.edu)"
    author: "team:unm-carc"
---

# Facilities description

!!! tip "For grant proposals"

    This page is written to be copied into the *Facilities, Equipment, and
    Other Resources* section of proposals. See also
    [acknowledging CARC](../support/acknowledging-carc.md) for the
    publication acknowledgement statement.

The UNM Center for Advanced Research Computing (CARC) supports
high-performance and data-intensive research across the UNM community. Our
systems are designed to serve a wide range of disciplines, from traditional
scientific computing to advanced data analytics, artificial intelligence, and
machine learning.

## Compute

CARC currently operates several high-performance computing clusters:

**Easley Cluster** — 65 compute nodes with 4,160 total CPU cores and 23.3 TB
of RAM. Easley includes 36 NVIDIA L40S GPUs for AI and machine learning
workloads, along with 8 NVIDIA H100 GPUs for double-precision computing. The
system is connected through an NVIDIA NDR 800 Gbps InfiniBand core network
for high-speed communication between nodes.

**Hopper Cluster** — 61 compute nodes with 2,176 CPU cores and 37 NVIDIA A100
GPUs. Hopper is connected through an NVIDIA HDR 400 Gbps InfiniBand network
and supports both general and GPU-accelerated workloads.

Together, these systems support a broad ecosystem of research software,
including scientific computing tools, machine learning frameworks such as
TensorFlow and PyTorch, data analytics platforms, and interactive
environments like Jupyter, R, and Parallel MATLAB.

## Data storage and virtual infrastructure

CARC provides multiple tiers of high-performance storage to support both
active research workflows and long-term data management:

* 720 TB of all-flash IBM Storage Scale (GPFS) scratch storage
* 2 PB of BeeGFS working scratch storage
* 2.4 PB of NetApp enterprise storage

Enterprise storage includes automated snapshots taken hourly, daily, weekly,
and monthly, with retention for up to four months to support user-directed
data recovery.

In partnership with UNM Libraries, CARC also supports a virtual machine
infrastructure that enables custom research applications, secure data
hosting, and flexible computing environments.

## Physical infrastructure

All CARC systems are housed in a dedicated 1,200 square-foot research data
center built to support high-performance and data-intensive computing.

The facility includes 270 kVA of UPS capacity and 990 tons of dedicated
cooling across three Liebert AC systems, providing resilience during
transient power events and allowing for controlled shutdown during extended
outages.

Systems are connected to campus through multiple 10 Gbps links, including a
dedicated 10 Gbps connection to UNM's Science DMZ research network. External
connectivity includes 100 Gbps connections to ESnet and the Western Regional
Network through the Albuquerque Gigapop.

Physical access to the machine room is restricted and managed through UNM's
Electronic Network Access Control system.
