**Finite Automata Generator**

Command line tool for generating JFLAP  '.jff' files containing random FA's.

```
usage: fa_generator.py [-h] [-n N] [-fs N] [-a [A [A ...]]] [-fn xxx.jff]
                       [--interesting]

Generate a finite automata

optional arguments:
  -h, --help      show this help message and exit
  -n N            Number of states
  -fs N           Number of final states
  -a [A [A ...]]  List of possible words to consume on hops
  -fn xxx.jff     Output XML filename
  --interesting   Generate an example with a more interesting accepted word
```

> Bartosz Kosmala 2019
