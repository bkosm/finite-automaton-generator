# Finite Automata Generator
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
# Converter
Command line tool for translating simple automatas from XML files into GraphViz and vice versa.
```
usage: converter.py [-h] [-ox xxx.(xml|jff)] [-og xxx.gv] input_file.ext

Convert xml described automatas to graphviz and vice versa

positional arguments:
  input_file.ext     Input filename

optional arguments:
  -h, --help         show this help message and exit
  -ox xxx.(xml|jff)  Output xml filename
  -og xxx.gv         Output graphviz filename
```
### Converter note
- GraphViz files are required to have each edge labeled with an accepted word.
- GraphViz graph's initial node is distinguished by being pointed at by a dot labeled "q".

Example convertable file below:
```ex.gv
digraph ex {
q -> q0                   // initial node
q0 -> q1 [label= "abc"];  // labeled edge
q [shape=point]           // initial node pointer
q1 [shape=doublecircle]   // final node indicator
}
```


> Bartosz Kosmala 2019
