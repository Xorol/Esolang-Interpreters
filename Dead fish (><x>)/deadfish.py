control = 0 #initialize the accumulator

#open the source file, get the relevent chars, and store in comm
d = open('main.deadf','r')
#Main loop
for i in [i for i in d.read() if i in ['s','o','i','d'] else '']:
  if i == 's': stack[cell] *= stack[cell]
  elif i == 'd': stack[cell] -= 1
  elif i == 'i': stack[cell] += 1
  elif i == 'o': print(stack[cell])
  if control == 256 or control == -1: control = 0
d.close()
