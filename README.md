# RELAY SWITCHER UI
Simple UI that allows you to control RelaySwitcher device.

- turn on/off power sockets with buttons in ui or f1, f2, f3, f4
- write and execute programs of automated control

*MANUAL SWITCHING*

Manual switching allows you to toggle on/off power sockets, or single port of socket. 
Press button "I", to enable socket 1 or press "L" under "I" to enable only L port of the first socket. Enabled ports and sockets will appear green, disabled grey.


*PROGRAM SWITCHING*

Program switching allows you to write program and execute it. 
Syntax:
"1234" - to enable all the sockets. "14" will enable 1 and 4 socket.
You can add "s" prefix to command to enable single relays. Command "s12" is equivalent to command "1".

REP N
...
ENDR
This block will start "for" cycle for N iterations. All commands between REP and ENDR will be executed N times.

DELAYS N
DELAYM N
DELAYH N
Each of this commands will pause execution for N seconds, minutes, hours.
