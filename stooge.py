#!/usr/bin/env python
# stooge.py - "one who plays a subordinate or compliant role to a principal"
# Ron Egli
# Version 0.7.7
# github.com/smugzombie - stooge.us

# Python Imports
import json;     import subprocess;   import pprint;   import argparse;
import commands; import os;           import textwrap; import atexit

# Defaults
currentdir = str(os.path.dirname(os.path.realpath(__file__)))
config = currentdir+"/stooge.json"
blankconfig = "{\"config\":{\"masteridentityfile\" : \"\", \"lockconfig\" : \"false\", \"configversion\" : \"0.4\", \"checkforupdates\" : \"true\"},\"hosts\":[]}"

# Arguments
arguments = argparse.ArgumentParser()
arguments.add_argument('--list','-l', help="List current devices in the config", required=False, action='store_true')
arguments.add_argument('--host','-H', help="Select a specific host from the config", required=False, default="")
arguments.add_argument('--command','-c', help="The command you want to push to selected hosts", required=False, default="")
arguments.add_argument('--sudo','-s', help="If the command is to be run via SUDO", required=False, action='store_true')
arguments.add_argument('--verbose','-v', help="Enables verbose output from host", required=False, action='store_true')
arguments.add_argument('--add', help="Allows the user to add a new host", required=False, action='store_true')
arguments.add_argument('--remove', help="Allows the user to remove a previous host", required=False, action='store_true')
arguments.add_argument('--debug', help="Enables Debugging", required=False, action='store_true')
args = arguments.parse_args()
listarg = args.list
host = args.host.replace(' ', '').lower()
command = args.command
# Additional Options
sudo = args.sudo; verbose = args.verbose;
# Add / Remove Hosts
addaction = args.add; remaction = args.remove;
# Debugging
debug = args.debug

# Styles
class bcolors:
        HEADER = '\033[95m';  OKBLUE = '\033[94m';   OKGREEN = '\033[92m';
        WARNING = '\033[93m'; FAIL = '\033[91m';     ENDC = '\033[0m';
        BOLD = '\033[1m';     UNDERLINE = '\033[4m';

# Functions

def createBlankConfig():
        try: file = open(config, "w"); file.write(blankconfig)
        except: print "Error! Unable to write to file (", config, ")."
        else: print "Config created successfully. Please add hosts to ", config; exit()
        return

# Get Hosts Function
def listHosts():
        print "Current Stooge Hosts"; print ""
        if hostcount > 0:
                for x in xrange(hostcount): print " ", x, data["hosts"][x]["id"]
                print ""; print "Total Stooge Hosts: ", hostcount
        else: print "No current Stooge Hosts."
        return

# Run Remote Command
def runCommand(user, host, command):
        output = commands.getstatusoutput('ssh '+user+'@'+host+" "+command)
        json = {}; json['errcode'] = output[0]; json['response'] = output[1]
        if json['response'] == "" and json['errcode'] == 0: json['response'] = "(successful with no output)"
        if verbose is True:
                if json['errcode'] == 0:
                        output = bcolors.OKGREEN + "Success!" + bcolors.ENDC + "\n" + bcolors.OKBLUE + str(json['response']) + bcolors.ENDC
                else:
                        output = bcolors.FAIL + "Error! " + str(json['errcode']) + bcolors.ENDC + " \n" + bcolors.OKBLUE  + str(json['response']) + bcolors.ENDC
        else: output = bcolors.OKBLUE + json['response'] + bcolors.ENDC
        return output

def checkDuplicates(nickname):
        if hostcount > 0:
                for x in xrange(hostcount):
                        hostname = data["hosts"][x]["id"];
                        if hostname == nickname: return True
                return False

def getUsage():
        print "Usage: stooge -H [HOSTNAME/IP]... -c [COMMAND]... -s"
        print "Run commands easily via ssh on remote devices"
        print ""
        print "  -H, --host            the targeted host for the remote command"
        print "  -c, --command         the command to be run on the remote host(s)"
        print "  -s. --sudo            if enabled, will use sudouser in place of standard"
        print "  -v, --verbose         enabled verbose output of commands that are run"
        print "  --add                 adds a new host to the stooge configuration "
        print "  --remove              removes a selected host from the stooge configuration "
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
        return

