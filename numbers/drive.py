import interpret
import pprint
import json
from tools import tool_selector

##argparser = argparse.Arg

with open("main.nums") as srcfile:
  src = srcfile.read()
  
with open("numbers/settings.json") as settingsfile:
  settings = json.load(settingsfile)

a = interpret.Interpreter(src, settings)
#pprint.pprint(a.program.code, sort_dicts=False, underscore_numbers = True)
a.interpret()
#print("\n\n\n\n")
