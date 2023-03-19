commands = ["A1", "B2", "C3", "D4", "E5", "F6", "G7", "H8"]
command_map = dict((number, letter) for letter, number in commands)
ignore_chars = [" "]

# Parses the command from back-to-front, ignoring any possible garbage before the list of commands
def parse_aprs_commands(info):
    char_iter = iter(reversed(info))
    commands = []
    try:
        while True:
            c2 = next(char_iter)
            if c2 in command_map:
                c1 = next(char_iter)
                if command_map[c2] == c1:
                    commands.append(c1 + c2)
                else:
                    print(f"Found invalid char pair {repr((c1,c2))}, ending parse")
                    raise StopIteration()
            elif c2 in ignore_chars:
                continue
            else:
                print(f"Found garbage char {repr(c2)}, ending parse")
                raise StopIteration()
    except StopIteration:
        pass

    commands.reverse()
    return commands