def promptCreateNew():
        print "Would you like us to create a new one? (Y/N)"
        answer = raw_input()
        if answer == "Y" or answer == "y" or answer == "yes" or answer == "YES":
                createBlankConfig(); exit()
        elif answer == "N" or answer == "n" or answer == "no" or answer == "NO":
                print "Please locate or create a valid config file and try again."; exit()
        else:
                print "Invalid entry. Try again. (Y/N)"; promptCreateNew()

def loadConfig():
# Load hosts
        global data; global hostcount; global configdata; global hosts
        if os.path.isfile(config) is True:
                with open(config) as data_file:
                        try:
                                data = json.load(data_file)
                                # Count Hosts
                                hostcount = len(data["hosts"])
                        except:
                                print "Error: Config file found, but corrupt or blank."
                                exit()
                        if hostcount > 0:
                                hosts = {}
                                for x in xrange(hostcount):
                                        hosts[x] = data["hosts"][x]['id']
        else:
                print "Error: Config file not found. (", config,")"
                promptCreateNew()
        return

def formatOutput(input):
        prefix = "    "; preferredWidth = 70
        wrapper = textwrap.TextWrapper(initial_indent=' '*len(prefix),width=preferredWidth,subsequent_indent=' '*len(prefix))
        return wrapper.fill(input)

def testPing(host):
        if OS == "CYGWIN":
                output = commands.getstatusoutput("timeout 1 ping " + host + " -n 1 | grep -E -o 'Received = [0-9]+' | awk {'print $3'}")[1]
        elif OS == "LINUX":
                output = commands.getstatusoutput("timeout 1 ping " + host + " -c 1 | grep -E -o '[0-9]+ received' | cut -f1 -d' '")[1]
        elif OS == "OSX":
                output = commands.getstatusoutput("timeout 1 ping " + host + " -c 1 | grep -E -o '[0-9]+ received' | cut -f1 -d' '")[1]
        else:
                output = commands.getstatusoutput("echo 0'")[1]
        if str(output) != "1":
                output = "0";
        return output

def getOS():
        global OS
        output = commands.getstatusoutput('uname')[1]
        if output.find("CYGWIN") != -1:
                output = "CYGWIN"
        elif output.find("Linux") != -1:
                output = "LINUX"
        elif output.find("Darwin") != -1:
                output = "OSX"
        OS = output
        return

