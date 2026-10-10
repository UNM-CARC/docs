---
title: "Logging in to CARC systems"
description: "Connect to CARC clusters with SSH from Linux, macOS, or Windows."
type: Guide
tags:
  - SSH
  - New users
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/logging_in.md"
    title: "UNM-CARC QuickBytes: logging_in.md"
    author: "team:unm-carc"
    last_modified: "2026-06-25T13:09:57-06:00"
---

# Logging in to CARC systems

To log in to the CARC systems and start computing you will need a terminal that can log in to remote systems using Secure Shell (SSH). If you are using a Linux or Mac machine you are in luck as they come bundled with a terminal that is ready to use. The terminal application packaged with your OS is great, but if you would like something with a bit more customization, utility, and flexibility there are other free options available. Below are a couple of options that CARC recommends. Note that iterm2 is only available on Mac, and MobaXterm is only available on Windows.


* iTerm2
* MobaXterm


If you are on windows, you can start with using Powershell, however it is recommended to install MobaXterm for a better overall experience.


Now that you have your terminal open you can log in. To do this type the following from the terminal prompt:

```bash
ssh <CARC-USERNAME>@<MACHINE-NAME>.alliance.unm.edu
```

Where `CARC-USERNAME` is the username you were assigned once your account was approved. `MACHINE-NAME` will be one of our carc systems; `hopper` or `easley`, for example. If this is your first time logging in, you will get a prompt asking you to accept your computer as a new authorized host. You can accept this first prompt, and you will then be prompted for your password. 

If you are unsure of your current password, please reference [the password reset quickbyte.](password-reset.md)


*This quickbyte was validated on 8/3/2026*

## Video walkthrough

**Logging into CARC Systems** — from the [CARC video tutorials](../training/videos.md):

<iframe class="carc-video" src="https://www.youtube-nocookie.com/embed/Puhaf6tCNO0" title="Logging into CARC Systems" loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<p class="carc-provenance" markdown>Migrated from [UNM-CARC QuickBytes](https://github.com/UNM-CARC/QuickBytes/blob/master/logging_in.md){target=_blank} (last source update 2026-06-25). Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/QuickBytes){target=_blank}.</p>
