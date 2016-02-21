#!/usr/bin/env python
# stooge.py - "one who plays a subordinate or compliant role to a principal"
# Ron Egli
Version="0.8.3"
# github.com/smugzombie - stooge.us

# Python Imports
import json;     import subprocess;   import pprint;
import argparse; import commands;     import os;
import re;       import textwrap;     import atexit;

# import sys;

# Defaults
# scriptname = str(os.path.basename(__file__))
# scriptname = str(sys.argv[0])
currentDir = str(os.path.dirname(os.path.realpath(__file__)))
config = currentDir+"/stooge.json"
blankConfig = "{\"config\":{\"masteridentityfile\" : \"\", \"lockconfig\" : \"false\", \"configversion\" : \"0.4\", \"checkforupdates\" : \"true\"},\"hosts\":[]}"

# Arguments
arguments = argparse.ArgumentParser()
arguments.add_argument('--list','-l', help="List current devices in the config", required=False, action='store_true')
arguments.add_argument('--host','-H', help="Select a specific host from the config:           -H '*' (all)  or -H 'server1'", required=False, default="")
arguments.add_argument('--group','-g', help="Select a specific group of hosts from the config", required=False, default="")
arguments.add_argument('--command','-c', help="The command you want to push to selected hosts", required=False, default="")
arguments.add_argument('--sudo','-s', help="If the command is to be run via SUDO", required=False, action='store_true')
arguments.add_argument('--verbose','-v', help="Enables verbose output from host", required=False, action='store_true')
arguments.add_argument('--add', help="Allows the user to add a new host", required=False, action='store_true')
arguments.add_argument('--remove', help="Allows the user to remove a previous host", required=False, action='store_true')
arguments.add_argument('--debug', help="Enables Debugging", required=False, action='store_true')
arguments.add_argument('--update', help="Checks for latest updates in Git", required=False, action='store_true')
args = arguments.parse_args()
list = args.list
host = args.host.replace(' ', '').lower()
group = args.group.lower()
command = args.command
# Additional Options
sudo = args.sudo; verbose = args.verbose;
# Add / Remove Hosts
addAction = args.add; remAction = args.remove;
# Debugging
debug = args.debug
# Updates
update = args.update

# Styles
class bcolors:
        HEADER = '\033[95m';  OKBLUE = '\033[94m';   OKGREEN = '\033[92m';
        WARNING = '\033[93m'; FAIL = '\033[91m';     ENDC = '\033[0m';
        BOLD = '\033[1m';     UNDERLINE = '\033[4m';

# Functions

def createBlankConfig():
        try: file = open(config, "w"); file.write(blankConfig)
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
def runCommand(host, command):
        identityfile = ""; user = "";
        for x in xrange(hostcount):
                hostname = data['hosts'][x]['id']
                if host == hostname:
                        identityfile = data['hosts'][x]['identityfile'];
                        host = data['hosts'][x]['hostname'];
                        if sudo is True:
                                user = data["hosts"][x]["sudouser"]
                        else:
                                user = data["hosts"][x]["user"]
                                break
                        break;
        if identityfile != "": identity = "-i "+ str(identityfile) +" "
        else: identity = ""
        output = commands.getstatusoutput('ssh '+identity+user+'@'+host+" "+command)
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
        printError("Invalid arguments provided. Please re-run the script with '-h' for more information on proper usage. ")
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
                                        #hostname = str(data["hosts"][x]['id'])
                                        #hosts[hostname]['identityfile'] = data["hosts"][x]['identityfile']
                                        #hosts.insert(hostname, newhost)
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

def printError(message):
        print bcolors.FAIL + "Error: " + bcolors.ENDC + message

def initialize():
        loadConfig(); getOS(); return

def Debug(message):
        if debug is True: print bcolors.OKGREEN + bcolors.BOLD + "DEBUG: " + bcolors.ENDC + str(message)
        return
