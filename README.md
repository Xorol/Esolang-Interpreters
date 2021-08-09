# Esolang-Interpreters
Interpreters/compilers that I've made for [esolangs](https://esolangs.org/ "Esolangs wiki homepage")

## [Semicolon Hash](https://esolangs.org/wiki/SemicolonHash "Semicolon Hash on the esolangs wiki")
### The language itself
Semicolon Hash is based on a control accumulator, which both commands uses to preform their respoective actions
Command | Action
---|---
|# | Modulos the control variable by 127, takes the result as an ASCII value, prints the character corresponding to it, and resets the control accumulator to 0|
|; | Increments the control accumulator|
### The interpreter
The interpreter just takes input from the user infinitely, and executes it as Semicolon Hash code.
