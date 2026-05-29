
def lex(file) -> list:
    tokens = []
    for  line in file:
        line = line.strip()
        if len(line) == 0:
            continue
        if line[0] == '[':
            tokens.append(block(line))
        elif line[0].isalpha():
            tokens.append(pair(line))
        elif line[0:1] == "\\":
            pass
        else :
            continue
    return tokens 

def block(line) -> tuple:
    if line[1] != ']':
        name = line[1: -1]
        return ("OPENER", name)
    else:
        return ("CLOSER", None)
def pair(line) -> tuple:
    key, value = line.split('=', 1)
    key = key.strip()
    value = value.strip()
    return ("PAIR", key, value)
