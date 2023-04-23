import math
import json
import re
from textwrap import indent
from error import ErrorHandler
from pprint import pprint
from tools import tool_selector
#import os
#from enums import Enum


VERSION = "1.0.0"
UPDATED = "3-31-2023"

executed = 0
compatible_45 = ["16", "17", "18", "19", "20", "24", "30", "31",]

def str_to_float_or_int(string: str) -> float | int:
  if isinstance(string, str):
    return float(string) if "." in string else int(string)
  return string

def match_brackets(string):
    op= [] 
    dc = { 
        op.pop() if op else -1:i for i,c in enumerate(string) if 
        (c=='{' and op.append(i) and False) or (c=='}' and op)
    }
    return False if dc.get(-1) or op else dc

class Stack:

  def __init__(self):
    self.value: list = []

  def __repr__(self) -> str:
    return self.value.__repr__()

  def __iter__(self):
    return iter(self.value)

  def __getitem__(self, idx):
    return self.value[-idx-1]

  def __len__(self):
    return len(self.value)

  def pop(self) -> int:
    return self.value.pop(-1)

  def set_val(self, new_value: list) -> None:
    self.value = new_value

  def push(self, value_to_push: int) -> None:
    self.value.append(value_to_push)

  def swap(self) -> None:
    self.push(self.value.pop(-2))

  def dup(self) -> None:
    self.push(self.value[-1])

  def clear(self) -> None:
    self.set_val([])

  def to_str(self, format: str) -> str | None:
    match format:
      case "str":
        return "".join([chr(i) for i in self])
      case "int":
        return " ".join([str(i) for i in self])
      case _:
        return None
      

  def print_out(self) -> None:
    print(self.to_str("int"))
    self.clear()

class ProgramState:

  def __init__(self, stack: Stack = Stack(), selected: int = 0):
    self.main_stack: Stack = stack
    self.control_stack = Stack()
    self.selected = selected
    self.lineno = 1

  def __repr__(self) -> str:
    return f"<ProgramState control_stack={self.control_stack} stack={self.main_stack}>"

  def pass_on(self):
    return ProgramState(self.main_stack, self.selected)

  def switch(self) -> None:
    self.selected = 0 if self.selected else 1
    return self

  @property
  def unselected_stack(self) -> Stack:
    return self.main_stack if self.selected else self.control_stack
    
  @property
  def stack(self) -> Stack:
    return self.control_stack if self.selected else self.main_stack


