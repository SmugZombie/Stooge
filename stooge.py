#!/usr/bin/env python
# stooge.py
# Ron Egli
# Versopm 0.2
# github.com/smugzombie

# Python Imports
import json
import subprocess
import pprint
import argparse
import commands

# Arguments
arguments = argparse.ArgumentParser()
arguments.add_argument('--list','-l', help="List current devices in the config", required=False, action='store_true')
arguments.add_argument('--host','-H', help="Select a specific host from the config", required=False, default="")
arguments.add_argument('--command','-c', help="The command you want to push to selected hosts", required=False, default="")
arguments.add_argument('--sudo','-s', help="If the command is to be run via SUDO", required=False, action='store_true')
arguments.add_argument('--verbose','-v', help="Enables verbose output from host", required=False, action='store_true')
args = arguments.parse_args()
listarg = args.list
host = args.host
command = args.command
sudo = args.sudo
verbose = args.verbose

# Styles
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Load hosts
with open('stooge.json') as data_file:
    data = json.load(data_file)

# Count Hosts
hostcount = len(data["hosts"])

# Get Hosts Function
def getHosts():
    print "------------------------------------"
    print "|  Listing Stooge Hosts            |"
    print "------------------------------------"
    print "Total Hosts: " + str(hostcount)
    for x in xrange(hostcount):
        print data["hosts"][x]["id"]
    return

# Run Remote Command
def runCommand(user, host, command):
        if verbose is True:
                output = str(commands.getstatusoutput('ssh '+user+'@'+host+" "+command))
        else:
                output = commands.getstatusoutput('ssh '+user+'@'+host+" "+command)[1]
        return output

# If list argument is provided, List and exit.
if listarg is True:
        getHosts()
        exit() # End script

# If a command is provided, validate host and continue
elif command != "":
        if verbose is True:
                print "Command: ",command
        if host == "" or host == "all":
                for x in xrange(hostcount):
                    if sudo is True:
                        user = data["hosts"][x]["sudouser"]
                    else:
                        user = data["hosts"][x]["user"]
                    host = data["hosts"][x]["id"]
                    print bcolors.FAIL + host + bcolors.ENDC
                    print bcolors.OKBLUE + "    " + runCommand(user, host, command) + bcolors.ENDC
        else:
                for x in range(hostcount):
                    foundhost = data["hosts"][x]["id"]
                    if foundhost == host:
                        if sudo is True:
                            user = data["hosts"][x]["sudouser"]
                        else:
                            user = data["hosts"][x]["user"]
                        break
                    else:
                        # Do Nothing
        #       if user == "":
        #           print "Host not found"
        #           exit()
        #       else:
                        print bcolors.FAIL + host + bcolors.ENDC
                        print bcolors.OKBLUE + "    " + runCommand('root', host, command) + bcolors.ENDC
        exit() # End Script

# If nothing is provided, provide user with usage.
else:
        print "Hello World"
