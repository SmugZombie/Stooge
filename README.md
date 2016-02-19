# Stooge
Handspun Salt / Puppet like tool

<strong>Stooge</strong> - "One who plays a subordinate or compliant role to a principal"

<strong>Usage:</strong>

<pre>stooge -H [HOSTNAME/IP]... -c [COMMAND]... -s
Run commands easily via ssh on remote devices

  -H, --host            the targeted host for the remote command
  -g, --group           targets a specific group of predefined hosts
  -c, --command         the command to be run on the remote host(s)
  -s. --sudo            if enabled, will use sudouser in place of standard
  -v, --verbose         enabled verbose output of commands that are run
  --add                 adds a new host to the stooge configuration
  --remove              removes a selected host from the stooge configuration

Examples:
  stooge -h server1 -c "shutdown -r now" -s
      - Tells the host server1 to shutdown/reboot now using a sudo user
  stooge -H "tes*" -c "who"
      - Tells all hosts that start with "tes" to return 'who' is logged in
                using a standard user
  stooge -H "*" -c "who"
      - Tells all available hosts to return 'who' is logged in, using a
                standard user</pre>
  
<strong>Installation</strong>:
<pre>wget http://source.stooge.us -O stooge; chmod +x stooge; ./stooge</pre>

FAQ:<br><br>
<strong>Why build this if there are other options already made and tested?</strong><br> - To assist in learning a new programming / scripting language I task myself with a project that will encourage me to grow and expand my knowledge of the capabilities and features of a the language without following boring step by step guides.<br> - Because its fun.
