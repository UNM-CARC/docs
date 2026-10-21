---
title: "Transferring data with Globus"
description: "Move large datasets to and from CARC home, project, and scratch storage with Globus, using your UNM login and your CARC account."
type: Guide
tags:
  - Data
  - Storage
  - Globus
generated:
  by: "claude/opus-5-5"
  at: "2026-10-21T00:00:00Z"
sources:
  - id: globus-docs
    resource: "https://docs.globus.org/guides/tutorials/manage-files/transfer-files/"
    title: "Globus documentation: transfer files"
    author: "team:globus"
status: draft
---

# Transferring data with Globus

[Globus](https://www.globus.org){ target=_blank } moves files between CARC and
your laptop, a lab server, or another institution. Transfers run in the
background, restart on their own after network interruptions, and verify every
file, so Globus is the best choice for large datasets or many files.

[:material-swap-horizontal: Open the Globus File Manager](https://app.globus.org/file-manager){ .md-button .md-button--primary target=_blank }

You log in to Globus with your UNM NetID, then connect your CARC account the
first time you open a CARC collection.

## Before you start

* **A Globus login.** Most people choose *University of New Mexico* on the
  Globus login page and sign in with their NetID. Any other Globus login
  (another university, ORCID, Google) also works.
* **An active CARC account** on Hopper or Easley, with your CARC username and
  password: the same ones you use for SSH and
  [Open OnDemand](../interactive/open-ondemand.md). If you don't have an
  account yet, start with [Getting started at CARC](overview.md).

Your CARC username can differ from your NetID. That's expected: Globus links
the two the first time you open a CARC collection.

## CARC collections

CARC has three Globus collections. All three show the same paths you use on
the clusters, so a path you copy from a terminal works in Globus.

| Collection | Opens in | Use it for |
| --- | --- | --- |
| [UNM CARC home](https://app.globus.org/file-manager?origin_id=858a3d27-0cbf-4de1-8dc8-89d14a3f1714){ target=_blank } | `/users/your-username` | Your home directory |
| [UNM CARC projects](https://app.globus.org/file-manager?origin_id=48dcb30d-f719-4c62-9741-ab730d44660d){ target=_blank } | `/projects` | Project storage for projects you belong to |
| [UNM CARC scratch](https://app.globus.org/file-manager?origin_id=7b90e69e-e02b-4c5f-91dd-c4b8eaa069e1){ target=_blank } | `/carc/scratch/users/your-username` | Personal and project scratch on `/carc/scratch` |

To find them in the File Manager, search for **UNM CARC**.

Globus acts as your CARC account, so it can read and write exactly what you
can on the clusters, within these areas:

* **Home:** your own home directory only. Other users' home directories aren't
  visible through Globus.
* **Projects:** you can open the directories of projects whose group you
  belong to. Every project's name is listed, but opening one you aren't a
  member of fails with *Permission denied*.
* **Scratch:** everything under `/carc/scratch`, including project scratch in
  `/carc/scratch/projects/`, subject to the usual file permissions.

Quotas and backup policies are the same as on the clusters; see
[Storage and backups](../systems/storage.md). Run `quotas` on a login node to
check your usage before a large transfer.

!!! note "Easley scratch isn't available through Globus"

    `/easley/scratch` (personal and project) isn't reachable from the CARC
    Globus collections. Transfer to `/carc/scratch` or your home or project
    directory, then copy the data into Easley scratch from an Easley login
    node.

## First-time setup

Setup takes a couple of minutes and happens once.

1. Go to [app.globus.org](https://app.globus.org){ target=_blank } and log in.
   Choose *University of New Mexico* and sign in with your NetID.
2. Open one of the CARC collections, for example
   [UNM CARC home](https://app.globus.org/file-manager?origin_id=858a3d27-0cbf-4de1-8dc8-89d14a3f1714){ target=_blank }.
3. Globus says the collection needs another login. Continue, and choose
   **UNM CARC**.
4. On the UNM CARC login page, enter your **CARC username and password**.
5. Globus asks to link this identity to your Globus account. Accept.
6. The File Manager opens in your home directory, `/users/your-username`.

To check the link, open **Settings → Identities** in Globus. You'll see
`your-username@carc.unm.edu` listed under your Globus account.

!!! warning "Administrative accounts"

    Accounts with administrative privileges can't use the CARC collections.
    Use your ordinary CARC account.

## Transferring files

A transfer always runs between two collections. In the File Manager, open a
CARC collection in one panel and the other end in the second panel, select
files, then click **Start**. You can close the browser; Globus emails you when
the transfer finishes.

* **Your laptop or desktop:** install
  [Globus Connect Personal](https://www.globus.org/globus-connect-personal){ target=_blank }.
  It turns your computer into a collection you can transfer to and from.
* **Another institution or a lab server:** search for its collection by name.
  You need an account there too.
* **Between CARC areas** (home, projects, scratch): open two CARC collections
  side by side.

Transfers to and from CARC are always encrypted. Sharing data with people
outside CARC through Globus isn't enabled yet.

## Logging in again

Every 24 hours, Globus asks for your CARC password again. When you open a CARC
collection after that, you'll see the UNM CARC login page; sign in as in step
4. You don't need to link anything again, and transfers that are already
running keep going.

!!! tip "Locked out after wrong passwords?"

    Five wrong passwords in a row lock the UNM CARC login for a few minutes,
    and the login page says your account is temporarily disabled. Wait two
    minutes and try again; repeated lockouts last longer, up to 15 minutes.
    The lockout also applies to Open OnDemand logins, but not to SSH or your
    running jobs. If your password has expired, see
    [Password reset and one-time passwords](password-reset.md).

## Troubleshooting

??? question "\"Identity set contains an identity from an allowed domain, but it does not map to a valid username\""

    Your CARC account isn't allowed to use Globus: it's an administrative
    account, or it isn't an active HPC account. Use your ordinary CARC
    account, or [open a ticket](../support/help.md).

??? question "The UNM CARC login rejects a password that works for SSH"

    Check that you typed your CARC username, not your NetID. After five
    tries, wait for the lockout to clear.

??? question "I linked the wrong CARC account"

    Log out of the UNM CARC login at
    [auth.alliance.unm.edu](https://auth.alliance.unm.edu/realms/carc/protocol/openid-connect/logout){ target=_blank },
    remove the wrong identity under **Settings → Identities** in Globus, then
    open the collection again.

??? question "A transfer is slow or stuck"

    Check its status under **Activity** in Globus. Globus retries on its own.
    If it stays stuck, [open a ticket](../support/help.md) with the transfer's
    task ID, which you'll find on its Activity page.

## Related pages

* [Transferring data](transferring-data.md) - scp and rsync for smaller transfers.
* [Storage and backups](../systems/storage.md) - paths, quotas, and what is backed up.
* [Getting help](../support/help.md) - open a ticket if Globus misbehaves.