def addHost():
        global configdata; global data
        if data["config"]["lockconfig"] == "true":
                print "The config file is currently locked. Please manually edit the file and change 'lockconfig' to 'false'"
                exit()

        proceed = False
        while proceed is False:
                print "Enter a valid hostname. (Valid resolvable hostname or IP)"
                hostname = raw_input().replace(' ', '').lower()
                if hostname == "":
                        proceed = False
                else:
                        online = testPing(hostname)
                        if online == "1":
                                print "Do you wish to continue with", hostname,"? (Y/N) [Default Y]"
                                answer = raw_input()
                                if answer == "y" or answer == "Y" or answer == "":
                                        proceed = True
                        else:
                                print "Unable to resolve",hostname,". Please enter a new hostname."
        proceed = False
        while proceed is False:
                print "Would you like to give this host a nickname for easier access? If no, hostname will be used. (Y/N) [Default Y]"
                answer = raw_input()
                if answer == "n" or answer == "N":
                        nickname = hostname
                        proceed = True
                elif answer == "y" or answer == "Y" or answer == "":
                        print "What nickname would you like to use for", hostname,"?"
                        nickname = raw_input().replace(' ', '').lower()
                        if checkDuplicates(nickname) is True:
                                print "The nickname",nickname,"is already in use! Please use a different nickname."
                        else:
                                print "Is", nickname,"Correct? (Y/N) [Default Y]"
                                answer = raw_input()
                                if answer == "Y" or answer == "y" or answer == "":
                                        proceed = True
                                        break
                                else:
                                        proceed = False
                else:
                        proceed = False

        proceed = False
        while proceed is False:
                print "Enter the standard username for ", hostname,". (Blank if none)"
                username = raw_input()
                if username == "":
                        print "No standard username? (Y/N) [Default Y]"
                else:
                        print "Is",username,"correct? (Y/N) [Default Y]"
                answer = raw_input()
                if answer == "y" or answer == "Y" or answer == "":
                        proceed = True

        proceed = False
        while proceed is False:
                print "Enter the sudo username for ", hostname,". (Blank if none)"
                sudousername = raw_input()
                if sudousername == "":
                        print "No sudo username? (Y/N) [Default Y]"
                else:
                        print "Is",sudousername,"correct? (Y/N) [Default Y]"
                answer = raw_input()
                if answer == "y" or answer == "Y" or answer == "":
                        proceed = True

        proceed = False
        while proceed is False:
                print "Enter the group", hostname,"belongs to (Blank for Default)"
                group = raw_input()
                if group == "":
                        print "No group? (Y/N) [Default Y]"
                else:
                        print "Is",group,"correct? (Y/N) [Default Y]"
                answer = raw_input()
                if answer == "y" or answer == "Y" or answer == "":
                        proceed = True

        proceed = False
        while proceed is False:
                print "If required, provide the path to the non default SSH Key", hostname,"(Blank for Default)"
                keyfile = raw_input()
                if keyfile == "":
                        print "No special SSH Key? (Y/N) [Default Y]"
                else:
                        print "Is",keyfile,"correct? (Y/N) [Default Y]"
                answer = raw_input()
                if answer == "y" or answer == "Y" or answer == "":
                        proceed = True

        newhost = {}
        newhost["id"] = nickname
        newhost["hostname"] = hostname
        newhost["user"] = username
        newhost["sudouser"] = sudousername
        newhost["group"] = group
        newhost["identityfile"] = keyfile

        Debug(json.dumps(newhost, sort_keys=True, indent=4, separators=(',', ': ')))

        data["hosts"].insert(hostcount, newhost)
        open(config, "w").write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

        print "Config File Written Successfully"
        return

def removeHost():
        print "Which host do you wish to remove? (number)"
        listHosts()
        answer = raw_input()
        obj  = json.load(open(config))
        try:
                obj['hosts'].pop(int(answer))
                open(config, "w").write(json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': ')))
        except:
                print "Error: Unable to remove host."
        else:
                print "Host removed successfully."
        return

def promptInput(message):
        print message; input = raw_input(); return input

def initialize():
        loadConfig(); getOS(); return

def Debug(message):
        if debug is True:
                print bcolors.OKGREEN + bcolors.BOLD + "DEBUG: " + bcolors.ENDC + str(message)
        return

# Initialize Script
Debug("Debug Enabled")
initialize()

# If list argument is provided, List and exit.
if listarg is True:
        Debug("Listing Hosts")
        listHosts()
        exit() # End script

if addaction is True:
        Debug("Adding Host")
        addHost()
        exit() # End script

if remaction is True:
        Debug("Removing Host")
        removeHost()
        exit() # End Script

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
                        print formatOutput(runCommand(user, host, command))
        else:
                Debug("Individual host")
                for x in range(hostcount):
                        foundhost = data["hosts"][x]["id"]
                        Debug("Curr Host: "+foundhost)
                        if foundhost == host:
                                Debug("Match Found")
                                if sudo is True:
                                        user = data["hosts"][x]["sudouser"]
                                else:
                                        user = data["hosts"][x]["user"]
                                break
                print bcolors.FAIL + host + bcolors.ENDC
                print formatOutput(runCommand(user, host, command))
        exit() # End Script

# If nothing is provided, provide user with usage.
else:
        getUsage(); exit()
