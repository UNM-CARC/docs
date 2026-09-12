---
title: "Installing Perl libraries"
description: "Install Perl modules into your own home directory with cpan."
type: Guide
tags:
  - Perl
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/install_perl_libraries.md"
    title: "UNM-CARC QuickBytes: install_perl_libraries.md"
    author: "team:unm-carc"
    last_modified: "2026-07-30T10:33:04-06:00"
---

# Installing Perl libraries

Perl libraries can be installed to your home directory.

First, load a perl module.
Use `module spider perl` to view available perl modules on the cluster you are using.
In this example we will use a perl module available on Easley. Easley's perl modules don't need a separate compiler module loaded first.
```bash
$> module load perl/5.40.0-kptf
``` 

Next, start an interactive cpan shell:
```bash
$> perl -MCPAN -e shell
```

Direct cpan to your home directory:
```bash
cpan[1]> o conf makepl_arg INSTALL_BASE=~/perl5
```

Commit the changes to cpan:
```bash
cpan[1]> o conf commit
```

Exit cpan:

```bash
cpan[1]> exit
```

Now, you need to modify your environment variables.
This can be done in the terminal using the following four commands, but would need to be done once per login session before installing perl libraries.
Alternatively, you can add these commands to your `.bashrc` file to have them happen automatically upon logging in.
```bash
$> export PERL_MM_OPT="INSTALL_BASE=$HOME/perl5"
$> export PERL5LIB="$HOME/perl5/lib/perl5:$PERL5LIB"
$> export PATH="$HOME/perl5/bin:$PATH"
$> eval $(perl -I$HOME/perl5/lib/perl5 -Mlocal::lib)
```

You can now use the cpan commands to install perl modules/libraries:
```bash
$> cpan <library>
```

Some examples are:
```bash
$> cpan YAML
$> cpan Math::Utils
$> cpan Thread::Queue
```

<p class="carc-provenance" markdown>Migrated from [UNM-CARC QuickBytes](https://github.com/UNM-CARC/QuickBytes/blob/master/install_perl_libraries.md){target=_blank} (last source update 2026-07-30). Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/QuickBytes){target=_blank}.</p>
