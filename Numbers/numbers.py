def clear ():
  print(chr(27)+'[2j')
  print('\033c')
  print('\x1bc')

file = input('Enter the file you would like to run (extension is auto-attached): ')
clear()
with open(file+'.numbers') as prog:
  program = []
  for x in prog.read().split(' '): program.append(int(x) if x != '~' else '~')
  program.append('~')

pointer = 0
stack = []
control = 0

try:
  while True:
      com = program[pointer]
      #input(f'CMD: {com} at {pointer}. Stack: {stack} {control}') #debug
      if com == 34: #in:int
        stack.append(int(input('Enter a number: ')))
      elif com == 24:
        control = stack.pop()
      elif com == 40:
        if control == 0:
          pointer += 1
          if program[pointer] in [42,20]:
            pointer += 1
      elif com == 41:
        if control != 0:
          pointer += 1
          if program[pointer] in [42,20]:
            pointer += 1
      elif com == 30:print(stack[-1])
      elif com == 42:pointer = program[pointer + 1] - 2
      elif com == 25:stack.append(control)
      elif com == 26:stack.append(stack[-1])
      elif com == 43:pointer = 0
      elif com == 31:print(chr(stack[-1]))
      elif com == 32:
        for x in stack: print(x, end=" ")
      elif com == 33:
        for x in stack: print(chr(x),end='')
      elif com == 35:
        stack.append(ord(input('Enter a character: ')))
      elif com == 36:
        for x in input('Enter a string: '): stack.append(ord(x))
      elif com == 20:
        pointer += 1
        stack.append(program[pointer])
      elif com == 21: stack.reverse()
      elif com == 22:
        j = stack[-1]
        stack[-1] = stack[-2]
        stack[-2] = j
      elif com == 23: stack.pop()
      elif com == 10: stack.append(stack.pop()+stack.pop())
      elif com == 11: stack.append(stack.pop()-stack.pop())
      elif com == 12: stack.append(stack.pop()*stack.pop())
      elif com == 13: stack.append(stack.pop()/stack.pop())
      elif com == 14: stack.append(stack.pop()//stack.pop())
      elif com == 15: stack.append(stack.pop()%stack.pop())
      elif com == 16: stack[-1] += 1
      elif com == 17: stack[-1] -= 1
      elif com == 18: stack.append(1+(stack.pop()-1)%9)
      elif com == 19:
        from math import factorial
        stack.append(factorial(stack.pop()))
      elif com == 27: stack = []
      elif com == '~': quit()
      pointer += 1
except Exception:
  print(f'problem at {pointer}')
  quit()
