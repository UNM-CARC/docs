---
title: "MATLAB Parallel Server"
description: "Use MATLAB Parallel Server to scale parpool jobs across multiple nodes."
type: Guide
tags:
  - MATLAB
  - Parallel
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/ParallelMatlabServer.md"
    title: "UNM-CARC QuickBytes: ParallelMatlabServer.md"
    author: "team:unm-carc"
    last_modified: "2021-02-24T17:43:53-07:00"
---

# MATLAB Parallel Server

MATLAB supports parallelization on desktop computers which can be used to increase the speed of analysis drastically. MATLAB also provides the MATLAB Parallel Server (previously the MATLAB Distributed Computing Server) which allows you to write MATLAB code on your local desktop or laptop computer and perform the computation using the CARC high-performance clusters. This QuickByte leads you through the steps needed to set this up. If you run into problems please send an email to help@carc.unm.edu and we will be happy to help.

Please ensure you have the MATLAB Parallel Toolbox installed on your local computer.

## How MATLAB Parallel Works Behind the Scenes
MATLAB parallel allows the MATLAB session you interact with on your local computer, also known as the MATLAB client, to talk to the Slurm scheduler at CARC to create jobs that run on a core, also known as the MATLAB worker. The Slurm scheduler allocates resources requested to users. One of the advantages of using MATLAB at CARC is the ability to scale up, or use many nodes for data intensive and/or computationally complex computations. To do this, you will request more workers from the Slurm scheduler by following the tutorial below (Workers window). If you request multiple workers, it is important to keep in mind that one worker will be running the batch script you have sent from your MATLAB client. This worker is sending your scripts to the other workers that will perform your computations. You can think about this lead MATLAB worker as a mirror of your MATLAB client that communicates with the Slurm scheduler and your scripts to accomplish your job. For more help on how to alter your scripts to take advantage of the scaling up abilities at CARC please visit the Mathworks [tutorials](https://www.mathworks.com/help/parallel-computing/what-is-parallel-computing.html){target=_blank}.


### MATLAB Parallel Server Client Configuration

Once MATLAB is installed on your local machine (the MATLAB version on your local machine must match the version on the CARC cluster) click "add-ons" to open Add-on explorer. Search for Slurm.

Click on the link "Parallel Computing Toolbox plugin for MATLAB Parallel Server with Slurm".

Click the "install" button and the plugin will install and a wizard is started.

![Install](../assets/images/quickbytes/ParallelMatlabInstall.png)

![Wizard1](../assets/images/quickbytes/ParallelMatlabWizard1.png)
Choose UNIX in the cluster type

![Wizard2](../assets/images/quickbytes/ParallelMatlabWizard2.png)

Select no for shared job location.

![Wizard3](../assets/images/quickbytes/ParallelMatlabWizard3.png)

Enter the address of the cluster you would like to use: for example, easley.alliance.unm.edu or hopper.alliance.unm.edu.

Enter `/users/<your username>/` for the path to the Slurm scripts (remote job storage location) that MATLAB will create on the cluster.

Select unique subfolders.
  
![Wizard4](../assets/images/quickbytes/ParallelMatlabWizard4.png)

Select the number of workers and number of threads per worker. This may depend on the program you are running but in general you should have one worker per core on the cluster. For set up and validation leave the number of workers at 1. Leave the threads per worker at 1 unless your software requires more threads.

Specify the path to the matlab installation on the compute nodes: `/opt/local/MATLAB/R2024b` (or whichever version you need — `module avail matlab` on the cluster shows what's currently installed). It is important that you are running the same version of MATLAB locally as you specify here for the cluster.

![Wizard6](../assets/images/quickbytes/ParallelMatlabWizard6.png)

Choose flexnet for the license

![Wizard7](../assets/images/quickbytes/ParallelMatlabWizard7.png)

Name your profile. For example "R2024b_Easley_Slurm"

![Wizard8](../assets/images/quickbytes/ParallelMatlabWizard8.png)

Review your profile settings and create the profile.

![Wizard10](../assets/images/quickbytes/ParallelMatlabWizard10.png)

You can create multiple profiles for different CARC clusters and numbers of workers.

```matlab
parallel.cluster.generic.runProfileWizard()
```

## Setting your IP Address

In the next steps MATLAB will need to know your local IP address to allow incoming/outgoing connections on your computer.

You will likely have to tell the system the IP address or hostname of your local machine. This is so the CARC cluster can communicate with your laptop or desktop. You will set the hostname with pctconfig (Parallel Config Toolbox). You can either type the hostname in directly or attempt to have MATLAB find it for you with the following commands:

OS X
```
[~,name]=system('ipconfig getifaddr en0');
pctconfig('hostname',name);
```

Linux
```
%%
[~,name]=system('hostname -i');
pctconfig('hostname',name);
```

Windows 10

Look up your computers IP address and enter:

```
%%
pctconfig('hostname',"<your IP address>");
```


### Validating the Configuration

Select "parallel" then create/manage clusters. 

Choose the profile you just created. In this example, the profile name is "R2024b_Easley_Slurm"

![Validating1](../assets/images/quickbytes/ParallelMatlabValidate1.png)

Select the profile you just created and select the validation tab. Press the validate button.

![Validating2](../assets/images/quickbytes/ParallelMatlabValidate2.png)

It will ask for your CARC username, and here you can also select your ssh keyfile if you use one (cmd+shift+. to reveal hidden directories so you can see you ~/.ssh folder and select your private key), or just enter your password.

MATLAB will now validate your setup. If you run into trouble please contact CARC support at help@carc.unm.edu.

This completes the install and configuration.

We have found it best to restart MATLAB at this point, otherwise setting the hostname in the next step may not work.

### Writing Parallel Matlab Code


Once you have set the hostname you can run your parallel MATLAB code. Mathworks provides extensive documentation on using parallelism in MATLAB: [Mathworks Docs](https://www.mathworks.com/help/parallel-computing/getting-started-with-parallel-computing-toolbox.html){target=_blank}

The very simple program that follows demonstrates how to run parallel code using MATLAB. The code uses parfor, which can often be used to replace a for loop in serial MATLAB code, to distribute the work across 10 parallel workers.

```
n_workers = 10;                  % We will request 10 workers to run in parallel
p = parpool('R2024b_Easley_Slurm', n_workers); % Create the pool of workers using the profile created earlier with 10 workers.
parfor i = 1:100                % Define a parallel loop that will be distributed across the 10 workers.
i                               % Print the value of i for this iteration.
end                   
delete(p);                      % Clean up the worker pool
```

## Monitoring MATLAB Jobs
To check that your jobs are indeed running at CARC, you can log in (ssh) to the cluster you have submitted your job to and check your job status. The command below shows only your jobs. 

```
ssh username@easley.alliance.unm.edu 
```

```
squeue -u <username>
```

If you are testing small scripts, they may run before you can type squeue. To watch your jobs, you can type watch before the squeue (or any other) command and it will re-run the command every 2sec. This is a good way to watch progress.

<p class="carc-provenance" markdown>Migrated from [UNM-CARC QuickBytes](https://github.com/UNM-CARC/QuickBytes/blob/master/ParallelMatlabServer.md){target=_blank} (last source update 2021-02-24). Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/QuickBytes){target=_blank}.</p>
