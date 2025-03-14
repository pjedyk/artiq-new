# Digilent Genesys ZU-5EV

[Genesys ZU-5EV](https://digilent.com/reference/programmable-logic/genesys-zu/start) is a development kit from [Digilent](https://digilent.com/) with [Zynq UltraScale+ (ZU5EV)](https://www.amd.com/en/products/adaptive-socs-and-fpgas/soc/zynq-ultrascale-plus-mpsoc.html) on-board. ZU5EV contains four Cortex-A53 and two Cortex-R5 cores.

## Build system

[GNU `make`](https://www.gnu.org/software/make/manual/make.html) serves as top build system.

The process has four stages. You may stop at any stage, passing the stage name to the `make` program:

```Shell
make 0_platform  # stop immediately after 0_platform
make 1_gateware  # stop immediately after 1_gateware
make 2_firmware  # stop immediately after 2_firmware
make 3_bootable  # build everything
make all  # build everything
make  # build everything
```

**NOTE:** `make 1_gateware` may also do `0_platform`.

**TIP:** If you have set up shell completions, `make 0<TAB>` should immediately expand to `make 0_platform`.

### Stages dependencies

`0_platform` depends on:
- nothing.

`1_gateware` depends on :
- `0_platform`.

`2_firmware` depends on:
- nothing.

`3_bootable` depends on:
- `0_platform`,
- `1_gateware`,
- `2_firmware`.

Thus:
- `0_platform` and `2_firmware` may be built independently and in parallel.
- `1_gateware` must be built after `0_platform`.
- `3_bootable` must be built at the end.

**You are allowed and encouraged to use the `make -jX` flag**, which will utilise the advantage of parallelism. The system is designed to propagate the job server to underlying build layers (when possible), like Cargo for Rust.

### Stages artifacts

The default build directory is `build`. You may override this setting by using `make O=../build-somewhere-else`.

The `0_platform` stage is a [TCL](https://www.tcl-lang.org/) script that uses [Vivado](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado.html) to generate:
- `platform.xsa` file for [Vitis](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vitis.html),
- `*.xci` files to be imported as IPs in [Migen](https://m-labs.hk/gateware/migen/),
- `mi_*.txt` and other files for Vivado-Migen integration.

The `1_gateware` stage is a Migen project (implies [Python](https://www.python.org/) and Vivado usage) which build artifact is:
- the bitstream for the PL unit of the ZCU5EV (`top.bit`).

The `2_firmware` stage is a Cargo project (implies [Rust](https://www.rust-lang.org/)) which build artifact is:
- a static C-linkable library (`librust_firmware.a`) with most firmware logic.

The `3_bootable` stage is a Vitis project managed by a Python script (used as `vitis -s vitis_script.py`) that provides:
- development environment generated from XSA file (from `0_platform` stage),
- FSBL and application images.

Additionally, the `make` program generates a `boot.bif` file and uses `bootgen` to create a `boot.bin`. Thus, the final artifact of the `3_bootable` is `boot.bin`.

### The application image

The application, written in C, is a glue layer for the Rust firmware. In the simplest scenario, it just calls `rust_main()` from `main()`.

You may use Xilinx/AMD Standalone Library in the application and export several functions to the Rust firmware, significantly reducing the effort of reverse-engineering the HAL library.

Another advantage is getting a fully-initialised CPU and C runtime before jumping into Rust code.

## Programming

The `boot.bin` image may be flashed into the on-board QSPI using the `program_flash` command:

```Shell
program_flash -f build/boot.bin -fsbl build/vitis-ws/hw_pf/zynqmp_fsbl/build/fsbl.elf
```

The `program_flash` is a part of Vitis.

## Debugging with GDB

Use `xsdb`, which is a part of Vitis, to launch the debug server:

```Plain
$ xsdb

****** System Debugger (XSDB) v2024.2
  **** Build date : Oct 29 2024-10:16:47
    ** Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
    ** Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.


xsdb% connect
tcfchan#0
xsdb% targets
  1  PS TAP
     2  PMU
     3  PL
  4  PSU
     5  RPU (Reset)
        6  Cortex-R5 #0 (RPU Reset)
        7  Cortex-R5 #1 (RPU Reset)
     8  APU
        9  Cortex-A53 #0 (Running)
       10  Cortex-A53 #1 (Power On Reset)
       11  Cortex-A53 #2 (Power On Reset)
       12  Cortex-A53 #3 (Power On Reset)
xsdb% █
```

Select the target you are going to debug and reset the processor:

```Plain
xsdb% targets 9
xsdb% rst -por
xsdb% rst -srst
xsdb% Info: Cortex-A53 #0 (target 9) Stopped at 0xffff0000 (Reset Catch)
xsdb% █
```

**NOTE:** The `rst -por` is unnecessary. However, it helps escape severe invalid conditions.

Now, being sure the processor is in a valid state (note "Reset Catch"), you may use multi-arch GDB:

```Plain
$ gdb-multiarch build/vitis-ws/app/build/app.elf

GNU gdb (Ubuntu 12.1-0ubuntu1~22.04.2) 12.1
Copyright (C) 2022 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<https://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from build/vitis-ws/app/build/app.elf...
(gdb) target extended-remote :3001
Remote debugging using :3001
0x00000000ffff0000 in ?? ()
(gdb) thb main
Hardware assisted breakpoint 1 at 0xc98: file /project/boards/genesys_zu-5ev/build/vitis-ws/app/src/main.c, line 7.
(gdb) c
Continuing.

Temporary breakpoint 1, main () at /project/artiq-zynqmp/boards/genesys_zu-5ev/build/vitis-ws/app/src/main.c:7
7           rust_main();
(gdb) █
```

**NOTE:** Do not close `xsdb` as it is a debug server!
