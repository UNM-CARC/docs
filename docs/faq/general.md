---
title: "General FAQ"
description: "Quick answers about accounts, projects, cost, storage, software, and GPUs at CARC."
type: Reference
tags:
  - FAQ
  - New users
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: carc-web
    resource: "https://carc.unm.edu/index.html"
    title: "CARC website (carc.unm.edu)"
    author: "team:unm-carc"
---

# General FAQ

## Accounts and projects

??? question "Who can use CARC?"

    CARC resources are free of charge for UNM faculty, staff, and student
    researchers, supported by the Office of the Vice President for Research.
    External collaborators can get accounts through a UNM project PI — see
    [Getting started](../getting-started/overview.md).

??? question "How do I get an account?"

    UNM affiliates use the self-service portal at
    [mokey.alliance.unm.edu](https://mokey.alliance.unm.edu){ target=_blank };
    collaborators without a UNM email are requested by their PI. Details in
    [Getting started](../getting-started/overview.md).

??? question "I have an account — why can't I run jobs?"

    Your account must belong to a **CARC project** that holds compute
    resources. Ask your PI to add you to their project in
    [ColdFront](https://coldfront.alliance.unm.edu){ target=_blank }. Note
    that your Slurm account is not the same as your login account — see
    [Slurm accounting and fairshare](../running-jobs/slurm-accounting.md).

??? question "How do I become a project PI?"

    PI eligibility follows the
    [UNM criteria for Principal Investigator status](https://osp.unm.edu/pi-resources/pi-eligibility.html){ target=_blank }.
    Eligible PIs create projects and request resources in ColdFront.

## Cost and allocations

??? question "Does CARC cost anything?"

    The core service is free for UNM researchers. Additional dedicated
    storage and premium services are available for purchase — see
    [premium research computing services](https://carc.unm.edu/research/premium-research-computing-services.html){ target=_blank }.

??? question "How is fair access enforced?"

    Through Slurm's fairshare system: heavy recent usage lowers your
    scheduling priority relative to lighter users, so everyone gets a fair
    opportunity. See [resource limits](../systems/resource-limits.md) and
    [Slurm accounting](../running-jobs/slurm-accounting.md).

??? question "Do allocations expire? How do I renew?"

    Yes — ColdFront allocations have end dates, and ColdFront emails
    automated `[coldfront]` notices as they approach: renewal reminders and
    expiration warnings need action from the PI (or a project manager),
    while request confirmations ("allocation request submitted", "quota
    increase request submitted") are informational. Renewals, like new
    requests, are handled in
    [ColdFront](https://coldfront.alliance.unm.edu){ target=_blank } —
    renew before the end date so the resources an allocation grants don't
    lapse. The
    [Annual Project Review walkthrough](https://www.youtube.com/watch?v=MGxMfmShVWk){ target=_blank }
    video covers the yearly review; unsure what a notice means?
    [Open a ticket](../support/help.md).

??? question "What if I need more than CARC can provide?"

    National platforms are the next step — ACCESS-CI allocations, the
    Jetstream2 cloud, and CyVerse data services. See
    [partner cyberinfrastructure](../about/partners.md); CARC staff can help
    you apply.

## Storage and data

??? question "Where should I put my data?"

    Home for small, important files; project space for shared work; scratch
    for active job I/O. Quotas and the `quotas` command are covered in
    [resource limits](../systems/resource-limits.md), and the layout in
    [storage and backups](../systems/storage.md).

??? question "Where is my project's scratch space?"

    Easley-local project scratch follows
    `/easley/scratch/projects/<pi-username>/<pi-username><project-id>`.
    Center-wide project scratch usually follows
    `/carc/scratch/projects/<pi-username>/<pi-username><project-id>`, but
    is **not consistently nested** — some allocations sit directly under
    `projects/`. If a newly approved allocation's path doesn't exist yet,
    check its status in
    [ColdFront](https://coldfront.alliance.unm.edu){ target=_blank } (it may
    still be provisioning), and [open a ticket](../support/help.md) to get
    the exact path. See [storage and backups](../systems/storage.md).

??? question "How do I keep data longer than scratch allows?"

    Scratch is sized for active job I/O, not retention — files on
    Easley-local scratch are auto-deleted after 180 days without access.
    For data that must persist, ask your PI (or a project **manager** the
    PI has designated) to request **project storage** in
    [ColdFront](https://coldfront.alliance.unm.edu){ target=_blank },
    choosing between the backed-up flavor (protected against loss) and
    non-backed-up project scratch (larger, unprotected). Estimate your
    current and projected size first — it's the first thing support will
    ask. Urgent need that can't wait for approval?
    [Open a ticket](../support/help.md).

??? question "Is my data backed up?"

    Enterprise (NetApp) storage has automated snapshots (hourly to monthly,
    retained up to four months). **Scratch is not backed up.** See
    [storage and backups](../systems/storage.md).

??? question "Can I store HIPAA / regulated data on CARC?"

    No. HIPAA, PHI, PCI, FERPA, and CUI data may not be stored on or
    transferred via CARC systems — see the
    [Good Neighbor Use Policy](../getting-started/good-neighbor-policy.md).

## Software and hardware

??? question "How do I get software installed?"

    First check `module avail` ([environment modules](../running-jobs/modules.md)).
    You can install your own stacks with [conda](../software/conda-intro.md)
    or run [containers](../software/singularity.md). For system-wide
    installs, [open a ticket](../support/help.md). Export-controlled software
    requires prior written approval from UNM Export Control.

??? question "What GPUs are available?"

    Easley has NVIDIA L40S and H100 GPUs, and Hopper has A100s (and some
    V100s) — see the [systems overview](../systems/overview.md). Request GPU
    partitions in your job script; examples are in
    [example Slurm scripts](../running-jobs/example-slurm-scripts.md).

    Note that Easley's `h100` and `l40s` partitions are **group-gated**:
    access comes from an approved ColdFront allocation for the specific
    partition, requested by your PI. If a submission is rejected with
    `uid not in group permitted to use this partition`, see
    [troubleshooting](troubleshooting.md#my-job-wont-start).

??? question "Can I use CARC from my browser?"

    Yes — [Open OnDemand](../interactive/open-ondemand.md) for files, shells,
    and jobs, or [JupyterHub](../interactive/jupyterhub.md) for notebooks.

## Publishing

??? question "How do I acknowledge CARC in a paper?"

    Use the statement on [acknowledging CARC](../support/acknowledging-carc.md)
    and add the publication to your project's list in ColdFront.
