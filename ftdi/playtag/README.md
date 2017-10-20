
Usage
-----

- start XVC (Xilinx Virtual Cable) server (default TCP port 2542):
```
tools/jtag/xilinx_xvc.py ftdi FT01A
```

- on Xilinx Impact select "Output -> Cable setup", then "Open cable plugin"
  and type:

```
xilinx_xvc host=lxconga01.na.infn.it:2542 maxpacketsize=65535 disableversioncheck=true
```

- to load a SVF file by command line:

```
tools/jtag/loadsvf.py ftdi FT01A SVF=tools/jtag/spartan6_test.svf
```
