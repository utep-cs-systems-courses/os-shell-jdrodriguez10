#! /usr/bin/env python3

import os, sys, time, re
from myReadlines import myReadlines
global loops
loops = 0


def redirect(args):
    if '|' in args:      #Remove piping symbol
        args.remove('|')
    if '>' in args:
        os.close(1)       #Close fd 1 - to redirect child's stdout to file
        os.open(args[args.index('>')+1], os.O_WRONLY | os.O_CREAT) # Open file to write to
        os.set_inheritable(1, True)           # makes fd 1 accessable
        args.remove(args[args.index('>')+1])
        command = args[args.index('>') -1]
        args.remove('>')
        args.remove(args[0])
    else:
        os.close(0)         #Close keyboard input-- fd 0
        os.open(args[args.index('<') + 1], os.O_RDONLY) # Open file that we want to read from
        os.set_inheritable(1, True)
        args.remove(args[args.index('<')+1])
        command = args[args.index('<') -1]
        args.remove('<')
        args.remove(args[0])
    for dir in re.split(":", os.environ['PATH']):
        program = "%s/%s" % (dir, command)
        if not args:             #If args is empty add the command/file back into the list
            args += command
        try:
            os.execve(program, args, os.environ)
        except FileNotFoundError:
            pass
    os.write(2, ("Command failed\n").encode())
    sys.exit(1)


def pipe(args):
    pid = os.getpid()
    import fileinput
    pr,pw = os.pipe()
    for f in (pr, pw):
        os.set_inheritable(f, True)
    print("pipe fds: pr=%d, pw=%d" % (pr, pw))
    print("About to fork (pid=%d)" % pid)
    rc = os.fork()
    if rc < 0:
        print("fork failed, returning %d\n" % rc, file=sys.stderr)
        sys.exit(1)
    elif rc == 0:                   #  child - will write to pipe
        print("Child: My pid==%d.  Parent's pid=%d" % (os.getpid(), pid), file=sys.stderr)
        os.close(1)                 # redirect child's stdout
        os.dup(pw)
        for fd in (pr, pw):
            os.close(fd)
        print("hello from child")
    else:                           # parent (forked ok)
        print("Parent: My pid==%d.  Child's pid=%d" % (os.getpid(), rc), file=sys.stderr)
        os.close(0)
        os.dup(pr)
        for fd in (pw, pr):
            os.close(fd)
        for line in fileinput.input():
            print("From child: <%s>" % line)
    print("Args before redirect: %s" % args)
    if '<' in args or '>' in args:
        redirect(args)


def command(ibuf):
    if ibuf.lower() == "exit":
        os.write(1, "\nShell exited!\n\n".encode())
        sys.exit(0)
    lines = ibuf.split()  # tokenize user input
    if lines[0] == "pwd":                  #Print working directory
        os.write(1, (os.getcwd()).encode())
    if lines[0] == "cd":
        try:
            for dir in lines[1:]:
                if dir == "..":
                    parent = os.pardir()
                    os.chdir(parent) # Go to parent directory
                if dir == "...":
                    os.chdir('..')        # Go to home Directory
                os.chdir(dir)
        except FileNotFoundError:
            pass                          # Fail quietly
    else:
        rc = os.fork()
        if rc < 0:
            os.write(2, ("Fork failed, returning.. %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:
            if '|' in lines:                    # Doing a pipe
                pipe(lines)
            if '>' in lines or '<' in lines:    # Doing a redirect
                redirect(lines)
            else:
                for dir in re.split(":", os.environ['PATH']):
                    program = "%s/%s" % (dir, lines[0])
                    try:
                        os.execve(program, lines, os.environ) # attempt to execute program
                    except FileNotFoundError:
                        pass
            os.write(2, ("Command failed\n").encode())
            sys.exit(1)
        else:
            childPidCode = os.wait() # parent waits for child

            
def main():
    while(1):
        os.write(1, "$ ".encode())
        ibuf = myReadlines()
        if len(ibuf) > 0:
            interpretCommand(ibuf)         # Determine user inputted command

            
if __name__ == '__main__':
    main()
