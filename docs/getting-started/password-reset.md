---
title: "Password reset and one-time passwords"
description: "Reset your CARC password and manage one-time-password (OTP) settings."
type: Guide
tags:
  - Accounts
  - Security
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/password_reset.md"
    title: "UNM-CARC QuickBytes: password_reset.md"
    author: "team:unm-carc"
    last_modified: "2026-06-22T09:56:10-06:00"
---

# Password reset and one-time passwords

To reset your password, you can use the link [here](https://mokey.alliance.unm.edu/auth/login){target=_blank}

After entering your CARC username, you can follow the prompts and reset your password. 

!!! tip "If the reset doesn't seem to take"

    - "Forgot password" needs your **exact CARC username** — confirm it first,
      and [open a ticket](../support/help.md) if you are unsure of your login name.
    - A freshly reset password can fail on the first attempt: Easley and Hopper
      share one authentication backend and the new password can take a little
      while to propagate. Try again shortly — and if needed, simply run the
      reset a second time.
    - If you can log into one cluster but not the other after a reset, SSH to
      the affected cluster *from* the working cluster's login node (e.g.
      `ssh easley` from a Hopper session) as a workaround, and
      [open a ticket](../support/help.md) if direct login keeps failing.

You can also log in with the above link to find other information about your CARC account, see which groups you are a part of, activate two-factor authentication, and add SSH keys to your account.

*This quickbyte was validated on 6/22/2026*

<p class="carc-provenance" markdown>Migrated from [UNM-CARC QuickBytes](https://github.com/UNM-CARC/QuickBytes/blob/master/password_reset.md){target=_blank} (last source update 2026-06-22). Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/QuickBytes){target=_blank}.</p>
