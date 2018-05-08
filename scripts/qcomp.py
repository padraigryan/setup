irun -64 -sv +UVM_TESTNAME=dummy +TB_CONFIG_DEBUGPRINT=1 +define+USE_SV_PRINTF +define+CHIP_TOP -uvmlinedebug -gui -notimezeroasrtmsg -timescale 1ns/1ns -access +rwc -work tmp ams_vcd_gen_test.sv
