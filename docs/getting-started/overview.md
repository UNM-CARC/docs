---
title: "Getting started at CARC"
description: "Create a CARC account, join a project in ColdFront, and find support."
type: Guide
tags:
  - Accounts
  - New users
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: carc-web
    resource: "https://carc.unm.edu/new-users/getting-started-at-carc1.html"
    title: "Getting started at CARC (carc.unm.edu)"
    author: "team:unm-carc"
  - id: quickbytes-pr-318
    resource: "https://github.com/UNM-CARC/QuickBytes/pull/318"
    title: "UNM-CARC QuickBytes PR #318: new-user onboarding (Welcome to CARC; Getting access)"
    author: "human:hfricke"
  - id: quickbytes-pr-295
    resource: "https://github.com/UNM-CARC/QuickBytes/pull/295"
    title: "UNM-CARC QuickBytes PR #295: ColdFront and Mokey account services"
    author: "human:hfricke"
---

# Getting started at CARC

The UNM Center for Advanced Research Computing provides high-performance
computing resources to facilitate UNM research — free of charge to faculty,
staff, and student researchers, with support from the UNM Office of the Vice
President for Research.

## New to research computing?

You don't need a coding background to get started, and asking questions is
exactly what CARC is for.

CARC runs **clusters**: large groups of computers, called *nodes*, that many
researchers share. Instead of running a program the moment you press Enter, as
on a laptop, you ask for a share of the cluster's time and resources. Your work
waits briefly until that share is free, then runs. A scheduler called
[Slurm](../running-jobs/slurm-intro.md) handles the waiting and placement for
you. CARC's current clusters are **Easley**, the general-purpose cluster most
people use, and **Hopper** (see the [systems overview](../systems/overview.md)).

Besides the clusters and storage, CARC offers one-on-one help running your
research code, [workshops](../training/workshops.md) and
[videos](../training/videos.md), these guides, and troubleshooting when
something isn't working. See [Getting help](../support/help.md).

## Accounts and projects

Access is organized around **CARC accounts** (people) and **CARC projects**
(resources). Every user needs an active account, and that account must belong
to a project that holds the compute and storage resources you want to use.
Each lives on its own website:

| Website | What it's for |
|---|---|
| **Mokey** ([mokey.alliance.unm.edu](https://mokey.alliance.unm.edu){ target=_blank }) | Your personal account: username, password, two-factor authentication, and SSH keys. |
| **ColdFront** ([coldfront.alliance.unm.edu](https://coldfront.alliance.unm.edu/){ target=_blank }) | Projects: a research group's space on CARC, led by a PI. Compute and storage allocations are requested and assigned here. |

A Mokey account on its own doesn't give you access to anything: you also need
to be added to a project in ColdFront.

| You are... | What you need |
|---|---|
| A student or collaborator whose PI already has a project | A Mokey account, then ask your PI to add you in ColdFront |
| A collaborator without a UNM email address | Your UNM PI requests an account for you |
| A PI starting a new project | Confirm eligibility, create the project, and request resources in ColdFront |

!!! note "Good Neighbor Use Policy"

    By creating a CARC account you agree to abide by the
    [Good Neighbor Use Policy](good-neighbor-policy.md). Please read it first.

## 1. Create your account

=== "UNM affiliates"

    If you have a UNM email address, use the self-service account portal:

    [:material-account-plus: Request an account](https://mokey.alliance.unm.edu){ .md-button .md-button--primary target=_blank }

=== "External collaborators"

    If you do not have a UNM email address, ask your UNM project PI to request
    an account for you:

    [:material-account-arrow-right: Collaborator account request form](https://forms.office.com/r/FJ46nKbPvV){ .md-button target=_blank }

## 2. Join a CARC project

Resources (compute time, storage) are attached to projects, managed through
**ColdFront** at [coldfront.alliance.unm.edu](https://coldfront.alliance.unm.edu/){ target=_blank }.

Ask the project's Principal Investigator — typically your research advisor or
UNM collaborator — to add your account to their project. Adding people to a
project is the PI's job (or the lab's designated project manager's); you can't
add yourself. Once you are on a project, you can use every resource allocated
to it.

## Managing your account

Use [Mokey](https://mokey.alliance.unm.edu){ target=_blank } to look after your
own account at any time:

* [Reset or change your password](password-reset.md), including after it
  expires.
* Turn on two-factor authentication and add or remove one-time-password
  (TOTP) tokens.
* [Add or remove SSH public keys](ssh-keys.md) for password-free logins.
* See which projects and groups your account belongs to.

## For Principal Investigators

1. **Create a project** in [ColdFront](https://coldfront.alliance.unm.edu){ target=_blank }.
   PI eligibility follows the
   [UNM criteria for Principal Investigator status](https://osp.unm.edu/pi-resources/pi-eligibility.html){ target=_blank }.
2. **Request resources** (compute and storage allocations) for the project
   through ColdFront.
3. **Add accounts** — the PI is responsible for adding collaborators' and
   students' accounts to the project.
4. **Keep allocations current** — allocations have end dates, and ColdFront
   emails automated renewal reminders and expiration warnings as they
   approach. Renew in ColdFront (the PI or a designated project manager)
   before the end date so the resources an allocation grants don't lapse —
   see the [allocation FAQ](../faq/general.md#cost-and-allocations).

For walkthroughs of project management and the annual review process, see the
[video tutorials](../training/videos.md).

## Data access and stewardship

CARC follows the data stewardship policies defined by the University for data
ownership and succession for all data stored on CARC systems. Review the
restrictions on regulated data (HIPAA, PHI, PCI, FERPA, CUI) in the
[Good Neighbor Use Policy](good-neighbor-policy.md).

## Next steps

* [Log in to a cluster](logging-in.md) with SSH.
* [Transfer your data](transferring-data.md) onto CARC storage.
* [Run your first Slurm job](../running-jobs/slurm-intro.md).
* New to the command line? Start with the [introduction to Linux](../tutorials/linux-intro.md).

## Video walkthroughs

**Creating an Account** — from the [CARC video tutorials](../training/videos.md):

<iframe class="carc-video" src="https://www.youtube-nocookie.com/embed/ewyqLP-Eo_4" title="Creating an Account" loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

**CARC Project Management with ColdFront** — for PIs and project managers:

<iframe class="carc-video" src="https://www.youtube-nocookie.com/embed/HJcjOSNWp1U" title="CARC Project Management with ColdFront" loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

More episodes — including the [Annual Project Review](https://www.youtube.com/watch?v=MGxMfmShVWk){target=_blank}
walkthrough — are on the [video tutorials page](../training/videos.md).

## Questions?

Submit a help request to <help@carc.unm.edu>, open a ticket at
[support.alliance.unm.edu](https://support.alliance.unm.edu/){ target=_blank },
or visit [office and consultation hours](../support/help.md).