class Program:

  def __init__(self, code: str, state: ProgramState = ProgramState()):
    self.code = code
    self.raw = code
    self.formatted = False
    self.state = state
    self.metacomments = []

  def __getitem__(self, idx):
    return self.code[idx]

  def get_raw(self, idx1, idx2 = ""):
    idx2 = (idx1 + 1) if not idx2 else idx2
    return eval(f"self.raw[{idx1}:{idx2}]")
  def get_commands(self, idx1, idx2 = ""):
    idx2 = (idx1 + 1) if not idx2 else idx2
    return eval(f"self.commands[{idx1}:{idx2}]")

  def __setitem__(self, idx, val):
    self.code[idx] = val

  def __delitem__(self, idx):
    del self.code[idx]

  def __len__(self):
    return len(self.code)

  @property
  def lineno(self):
    return self.state.lineno

  def tokenize(self):
    def find_end(i):
        j = self[i]
        #print(j, self.code)
        if isinstance(j, dict):
          #print(j)
          return "skip 1"
        if j.startswith("$"):
          self[i] = {
            "command": "reference",
            "args": [
              int(j[1:])
            ],
            "repr": j
          }
          return "pass"
        try:
          if self[i+1] == "{":
            matches = match_brackets(" ".join(self[i+1:]))
            contents = " ".join(self[i+2:])[3:matches[0]-5]
            self[i] = {
              "command": "def-namespace",
              "args": [
                j, contents
              ],
              "repr": f"{j}" + " {\n" + f"{indent(contents, chr(9))}" + "\n}"
            }
            matches = match_brackets("".join(self[i+1:]))
            self.code = self.code[:i+1] + [i for i in self.code[i+1:matches[0]+i+3] if i == "\n"] + self.code[matches[0]+i+3:]
            return "pass"
        except IndexError:
          pass
        match j:
          case "20":
            self[i] = {
              "command": j,
              "args": [self[i+1] if "$" not in self[i+1] else {
                "command": "reference",
                "args": [
                  int(self[i+1][1:])
                ]
              }],
              "repr": j + " " + self[i+1]
              #"end": i + 2
            }
            return "skip 2"
          case "40" | "41":
            skip = find_end(i + 1)
            self[i] = {
              "command": j,
              "args": [self[i+1]],
              "repr": j + " " + self[i+1]["repr"]
              #"end": find_end(i + 1)
            }
            return skip
          case "44":
            skip = self[i+1:].index("44") + 2
            self[i] = {
              "command": j,
              "args": [
                # Mapping compatibility
                self[i+1], 
                # The code for the function
                Program(" ".join(self[i+2:i+skip-1])).format().code
              ],
              "repr": j + " " + " ".join(self[i+1:i+skip-1]) + " 44"
              #"end": skip + i 
            }
            return f"skip {skip}"
          case "45":
            skip = self[i+1:].index("45") + 2
            self[i] = {
              "command": j,
              "args": [
                self[i+1:i+skip-1]
              ],
              "repr": j + " " + " ".join(self[i+1:i+skip-1]) + " 45"
              #"end": skip + i 
            }
            return f"skip {skip}"
          case "\n":
            self[i] = {
              "command": "NEWLINE",
              "repr": "\n"
            }
          case _:
            self[i] = {
              "command": j,
              "repr": j
              #"end": i + 1
            }
        return "pass"
    i = 0
    while i != len(self):
      if (skipamt := find_end(i)).startswith("skip"):
        skipamt = int(skipamt[5:])
        i += skipamt
    self.code = [i for i in self.code if isinstance(i, dict)]

  def remove_comments(self):
    code = self.code
    code = re.sub(r" ;.*", "", code)
    code = code.splitlines()
    block_comment = False
    for i, line in enumerate(code):
      block_comment ^= line.startswith(";;")
      if line.startswith(";!"):
        self.metacomments.append(line.replace(";!", "").split())
      if block_comment or line.startswith(";"):
        code[i] = ""
    self.code = code
        
  def format(self):
    if self.formatted:
      return self
    self.formatted ^= True
    #code = sub(r";.*\n", "", code)
    self.remove_comments()
    code = "\n".join(self.code)
    code = code.replace("*", "20 ")
    code = code.replace("\n", " \n ")
    code = code.replace("  ", " ").strip(" ")
    code = code.split(" ")
    self.code = code
    self.commands = code
    self.tokenize()
    self.code.append({
      "command": "~",
      "repr": "~"
    })
    return self

class Function:
  def __init__(self, name: str, mapping_compatible: bool, code: str):
    self.name = name
    self.mapping_compatible = mapping_compatible
    self.code = code
    # name: str
    # mapping_compatible: bool
    # code: str

  def __repr__(self):
    return f"{self.name} : {'1' if self.mapping_compatible else '0'} : {self.code}"

  def run(self, state: ProgramState, settings: dict, it) -> Stack:
    i = it(self.code, settings, state.pass_on())
    i.interpret()
    return i.program.state.main_stack

