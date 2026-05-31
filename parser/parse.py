
class Block:
    name:str 
    attributes: dict
    children: list["Block"]

    def __init__(self, name):
        self.name = name 
        self.attributes = {} 
        self.children = []
        
def parse(tokens) -> "Block":
    root = Block("root")
    stack: list[Block] = []
    stack.append(root)  
   
    for token in tokens:
        if token[0] == "OPENER": 
            branch = Block(token[1])
            parent = stack[-1]
            parent.children.append(branch)
            stack.append(branch)
        elif token[0] == "PAIR":
            stack[-1].attributes[token[1]] = token[2]
        elif token[0] == "CLOSER": 
            stack.pop()
    
    return root 
