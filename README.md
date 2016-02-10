# Stooge.py
Handspun Salt / Puppet like tool

<strong>Stooge</strong> - "One who plays a subordinate or compliant role to a principal"

<strong>Usage</strong>

<pre>stooge -H [HOSTNAME/IP]... -c [COMMAND]... -s
Run commands easily via ssh on remote devices

  -H, --host            the targeted host for the remote command
  -c, --command         the command to be run on the remote host(s)
  -s. --sudo            if enabled, will use sudouser in place of standard
  -v, --verbose         enabled verbose output of commands that are run

Examples:
  stooge -h server1 -c "shutdown -r now" -s
      - Tells the host server1 to shutdown/reboot now using a sudo user
  stooge -c "who"
      - Tells all available hosts to return 'who' is logged in, using a
                standard user

Coming Soon:
  -g, --group           targets a specific group of predefined hosts
  -a, --add             adds a new host to the stooge configuration</pre>