class Namespace:
  def __init__(self, name: str):
    self.name = name
    self.children = {}

  def __iter__(self):
    return iter(self.children.values())

  def __getitem__(self, idx):
    if "." in idx:
      idx = idx.split(".")
      return self.children[idx[0]][".".join(idx[1:])]
    return self.children[idx]

  def __contains__(self, item) -> bool:
    try:
      self[item]
    except KeyError:
      return False
    return True

  def __repr__(self) -> str:
    out = f"{self.name} : " + "{"
    children = ""
    for i in self:
      children += "\n" + str(i)
    children = indent(children, "\t")
    out += children
    if children:
      out += "\n"
    out += "}"
    return out

  def register(self, item):
    self.children[item.name] = item

  @classmethod
  def from_str(cls, string, name):
    namespace = cls(name)
    matches = match_brackets(string)
    raw_s = string
    string = string.splitlines()
    i = -1
    while True:
      i += 1
      if i >= len(string):
        break
      line = string[i].strip().split(" : ")
      if len(line) == 3:
        namespace.register(Function(line[0], bool(int(line[1])), line[2]))
      elif len(line) == 2:
        line_r = " : ".join(line)
        li = raw_s.index(line_r) + line_r.index("{")
        namespace_conts = raw_s[li:matches[li]+1]
        i = raw_s[:matches[li]+1].count("\n") + 1
        namespace.register(Namespace.from_str(namespace_conts, line[0]))
    return namespace
    
