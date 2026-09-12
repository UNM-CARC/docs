---
title: "Transferring data"
description: "Move data to and from CARC systems with scp, rsync, sftp, and Globus."
type: Guide
tags:
  - Data
  - Storage
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/transfer_data.md"
    title: "UNM-CARC QuickBytes: transfer_data.md"
    author: "team:unm-carc"
    last_modified: "2026-08-03T20:10:33-06:00"
---

# Transferring data

### Where is your data?

Your home directory, `/users/your-user-name/`, is shared across all CARC machines, meaning that once your data has been uploaded to your home directory, it is accessible regardless of which machine you are logged in to.

### Graphical User Interface (GUI) options

There are several options available for data transfer that employ a GUI for ease of use. Several options are listed below, linked to the homepage for each piece of software, with documentation on how to use it.

* [FileZilla](https://filezilla-project.org/){target=_blank}
* [WinSCP](https://winscp.net/eng/index.php){target=_blank}
* [Fetch](https://fetchsoftworks.com/){target=_blank}
* [CyberDuck](https://cyberduck.io/){target=_blank}

FileZilla is available for both Windows and Unix systems, whereas WinSCP is Windows-only and Fetch is macOS-only. GUI-based programs are very user-friendly and well-suited to those who are less comfortable with the Linux command-line interface. Unfortunately, the programs listed above, and other GUI-based programs, use File Transfer Protocol (FTP), which has a relatively low transfer speed and is best suited to smaller file sizes.

### Command-line interface (CLI) options

For larger files, it is recommended that you use one of several programs implemented as a command-line interface. These programs have several benefits over their GUI-based counterparts, including higher transfer speeds and the ability to resume a transfer if it is interrupted, without having to restart from the beginning. Below are two popular options with example commands and links for more advanced usage.

#### Secure Copy (SCP)

Transfer from local machine to CARC:
```bash
scp /your-file your-username@easley.alliance.unm.edu:target-directory/
```

Transfer from CARC to local machine:
```bash
scp your-username@easley.alliance.unm.edu:your-file /target-directory/
```

#### Remote Sync (RSYNC)

Transfer from local machine to CARC:
```bash
rsync -vhatP /your-file your-username@easley.alliance.unm.edu:target-directory
```

Transfer from CARC to local machine:
```bash
rsync -vhatP your-username@easley.alliance.unm.edu:your-file /target-directory/
```

The `-vhatP` flags instruct rsync to print the progress of the transfer verbosely and in a human-readable format.

!!! tip "Large transfer keeps hanging or timing out?"

    A single huge `rsync` that repeatedly stalls usually points to network
    stability on the client side (wireless, VPN, off-campus path) rather than
    a problem at CARC:

    - **Chunk the transfer** — loop over subdirectories with separate `rsync`
      calls instead of one massive invocation. Since `rsync` skips files that
      have already arrived, re-running after a failure resumes where it left off.
    - Note whether it dies at the same file each run or at random, your client
      OS, wired vs. wireless, and on- vs. off-campus. Those details make a
      [support ticket](../support/help.md) much faster to resolve — support can
      also try reproducing the transfer to rule out a CARC-side issue.
    - Increase verbosity (`-v`/`-vv`) only on a **small subset** of the data
      while diagnosing, not on the full transfer.

As you can see, the syntax for these two programs is very similar; however, the options for advanced usage are unique to each one. The examples above cover only basic data transfers — refer to the links provided, or use `man programname` for the CLI options, to optimize each tool for maximum data transfer efficiency and speed.

*This quickbyte was validated on 6/22/2026*

## Video walkthrough

**Transferring data** — from the [CARC video tutorials](../training/videos.md):

<iframe class="carc-video" src="https://www.youtube-nocookie.com/embed/2UphEzHOHGM" title="Transferring data" loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<p class="carc-provenance" markdown>Migrated from [UNM-CARC QuickBytes](https://github.com/UNM-CARC/QuickBytes/blob/master/transfer_data.md){target=_blank} (last source update 2026-08-03). Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/QuickBytes){target=_blank}.</p>