def processGroup(group):
        if command == "": printError("No command provided!"); exit();
        matches = 0;
        if hostcount > 0:
                for x in xrange(hostcount):
                        isgroup =  data["hosts"][x]["group"]
                        host = data["hosts"][x]["hostname"]
                        nickname = data["hosts"][x]["id"]
                        if isgroup == group:
                                matches += 1
                                print bcolors.FAIL + nickname + bcolors.ENDC
                                print formatOutput(runCommand(host, command))

        else: print "No current Stooge Hosts."

        if matches <= 0:
                printError("No hosts found for group: "+ group)
        else:
                print str(matches)+" hosts found for group: "+ group
        return

def findHost(host):
        Debug("Looking for hosts starting with: "+host)
        matches = 0;
        search = host.replace('*', '')
        if hostcount > 0:
                for x in xrange(hostcount):
                        ismatch = data["hosts"][x]["id"]
                        host = data["hosts"][x]["hostname"]
                        nickname = data["hosts"][x]["id"]
                        if ismatch.startswith(search) is True:
                                matches += 1
                                print bcolors.FAIL + nickname + bcolors.ENDC
                                print formatOutput(runCommand(host, command))

        else: print "No current Stooge Hosts."

        if matches <= 0:
                printError("No hosts found matching: "+search)
        else:
                print str(matches)+" hosts matching: "+ search
        return
def validateCommand():
        if verbose is True: print "Command: ",command
        if command == "": printError("No command provided!"); exit()
        return

def processAll():
        Debug("Processing all hosts")
        for x in xrange(hostcount):
                host = data["hosts"][x]["id"]
                print bcolors.FAIL + host + bcolors.ENDC
                print formatOutput(runCommand(host, command))
        return

def processHost():
        Debug("Individual host")
        for x in range(hostcount):
                foundhost = data["hosts"][x]["id"]
                Debug("Curr Host: "+foundhost)
                if foundhost == host:
                        Debug("Match Found")
                        print bcolors.FAIL + host + bcolors.ENDC
                        print formatOutput(runCommand(host, command))
        return

def checkForUpdate():
        Debug("Checking for updates")
        import urllib2; import ssl; from distutils.version import LooseVersion
        rawfileurl = "https://raw.githubusercontent.com/SmugZombie/Stooge/master/stooge.py"
        Debug("Url: "+rawfileurl)
#       regex = re.compile(ur'(?P<title>Version=.)(?P<version>.{1,3}..{1,3}..{1,3})(.\n)')
        regex = re.compile(ur'(\d+\.\d+\.\d+)')
        req = urllib2.Request(rawfileurl)

        # SSL
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        output = {}; output['url'] = rawfileurl;

        try:
                response = urllib2.urlopen(req, context=ctx)
        except urllib2.HTTPError, err:
                Debug("HTTP Error: "+ err.code)
                output['code'] = err.code; response = ""
        else:
                Debug("HTTP Success:")
                output['code'] = response.getcode(); response = response.read()
#               Debug("Response: "+ str(response))

        if response != "":
                try:
                        newVersion = re.search(regex, response).group(1)
                except:
                        newVersion = "Unknown"
                        update = False
#               except Exception,e: print str(e)
                else:
                        if LooseVersion(newVersion) > LooseVersion(Version):
                                update = True
                        else:
                                update = False
        else:
                update = False
        print "Current Version : " + Version
        print "Latest Version  : " + newVersion
        print "Update Available: " + str(update)
        exit()

# Initialize Script
Debug("Debug Enabled")
initialize()

# If list argument is provided, List and exit.
if list is True:
        Debug("Listing Hosts")
        listHosts()
        exit() # End script

if update is True:
        Debug("Checking for Updates")
        checkForUpdate()
        exit()

if addAction is True:
        Debug("Adding Host")
        addHost()
        exit() # End script

if remAction is True:
        Debug("Removing Host")
        removeHost()
        exit() # End Script

# If both host and group are defined, error and exit
if host != "" and group != "":
        printError("Both host and group cannot be specified!")
        exit() # End Script

# If group, process group
if group != "":
        processGroup(group)
        exit() # End Script

# If wildcard host, process hosts
if "*" in host and host != "*":
        findHost(host)
        exit() # End Script

if host == "":
        printError("Invalid host provided. See -h for assistance.")
elif host == "all" or host == "*":
        validateCommand()
        processAll()
        exit()
else:
        validateCommand()
        processHost()
        exit

