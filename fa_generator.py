from random import randint
import argparse


class State:
    MIN_X: float = 50.0
    MIN_Y: float = 30.0

    def __init__(self, id_str: str, name: str, initial: bool = False, final: bool = False):
        self.id = id_str
        self.name = name

        self.is_initial = initial
        self.is_final = final

        self.x_coord = ''
        self.y_coord = ''

    def as_string(self) -> str:
        state_str = '\n\t\t<state id="'+self.id+'" name="'+self.name + \
            '">&#13;\n\t\t\t<x>'+self.x_coord+'</x>&#13;\n\t\t\t<y>'+self.y_coord+'</y>&#13;'

        if self.is_initial:
            state_str += '\n\t\t\t<initial/>&#13;'
        if self.is_final:
            state_str += '\n\t\t\t<final/>&#13;'

        return state_str+'\n\t\t</state>&#13;'


class Transition:
    def __init__(self, from_state: State, to_state: State, accepted_word: str = None):
        self.from_state = from_state
        self.to_state = to_state
        self.accepted_word = accepted_word

        self.base_pre = '\n\t\t<transition>&#13;'
        self.base_post = '\n\t\t</transition>&#13;'

    def as_string(self) -> str:
        trans_str = '\n\t\t\t<from>'+self.from_state.id + \
            '</from>&#13;\n\t\t\t<to>'+self.to_state.id+'</to>&#13;'

        if self.accepted_word:
            trans_str += '\n\t\t\t<read>'+self.accepted_word+'</read>&#13;'
        else:
            trans_str += '\n\t\t\t<read/>&#13;'

        return self.base_pre+trans_str+self.base_post


class XML_Generator:
    def __init__(self, n: int, fs: int, alphabet: list):
        if fs > n or n <= 0:
            raise Exception("Invalid arguments")

        self.number_of_states = n
        self.number_of_final_states = fs
        self.number_of_transitions = randint(0, 2*self.number_of_states)
        self.alphabet = alphabet

        self.xml_pre = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><!--Created with JFLAP 7.1.--><structure>&#13;\n\t<type>fa</type>&#13;\n\t<automaton>&#13;'
        self.states_stamp = '\n\t\t<!--The list of states.-->&#13;'
        self.transitions_stamp = '\n\t\t<!--The list of transitions.-->&#13;'
        self.xml_post = '\n\t</automaton>&#13;\n</structure>'

        self.states = []
        self.transitions = []

        self.gen_fa()

    def gen_fa(self) -> None:
        number_of_final_states = self.number_of_final_states

        # Generowanie stanów
        for i in range(self.number_of_states):
            s_id = str(i)
            s_name = 'q'+s_id

            self.states.append(State(s_id, s_name))

        self.states[0].is_initial = True

        # Wypełnianie ostatecznych wierzcholkow
        while not number_of_final_states == 0:
            current_state = self.random_state()

            if current_state.is_final:
                break
            else:
                current_state.is_final = True
                number_of_final_states -= 1

        # Generowanie przejść
        if self.alphabet:
            for i in range(self.number_of_transitions):
                if randint(1, 5) == 1:
                    self.transitions.append(Transition(self.random_state(),
                                                       self.random_state()))
                else:
                    self.transitions.append(Transition(self.random_state(),
                                                       self.random_state(),
                                                       self.random_word()))
        else:
            for i in range(self.number_of_transitions):
                self.transitions.append(Transition(self.random_state(),
                                                   self.random_state()))

    def random_state(self) -> State:
        return self.states[randint(0, len(self.states)-1)]

    def random_word(self) -> str:
        return self.alphabet[randint(0, len(self.alphabet)-1)]

    def gen_jff_file(self, filename: str) -> None:
        self.set_state_coords()

        with open(file=filename, mode="w", encoding="utf8") as f:
            f.write(self.xml_pre)

            f.write(self.states_stamp)
            for s in self.states:
                f.write(s.as_string())

            f.write(self.transitions_stamp)
            for t in self.transitions:
                f.write(t.as_string())

            f.write(self.xml_post)

    def set_state_coords(self) -> None:
        last_x = State.MIN_X
        last_y = State.MIN_Y

        for s in self.states:
            s.x_coord = str(last_x)
            s.y_coord = str(last_y)

            last_x += 150.0

            if last_x > 500.0:
                last_x = State.MIN_X
                last_y += 70.0

    def print_as_matrix(self) -> None:
        print('States\tinitial\tfinal\t', end='')
        for a in self.alphabet:
            print(a+'\t', end='')
        print('lambda')

        for s in self.states:
            print(s.name+'\t', end='')
            print(s.is_initial, '\t', end='')
            print(s.is_final, '\t', end='')

            for a in self.alphabet:
                dest = self.find_state_destination(s, a)
                if not dest:
                    print('-\t', end='')
                else:
                    print(dest.name)

            dest = self.find_state_destination(s, None)
            if not dest:
                print('-\t', end='')
            else:
                print(dest.name)

    def find_state_destination(self, state: State, word: str) -> State:
        for trans in self.transitions:
            if trans.from_state.id == state.id:
                if trans.accepted_word == word:
                    return trans.to_state
        return None


def parse_args():
    parser = argparse.ArgumentParser(description='Wylosuj skończony automat')

    parser.add_argument("-n", help="Liczba stanów", metavar="N", type=int)
    parser.add_argument(
        "-fs", help="Liczba stanów końcowych", metavar="N", type=int)
    parser.add_argument(
        "-a", help="Alfabet, słowa rozpoznawane przez automat", metavar="A", nargs="*")
    parser.add_argument(
        "-fn", help="Nazwa pliku wyjściowego XML", metavar="xxx.jff", required=False)

    arguments = parser.parse_args()

    if not arguments.a:
        arguments.a = []
    if not arguments.fn:
        arguments.fn = "random_fa.jff"

    return arguments


if __name__ == "__main__":
    arg = parse_args()

    g = XML_Generator(arg.n, arg.fs, arg.a)

    g.print_as_matrix()
    g.gen_jff_file(arg.fn)
