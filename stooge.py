#!/usr/bin/env python
# stooge.py - "one who plays a subordinate or compliant role to a principal"
# Ron Egli
# Version 0.4
# github.com/smugzombie - stooge.us

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
        print "Current Stooge Hosts"
        print ""
        for x in xrange(hostcount):
                print " ", x, data["hosts"][x]["id"]
        print ""
        print "Total Stooge Hosts: ", hostcount
        return

# Run Remote Command
def runCommand(user, host, command):
        output = commands.getstatusoutput('ssh '+user+'@'+host+" "+command)
        json = {}
        json['errcode'] = output[0]
        json['response'] = output[1]
        if verbose is True:
                if json['errcode'] == 0:
                        output = bcolors.OKGREEN + "Success!" + bcolors.ENDC + "\n    " + bcolors.OKBLUE + str(json['response']) + bcolors.ENDC
                else:
                        output = bcolors.FAIL + "Error! " + str(json['errcode']) + bcolors.ENDC + " \n    " + bcolors.OKBLUE  + str(json['response']) + bcolors.ENDC
        else:
                output = bcolors.OKBLUE + json['response'] + bcolors.ENDC

        return output

def getUsage():
        print "Usage: stooge -H [HOSTNAME/IP]... -c [COMMAND]... -s"
        print "Run commands easily via ssh on remote devices"
        print ""
        print "  -H, --host            the targeted host for the remote command"
        print "  -c, --command         the command to be run on the remote host(s)"
        print "  -s. --sudo            if enabled, will use sudouser in place of standard"
        print "  -v, --verbose         enabled verbose output of commands that are run"
        print ""
        print "Examples:"
        print "  stooge -h server1 -c \"shutdown -r now\" -s "
        print "      - Tells the host server1 to shutdown/reboot now using a sudo user"
        print "  stooge -c \"who\""
        print "      - Tells all available hosts to return 'who' is logged in, using a"
        print "         standard user"
        print ""
        print "Coming Soon:"
        print "  -g, --group           targets a specific group of predefined hosts"
        print "  -a, --add             adds a new host to the stooge configuration "
        return

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
                    print "    ", runCommand(user, host, command)
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
                        print "    ", runCommand('root', host, command)
        exit() # End Script

# If nothing is provided, provide user with usage.
else:
        getUsage()
        exit()