class Interpreter:
  def __init__(self, code: str, settings: dict, state=ProgramState()):
    self.program = Program(code, state).format()
    self.program.state.loaded = Namespace("global")
    self.settings = settings
    if "debug-mode" not in self.settings:
      self.settings["debug-mode"] = ["DEBUG"] in self.program.metacomments
    if "tool-menu" not in self.settings:
      self.settings["tool-menu"] = ["TOOLS"] in self.program.metacomments
    if "infinite-loop-checker" not in self.settings:
      self.settings["infinite-loop-checker"] = ["NOILC"] not in self.program.metacomments
    if "built-in-functions" not in self.settings:
      self.settings["built-in-functions"] = ["NOBUILTINS"] not in self.program.metacomments
  @property
  def stack(self) -> Stack:
    return self.program.state.stack

  @property
  def loaded(self) -> Namespace:
    return self.program.state.loaded

  @property
  def unselected_stack(self) -> Stack:
    return self.program.state.unselected_stack

  def load_module(self, modulename):
    modulename = modulename.replace(".", "/").replace("^","../") + ".nmod"
    with open(modulename, "r") as m:
      modulecontents = m.read()
    modulecontents = Program(modulecontents)
    modulecontents.remove_comments()
    moduleuses = False
    if modulecontents.metacomments:
      moduleuses = modulecontents.metacomments[0][1]
    if moduleuses:
      module = Namespace.from_str(modulecontents.raw, moduleuses)
      self.program.state.loaded.register(module)
    else:
      ErrorHandler.ModuleError(self.program, self.ip-1, "No USE statement found").throw()
      pass

  def parse_stack_reference(self, reference):
    if not isinstance(reference, dict):
      return reference
    try:
      return self.stack[reference["args"][0]]
    except IndexError:
      ErrorHandler.StackError(self.program, self.ip-1, reference)

  def prompt_debug(self):
    command = input(">>>").split()

    if command == ["^"]:
      command = self.last_command
    else:
      self.last_command = command
    
    if not command:
      return

    match command[0]:
      case "view":
        if len(command) < 2:
          print("`view` must be supplied an argument. See README.md for usage")
        elif command[1] == "main":
          pprint(self.program.state.main_stack)
        elif command[1] == "control":
          pprint(self.program.state.main_stack)
        elif command[1] == "selected":
          print(f"Currently selected: {'control' if self.program.state.selected else 'main'} stack")
          pprint(self.stack)
        elif command[1] == "unselected":
          print(f"Currently unselected: {'main' if self.program.state.selected else 'control'} stack")
          pprint(self.unselected_stack)
        elif command[1] == "state":
          print(f"Currently selected: {'control' if self.program.state.selected else 'main'} stack\nLine no.: {self.program.lineno}")
          print(f"\nMain stack ({'unselected' if self.program.state.selected else 'selected'})")
          pprint(self.program.state.main_stack)
          print(f"\nControl stack ({'selected' if self.program.state.selected else 'unselected'})")
          pprint(self.program.state.control_stack)
        elif command[1] == "compiled":
          pprint(self.program.code, sort_dicts = False)
        elif command[1] == "loaded":
          pprint(self.loaded, sort_dicts = False)
        elif command[1] == "settings":
          pprint(self.settings, sort_dicts=False)
        return
      case "step":
        out = "step"
        if len(command) >= 2:
          if "-v" in command:
            out += " verbose"
          if "end" in command:
            out += " to_end"
        return out
      case "q" | "quit" | "exit":
        quit()
      case "help" | "?":
        print("Numbers interactive debugger. Type commands such as `step` or `view` to use. See README.md for documentation")
      case "info":
        print(f"Numbers version {VERSION}, last updated {UPDATED}. Made by hcaelbxorol. Use `changelog` to see a changelog.")
      case "changelog":
        with open("numbers/changelog.txt", "r") as clfile:
          changelog = clfile.read()
        print(changelog)

  def interpret(self):
    global executed, compatible_45
    if self.settings["tool-menu"]:
      tool_selector()
      return
    self.ip = 0
    nextc = None
    vrbo = False
    if self.settings["built-in-functions"]:
      self.load_module("numbers.builtins")
    while True:
      curcom = self.program[self.ip]
      executed += 1
      if executed >= 50_000 and self.settings["infinite-loop-checker"]:
        ErrorHandler.InfiniteLoopError(self.program, self.ip).throw()
      #print(curcom)
      if self.settings["debug-mode"] and curcom["command"] != "NEWLINE":
        action = self.prompt_debug()
        vrbo = False
        if not action:
          continue
        if "verbose" in action:
          vrbo = True
        if "end" in action:
          self.settings["debug-mode"] = False
      if vrbo and curcom["command"] != "NEWLINE":
          print(f"Line {self.program.lineno}: \n\t{curcom['repr']}")
  
      self.ip += 1
      if nextc:
        curcom = nextc
        nextc = None
        self.ip -= 1
      # Note to self: when adding new commands
      # put continue at the end of the case or else
      match curcom["command"]:
        # --- SPECIAL COMMANDS --- #
        case "~":
          return self
        case "NEWLINE":
          self.program.state.lineno += 1
          continue
        case "def-namespace":
          self.loaded.register(Namespace.from_str(curcom["args"][1], curcom["args"][0]))
          continue
        
        # --- ARITHMETIC COMMANDS --- #
        case "10":
          if len(self.stack) < 2:
            ErrorHandler.StackError(self.program, self.ip-1, 2).throw()
          self.stack.push(self.stack.pop() + self.stack.pop())
          continue
        case "11":
          if len(self.stack) < 2:
            ErrorHandler.StackError(self.program, self.ip-1, 2).throw()
          self.stack.push(self.stack.pop() - self.stack.pop())
          continue
        case "12":
          if len(self.stack) < 2:
            ErrorHandler.StackError(self.program, self.ip-1, 2).throw()
          self.stack.push(self.stack.pop() * self.stack.pop())
          continue
        case "13":
          if len(self.stack) < 2:
            ErrorHandler.StackError(self.program, self.ip-1, 2).throw()
          self.stack.push(self.stack.pop() / self.stack.pop())
          continue
        case "14":
          if len(self.stack) < 2:
            ErrorHandler.StackError(self.program, self.ip-1, 2).throw()
          self.stack.push(self.stack.pop() // self.stack.pop())
          continue
        case "15":
          if len(self.stack) < 2:
            ErrorHandler.StackError(self.program, self.ip-1, 2).throw()
          self.stack.push(self.stack.pop() % self.stack.pop())
          continue
        case "16":
          if len(self.stack) < 1:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          self.stack.push(self.stack.pop() + 1)
          continue
        case "17":
          if len(self.stack) < 1:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          self.stack.push(self.stack.pop() - 1)
          continue
        case "18":
          if len(self.stack) < 1:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          self.stack.push(int(self.stack.pop() < 0))
          continue
        case "19":
          if len(self.stack) < 1:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          self.stack.push(math.factorial(self.stack.pop()))
          continue

        # --- STACK COMMANDS --- #
        case "20":
          self.stack.push(str_to_float_or_int(self.parse_stack_reference(curcom["args"][0])))
          continue
        case "21":
          self.program.state.switch()
          continue
        case "22":
          if len(self.stack) < 2:
            ErrorHandler.StackError(self.program, self.ip-1, 2).throw()
          self.stack.swap()
          continue
        case "23":
          if len(self.stack) < 1:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          self.stack.pop()
          continue
        case "25":
          if len(self.unselected_stack) < 1:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          self.stack.push(self.unselected_stack.pop())
          continue
        case "24":
          if len(self.stack) < 1:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          self.unselected_stack.push(self.stack.pop())
          continue
        case "26":
          if len(self.stack) < 1:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          self.stack.dup()
          continue
        case "27":
          self.stack.clear()
          continue
        case "28":
          self.stack.push(len(self.stack))
          continue

        # --- IO COMMANDS --- #
        case "30":
          if len(self.stack) < 1:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          print(self.stack.pop())
          continue
        case "31":
          if len(self.stack) < 1:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          print(chr(self.stack.pop()))
          continue
        case "32":
          if len(self.stack) == 0:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          self.stack.print_out()
          continue
        case "33":
          if len(self.stack) == 1:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          print(self.stack.to_str("str"))
          self.stack.clear()
          continue
        case "34":
          self.stack.push(str_to_float_or_int(input(self.settings["input-prompts"]["integer"])))
          continue
        case "35":
          self.stack.push(ord(input(self.settings["input-prompts"]["character"])))
          continue
        case "36":
          [self.stack.push(ord(i)) for i in input(self.settings["input-prompts"]["string"])]
          continue

        # --- CONTROL FLOW COMMANDS --- #
        case "40" | "41":
          if len(self.program.state.control_stack) == 0:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          if (self.program.state.control_stack.pop() == 0) ^ (self.program[self.ip]["command"] == "41"):
            nextc = curcom["args"][0]
            continue
        case "42":
          self.ip = self.stack.pop()
          continue
        #case "43":
        #  self.ip = 0
        #  continue
        case "44":
          if len(self.stack) == 0:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          self.loaded.register(Function(self.stack.pop(), bool(curcom["args"][0]), curcom["args"][1],))
          continue
        case "45":
          if len(self.stack) == 0:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          tomap = self.stack.pop()
          if tomap not in compatible_45:
            ErrorHandler.MappingIncompatibleError(self.program, self.ip-1).throw()
          if tomap == 20:
            c = "*" + " *".join(curcom["args"][0])
          else:
            c = "20 " + f" {tomap} *".join(curcom["args"][0]) + f" {tomap}"
          self.program.state = Interpreter(
            c, 
            self.settings,
            self.program.state,
          ).interpret().program.state

          continue
        case "46":
          if len(self.stack) == 0:
            ErrorHandler.StackError(self.program, self.ip-1, 1).throw()
          try:
            self.load_module(self.stack.to_str("str"))
          except FileNotFoundError:
            ErrorHandler.ModuleDoesntExistError(self.program, self.ip-1, self.stack.to_str("str")).throw()
          self.stack.clear()
          continue

      if curcom["command"] in self.loaded:
        try:
          self.loaded[curcom["command"]].run(
            self.program.state, 
            self.settings, 
            Interpreter
          )
          continue
        except AttributeError:
          ErrorHandler.NamespaceError(self.program, self.ip-1).throw()
          continue
      ErrorHandler.UnknownCommandError(self.program, self.ip-1, self).throw()
    return self