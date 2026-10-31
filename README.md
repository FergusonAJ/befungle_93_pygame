# Python3 Befungle93 Interpreter + Pygame Visualizer

Just a simple interpreter for the 2D esoteric programming language [Befungle93](https://esolangs.org/wiki/Befunge). 

This implementation breaks from the standard 80x25 grid and uses an infinite grid. 
When loading files, the top-left character will be the origin (0,0). 

The two pieces (interpreter and visualizer) are separate. 
To interpret a Befungle file, run this command replacing `FILE` with your filename: 
```
python3 befungle93_interpreter.py FILE
```

To run the pygame-based visualizer, run this instead: 
```
python3 befungle93_pygame_visualizer.py FILE
```

Controls for the visualizer:
- WASD/arrow keys to pan
  - Hold shift (left or right) to pan at 5x speed
- \+ and - (top row) to change zoom
- \[ and \] to change tick speed
- Space to advance one step
- p to pause/unpause
- f to toggle following the program counter
- Escape or q to quit

Files in the `examples/esolang_examples` were copied from the [Befungle93 esolang wiki page](https://esolangs.org/wiki/Befunge).
Other files in `examples` were made by hand. 
