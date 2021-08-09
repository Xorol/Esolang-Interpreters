#Control accumulator
control = 0
#Main loop
while True:
  code = input('>> ')
  for i in code:
    if i not in [';','#']: continue
    control = control + 1 if i == ';' else chr(control % 127)
    if i == '#':
      print(control)
      control = 0
