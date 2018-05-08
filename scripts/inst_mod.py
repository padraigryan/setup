#!/home/prya/usr/bin/python

import sys
import re

def get_vhdl_port_list(vhdl_file):
  ''' Parse the top-level vhdl for the ports list '''
  ports = []
  function_detected = False;
  module_name = None

  for line in vhdl_file.split('\n'):
    # Remove comments
    line = line.split("--")[0]
    sline = line.strip().split()
    if(len(sline) >= 3):
      port = {}

      # Find the module name
      if(sline[0] == "entity"):
        module_name = sline[1];

      if((sline[2] == "in") | (sline[2] == "out")):
        if(sline[2] == "in"):
          port["type"] = "input";
        else:
          port["type"] = "output";
        port["name"] = sline[0];
        port_size = re.findall(r"\(.*\)", line)
        if(len(port_size) > 0):
          port["size"] =  port_size[0].replace(" downto ", ':')
          port["size"] =  port["size"].replace("(", '[')
          port["size"] =  port["size"].replace(")", ']')
        else:
          port["size"] = ""
        port["test_pin"] = ""
        ports.append(port)

  if(module_name == None):
    print "Error: couldn't find module name in file" 
    sys.exit()

  return (module_name, ports);

def get_verilog_port_list(verilog_file):
  ''' Parse the top-level verilog for the ports list '''
  ports = []
  function_detected = False;
  module_name = None

  for line in verilog_file.split('\n'):
    # Remove comments
    line = line.split("//")[0]
    sline = line.strip().split()
    if(len(sline) >= 2):
      port = {}

      # Find the module name
      if(sline[0] == "module"):
        module_name = sline[1].split('(')[0]

      # Deal with functions that have inputs/outpus as well
      if(sline[0] == "function"):
        function_detected = True
        continue;
      if(function_detected):
        continue;
      if(sline[0] == "endfunction"):
        function_detected = False
        continue;

      # TODO: Handle multiple ports on a single line
      if((sline[0] == "input") | (sline[0] == "output")| (sline[0] == "inout")):
        port["type"] = sline[0]
        port["name"] = sline[-1].rstrip(',').rstrip(';')
        port['name'].replace(';','')
        port["size"] = re.findall(r"\[.*\]", line)
        if(len(port["size"]) > 0):
          port["size"] =  port["size"][0]
        else:
          port["size"] = ""
        port["test_pin"] = ""
        ports.append(port)
      elif(sline[0] == "localparam"):
        port["type"] = "localparam"
        port["size"] = ""
        port["name"] = line
        port["test_pin"] = ""

        ports.append(port)

  if(module_name == None):
    print "Error: couldn't find module name in file" 
    sys.exit()

  return (module_name, ports);

def declare_signals(module_name, ports):
  # Declare the signals
  disp_str = "\n  // " + module_name + "\n"
  for port in ports:
    if(port["type"] == "localparam"):
      continue
    else:
      disp_str = disp_str + "  wire {0:44}{1};\n".format(port["size"],  port["name"])

  return disp_str

###############################################################################
# Connect in the same order as declared in the module
def instance_module_style1(module_name, ports):

  # Instance the module
  disp_str = "\n{0} {0} (\n".format(module_name)

  first_pin = True;
  for port in ports:
    if(port["type"] != "localparam"):
      if(first_pin == False):
        disp_str = disp_str + "),\n"
      first_pin = False;

      disp_str = disp_str + "    .{0:42}({0}".format(port["name"])
  disp_str = disp_str + ")\n  );\n"
  return disp_str

###############################################################################
# Connect with inputs/outputs grouped together
def instance_module_style2(module_name, ports):

  # Instance the module
  disp_str = "  {0} {0} (\n".format(module_name)

  first_pin = True;
  disp_str = disp_str + "    // Inputs\n"
  for port in ports:
    if((port["type"] != "localparam") & (port["type"] == "input")):
      if(first_pin == False):
         disp_str = disp_str + "),\n"
      first_pin = False;

      disp_str = disp_str + "    .{0:42}({0}".format(port["name"])

  disp_str = disp_str + "),\n\n    // Outputs\n"

  first_pin = True;
  for port in ports:
    if( (port["type"] != "localparam") & (port["type"] == "output") ):
      if(first_pin == False):
        disp_str = disp_str + "),\n"
      first_pin = False;
      disp_str = disp_str + "    .{0:42}({0}".format(port["name"])

  disp_str = disp_str + ")\n  );\n"
  return disp_str

###############################################################################
# Connect according the names provided
def instance_module_style3(module_name, ports):

  # Instance the module
  disp_str = "\n{0} {0} (\n".format(module_name)

  first_pin = True;
  for (port, sig) in ports:
    if(first_pin == False):
      disp_str = disp_str + "),\n"
    first_pin = False;

    disp_str = disp_str + "    .{0:42}({1}".format(port, sig)
  disp_str = disp_str + ")\n  );\n"

  return disp_str

def instance_module(fn):
    f = open(fn)

    if(fn.split(".")[-1] == "vhd"):
      (mn, p) = get_vhdl_port_list(f.read())
    else:
      (mn, p) = get_verilog_port_list(f.read())

    return instance_module_style1(mn, p)

if __name__ == "__main__":  

  if(len(sys.argv) != 2):
    print "Usage: inst_mod <file_name>"
  else:
    fn = sys.argv[1]
    f = open(fn)

    if(fn.split(".")[-1] == "vhd"):
      (mn, p) = get_vhdl_port_list(f.read())
    else:
      (mn, p) = get_verilog_port_list(f.read())

    print declare_signals(mn, p)
    print instance_module_style1(mn, p)


