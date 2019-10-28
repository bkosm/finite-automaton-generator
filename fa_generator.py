from random import randint
import argparse
from sys import exit


class State:
    MIN_X: float = 50.0
    MIN_Y: float = 30.0

    def __init__(self, id_str: str, name: str, initial: bool = False, final: bool = False):
        self.id = id_str
        self.name = name

        self.is_initial = initial
        self.is_final = final

        self.entering_trans = []
        self.outcoming_trans = []

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
        for i in range(self.number_of_transitions):
            from_state = self.random_state()
            to_state = self.random_state()

            trans = Transition(from_state, to_state, self.random_word())
            if self.alphabet and randint(1, 5) == 1:
                trans.accepted_word = None
            elif not self.alphabet:
                trans.accepted_word = None

            from_state.outcoming_trans.append(trans)
            to_state.entering_trans.append(trans)

            self.transitions.append(trans)

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
                    print(dest.name, '\t', end='')

            dest = self.find_state_destination(s, None)
            if not dest:
                print('-')
            else:
                print(dest.name)

        print()

    def find_state_destination(self, state: State, word: str) -> State:
        for trans in self.transitions:
            if trans.from_state.id == state.id:
                if trans.accepted_word == word:
                    return trans.to_state
        return None

    def generate_fa_accepted_word(self) -> str:
        final_states = [s for s in self.states if s.is_final]

        for ref in final_states:
            msg = ''
            loop_breaker = 0

            while True:
                for trans in self.transitions:
                    if trans.to_state.id == ref.id:
                        if trans.accepted_word:
                            msg += trans.accepted_word[::-1]
                        ref = trans.from_state
                        break

                loop_breaker += 1

                if ref.is_initial:
                    return msg[::-1]
                elif loop_breaker > 1000:
                    break

        return "~"

    def gen_interesting_case(self) -> None:
        attempt = 1
        while not len(self.generate_fa_accepted_word()) > 3:
            print('Attempt no', attempt, '\r', end='')
            attempt += 1

            self.reset_generator()
            self.gen_fa()

        print()

    def reset_generator(self) -> None:
        self.number_of_transitions = randint(0, 2*self.number_of_states)
        self.states = []
        self.transitions = []

    # Działa tylko na slowach nad alfabetami z pojedynczych liter
    def test_word(self, word: str) -> (str, bool):
        ref = self.states[0]
        word_index = 0

        while word_index < len(word):
            for trans in ref.outcoming_trans:
                if trans.accepted_word == word[word_index]:
                    word_index += 1
                    ref = trans.to_state
                    break
            else:
                return (word, False)

        if ref.is_final:
            return (word, True)

        return (word, False)


def parse_args():
    parser = argparse.ArgumentParser(description='Generate a finite automata')

    parser.add_argument("-n", help="Number of states", metavar="N", type=int)
    parser.add_argument(
        "-fs", help="Number of final states", metavar="N", type=int)
    parser.add_argument(
        "-a", help="List of possible words to consume on hops", metavar="A", nargs="*")
    parser.add_argument(
        "-fn", help="Output XML filename", metavar="xxx.jff", required=False)
    parser.add_argument("--interesting", help="Generate an example with a more interesting accepted word",
                        action="store_true", required=False)

    arguments = parser.parse_args()

    if not arguments.a:
        arguments.a = []

    return arguments


if __name__ == "__main__":
    arg = parse_args()

    g = XML_Generator(arg.n, arg.fs, arg.a)

    if arg.interesting:
        g.gen_interesting_case()

    g.print_as_matrix()
    print('random word accepted by fa: "', g.generate_fa_accepted_word(), '"')

    if arg.fn:
        g.gen_jff_file(arg.fn)
