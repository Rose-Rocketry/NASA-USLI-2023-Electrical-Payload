def parse_command(commandStr):
    callSign = "XX4XXX"
    callsignIndex = commandStr.find(callSign)
    commandList = commandStr[callsignIndex + callSign.len():].split()
    for command in commandList:
        if command.len() == 2:
            if command[0] == "A":
                if command[1] != "1":
                    return False
            elif command[0] == "B":
                if command[1] != "2":
                    return False
            elif command[0] == "C":
                if command[1] != "3":
                    return False
            elif command[0] == "D":
                if command[1] != "4":
                    return False
            elif command[0] == "E":
                if command[1] != "5":
                    return False
            elif command[0] == "F":
                if command[1] != "6":
                    return False
            elif command[0] == "G":
                if command[1] != "7":
                    return False
            elif command[0] == "H":
                if command[1] != "8":
                    return False
            else:
                return False 
        else:
            return False
    return commandList
            




