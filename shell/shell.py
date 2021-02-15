import os, sys, re

def startShell():
    os.environ['PS1'] = '$$'         #promt variable
    print(os.environ['PS1'],end='')  
    userInput = input()              
    args = userInput.split(" ")
    if userInput == "exit":          #exits shell
        sys.exit(1)
    rc = os.fork()
    if rc < 0:                       #fork call fails
        os.write(2, ("fork failed, returning %d\n" %rc).encode())
        sys.exit(1)
    elif rc == 0:
        for dir in re.split(":", os.environ['PATH']): 
            program = "%s/%s" % (dir, args[0])       #concats users directory command
            #program is directory and command, args is user input, os.environ is child inherance
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass
        os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        sys.exit(1)
    else:
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" %
        childPidCode).encode())
        startShell()
startShell()
