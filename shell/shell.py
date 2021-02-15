#! /usr/bin/env python3

import os, sys, time, re
from myReadlines import myReadlines

while(True):
    os.write(1,"my_shell:$ ".encode()) # Print shell prompt
    args = myReadlines().split()       # Tokenize input

    if args == []:                     # continue if no input
        continue

    elif args[0] == "exit":            # exit if exit is input
        sys.exit(0)

    rc = os.fork()

    if rc < 0:                                        # forking failed
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)                                   # error

    elif rc == 0:                                     # child
        for dir in re.split(":", os.environ['PATH']): # try directorys in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)  # try to exec program
            except FileNotFoundError:                 # ...expected
                pass                                  # ...fail quietly

        os.write(1, ("\"%s\" is not an available command in your system.\n" % args[0]).encode())
        sys.exit(1)                                   # error

    else:                                             # Parent forked
        childPidCode = os.wait()
