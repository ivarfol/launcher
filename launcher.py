#!/mnt/e/anaconda3/bin/python3

import termios, fcntl, sys, os, time, subprocess, pickle

def key_detect():
    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    try:
        while True:
            time.sleep(0.05)
            try:
                c = sys.stdin.read(1)
                if c:
                    return c
            except IOError: pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

def outp_table(new, shortcuts, pointer, old_pointer):
    print(f"\033[{len(shortcuts) + 1}F\033[0Jprogram name")
    if new:
        for i in range(len(shortcuts)):
            if i == pointer:
                print("\033[5;7m", shortcuts[i][0], "\033[25;27m")
            else:
                print(shortcuts[i][0])
    else:
        pass # go to lines an redraw them
    return()

def mov_pointer(pointer, limit, move):
    if pointer + move > limit:
        pointer = 0
    elif pointer + move < 0:
        pointer = limit
    else:
        pointer += move
    return(pointer)

def helpf(limit):
    print(f"\033[H\033[0JHelp menu\nq to exit")
    print("w or k to go up, s or j to go down")
    print("r to remove a shortcut, n to make a new one")
    print("h or ? to access this menu")
    print("enter to run the commands associated with the name")
    while True:
        if key_detect() == "q":
            break

def new_shortcut(shortcuts):
    return(shortcuts + [[input("input the name:\n"), [input("what to run:\n"), input("where to run:\n")]]])

def remove_shortcut(shortcuts, pointer):
    shortcuts.pop(pointer)
    return(shortcuts)

def main():
    shortcuts = [["name", ["echo 'what did you expect'", "/"]]]
    if os.path.exists(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".shortcuts.pb")):
        with open(".shortcuts.pb", "rb") as file:
            shortcuts = pickle.load(file)
    else:
        print("No .shortcuts.pb file found, a new one has been created")
        with open(".shortcuts.pb", "wb") as file:
            pickle.dump(shortcuts, file)
    limit = len(shortcuts) - 1
    pointer = 0
    print("\033[2J\033[H")
    for _ in range(len(shortcuts)):
        print()
    outp_table(True, shortcuts, 0, 0)
    while True:
        inp = key_detect()
        if inp == "q":
            print("\033[H\033[0J", end="")
            break # quit
        elif inp == "w" or inp == "k":
            pointer = mov_pointer(pointer, limit, -1)
            outp_table(True, shortcuts, pointer, 0)
        elif inp == "s" or inp == "j":
            pointer = mov_pointer(pointer, limit, 1)
            outp_table(True, shortcuts, pointer, 0)
        elif inp == "n":
            shortcuts = new_shortcut(shortcuts)# new shortcut
            limit += 1
            with open(".shortcuts.pb", "wb") as file:
                pickle.dump(shortcuts, file)
            print("\033[H\033[0J", end="")
            outp_table(True, shortcuts, pointer, 0)
        elif inp == "r":
            shortcuts = remove_shortcut(shortcuts, pointer) # remove
            limit -= 1
            with open(".shortcuts.pb", "wb") as file:
                pickle.dump(shortcuts, file)
            print("\033[H\033[0J", end="")
            outp_table(True, shortcuts, pointer, 0)
        elif inp == "h" or inp == "?":
            helpf(limit) # help
            print("\033[H\033[0J", end="")
            outp_table(True, shortcuts, pointer, 0)
        elif ord(inp) == 10:
            subprocess.Popen(shortcuts[pointer][1][0], shell=True, cwd=shortcuts[pointer][1][1])# enter
            break

if __name__ =="__main__":
    main()
