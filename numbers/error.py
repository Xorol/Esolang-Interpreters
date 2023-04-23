import re

def errorprint(msg):
  print("\033[1;31m" + msg + "\033[0;m")

class NumbersError:
  def __init__(self, program, pointer, _type, details):
    #start = max(pointer-5, 0)
    #surroundings = program.get_raw(start,min(pointer+5, len(program)))
    #context = ("..." if max(pointer-5,0) == pointer - 5 else "") + surroundings + ("..." if min(pointer+5,len(program)) == pointer + 5 else "")
    command = program[pointer]["command"]
    self.msg = f"{_type}, line {program.lineno}: {command}\n{program[pointer]['repr']}\n{details}"
    
  def throw(self):
    errorprint(self.msg)
    quit(1)

class ErrorHandler:

  @classmethod
  def UnknownCommandError(cls, program, pointer, interpreter):
    ocommand = program[pointer]['command']
    errmsg = f"Unknown command: {ocommand}"
    if ";" in ocommand:
      errmsg += " Did you forget to put a space before the comment?"
    elif ocommand == "reference":
      errmsg = f"Stack reference (${program[pointer]['args'][0]}) in bad context: they cannot be used as commands"
    elif re.match(r"[^$;0-9.*]", ocommand):
      errmsg += " Remember that commands cannot contain invalid characters"
    return NumbersError(program, pointer, "UnknownCommandError", errmsg)

  @classmethod
  def ModuleDoesntExistError(cls, program, pointer, module_name):
    errmsg = f"Module {module_name}.nmod doesn't exist!"
    return NumbersError(program, pointer, "ModuleDoesntExistError", errmsg)

  @classmethod
  def InfiniteLoopError(cls, program, pointer):
      errmsg = "Infinite loop detected: the program has surpassed 50,000 commands. If there was no infinite loop, set the `infinite-loop-checker` setting to false in `settings.json`"
      return NumbersError(program, pointer, "InfiniteLoopError", errmsg)
  @classmethod
  def StackError(cls, program, pointer, expected):
    if isinstance(expected, dict):
      errmsg = f"Stack reference index is larger than the length of the current stack ({'control' if program.state.selected else 'main'} stack): attempting to index {expected['args'][0]} out of {len(program.state.stack)}"
    else:
      errmsg = f"Command {program[pointer]['command']} expected {expected} items but got {len(program.state.stack)} items from the currently selected stack ({'control' if program.state.selected else 'main'} stack)"
    return NumbersError(program, pointer, "StackError", errmsg)

  @classmethod
  def MappingIncompatibleError(cls, program, pointer):
    pointer -= 1
    program[pointer]["repr"] += " " + program[pointer+1]["repr"]
    errmsg = f"Command {program[pointer]['args'][0]} is incompatible with mapping."
    return NumbersError(program, pointer, "MappingIncompatibleError", errmsg)

  @classmethod
  def NamespaceError(cls, program, pointer):
    errmsg = ""
    if hasattr(program.state.loaded[program[pointer]["command"]], "children"):
      errmsg = f"Cannot run {program[pointer]['command']} as it is a namespace."
    return NumbersError(program, pointer, "NamespaceError", errmsg)

  @classmethod
  def ModuleError(cls, program, pointer, msg):
    return NumbersError(program, pointer, "ModuleError", msg)