import re
import argparse
from copy import deepcopy


class XML_Misc:
    HEADER = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><!--Created with JFLAP 7.1.--><structure>\n\t<type>fa</type>\n\t<automaton>'
    STATES_STAMP = '\n\t\t<!--The list of states.-->'
    TRANS_STAMP = '\n\t\t<!--The list of transitions.-->'
    FOOTER = '\n\t</automaton>\n</structure>'

    STATE_START_EX = r'\s*<state id=\"(\d*)\" name=\"(q\d*)\">'
    IS_INIT_EX = r'\s*<initial/>'
    IS_FINAL_EX = r'\s*<final/>'
    STATE_END_EX = r'\s*</state>'

    TRANS_START_EX = r'\s*<transition>'
    TRANS_FROM_EX = r'\s*<from>(\d*)</from>'
    TRANS_TO_EX = r'\s*<to>(\d*)</to>'
    TRANS_READ_EX = r'\s*<read>(.*)</read>'
    TRANS_END_EX = r'\s*</transition>'

    TRANS_PRE = '\n\t\t<transition>'
    TRANS_POST = '\n\t\t</transition>'


class GV_Misc:
    IS_INIT_EX = r'q -> (q\d*)$'
    IS_FINAL_EX = r'(q\d*) \[shape=doublecircle\]'
    TRANS_EX = r'(q\d*) -> (q\d*)( \[label= \"(.*)\"\];)*'


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

    def as_xml_string(self) -> str:
        state_str = '\n\t\t<state id="'+self.id+'" name="'+self.name + \
            '">\n\t\t\t<x>'+self.x_coord+'</x>\n\t\t\t<y>'+self.y_coord+'</y>'

        if self.is_initial:
            state_str += '\n\t\t\t<initial/>'
        if self.is_final:
            state_str += '\n\t\t\t<final/>'

        return state_str+'\n\t\t</state>'

    def __str__(self):
        return "{} [{}] i:{}, f:{}".format(self.name, self.id, self.is_initial, self.is_final)


class Transition:
    def __init__(self, from_state: State, to_state: State, accepted_word: str = None):
        self.from_state = from_state
        self.to_state = to_state
        self.accepted_word = accepted_word

    def as_xml_string(self) -> str:
        trans_str = '\n\t\t\t<from>'+self.from_state.id + \
            '</from>\n\t\t\t<to>'+self.to_state.id+'</to>'

        if self.accepted_word:
            trans_str += '\n\t\t\t<read>'+self.accepted_word+'</read>'
        else:
            trans_str += '\n\t\t\t<read/>'

        return XML_Misc.TRANS_PRE+trans_str+XML_Misc.TRANS_POST

    def as_gv_string(self) -> str:
        trans_str = "\n{} -> {}".format(self.from_state.name,
                                        self.to_state.name)

        if self.accepted_word:
            trans_str += ' [label= "{}"];'.format(self.accepted_word)
        else:
            trans_str += ' [label= "λ"];'

        return trans_str

    def __str__(self):
        return "{} -> {}: {}".format(self.from_state.name, self.to_state.name, self.accepted_word)


class Converter:
    def __init__(self, filename: str):
        self.states = []
        self.transitions = []

        self.__read_file__(filename)

    def __read_file__(self, filename: str) -> None:
        file_type = re.match(r".*\.(.*)", filename).group(1)
        file_content = []

        with open(file=filename, mode="r", encoding="utf8") as file:
            file_content = file.readlines()

        if file_type == "jff" or file_type == "xml":
            print("> reading XML file...")
            self.__read_xml__(file_content)
        elif file_type == "gv":
            print("> reading GV file...")
            self.__read_gv__(file_content)

        print("> read {} lines\n> {} states\n> {} transitions".format(len(file_content),
                                                                      len(self.states), len(self.transitions)))

    def __read_xml__(self, file_content: list) -> None:
        state: State = None
        trans: Transition = None

        for line in file_content:
            if state:
                if re.match(XML_Misc.IS_INIT_EX, line):
                    state.is_initial = True
                elif re.match(XML_Misc.IS_FINAL_EX, line):
                    state.is_final = True
                elif re.match(XML_Misc.STATE_END_EX, line):
                    self.states.append(deepcopy(state))
                    state = None
                continue

            elif trans:
                if re.match(XML_Misc.TRANS_END_EX, line):
                    self.transitions.append(deepcopy(trans))
                    trans = None
                    continue

                from_match = re.match(XML_Misc.TRANS_FROM_EX, line)
                if from_match:
                    for s in self.states:
                        if s.id == from_match.group(1):
                            trans.from_state = s
                            break
                    continue

                to_match = re.match(XML_Misc.TRANS_TO_EX, line)
                if to_match:
                    for s in self.states:
                        if s.id == to_match.group(1):
                            trans.to_state = s
                            break
                    continue

                read_match = re.match(XML_Misc.TRANS_READ_EX, line)
                if read_match:
                    trans.accepted_word = read_match.group(1)

            else:
                new_state = re.match(XML_Misc.STATE_START_EX, line)

                if new_state:
                    state = State(new_state.group(1), new_state.group(2))
                    continue

                new_trans = re.match(XML_Misc.TRANS_START_EX, line)
                if new_trans:
                    trans = Transition(None, None)
                    continue

    def __read_gv__(self, file_content: list) -> None:
        initial_states = []

        for line in file_content:
            is_init = re.match(GV_Misc.IS_INIT_EX, line)
            if is_init:
                initial_states.append(is_init.group(1))
                continue

            is_final = re.match(GV_Misc.IS_FINAL_EX, line)
            if is_final:
                for s in self.states:
                    if s.name == is_final.group(1):
                        s.is_final = True
                        break
                continue

            new_trans = re.match(GV_Misc.TRANS_EX, line)
            if new_trans:
                first: State = None
                second: State = None

                for s in self.states:
                    if s.name == new_trans.group(1):
                        first = s
                    if s.name == new_trans.group(2):
                        second = s

                    if first and second:
                        break

                if not first:
                    first = State(new_trans.group(1)[1:], new_trans.group(1))
                    self.states.append(first)

                if not second:
                    second = State(new_trans.group(2)[1:], new_trans.group(2))
                    self.states.append(second)

                trans = Transition(first, second)
                if new_trans.group(3):
                    trans.accepted_word = new_trans.group(4)

                self.transitions.append(trans)

        for init in initial_states:
            for s in self.states:
                if s.name == init:
                    s.is_initial = True
                    break

    def to_xml(self, filename: str) -> None:
        self.__set_state_coords__()

        with open(file=filename, mode="w", encoding="utf8") as file:
            file.write(XML_Misc.HEADER)

            file.write(XML_Misc.STATES_STAMP)
            for s in self.states:
                file.write(s.as_xml_string())

            file.write(XML_Misc.TRANS_STAMP)
            for t in self.transitions:
                file.write(t.as_xml_string())

            file.write(XML_Misc.FOOTER)

    def __set_state_coords__(self) -> None:
        last_x = State.MIN_X
        last_y = State.MIN_Y

        for s in self.states:
            s.x_coord = str(last_x)
            s.y_coord = str(last_y)

            last_x += 150.0

            if last_x > 500.0:
                last_x = State.MIN_X
                last_y += 70.0

    def to_gv(self, filename: str) -> None:
        graph_name = re.sub("\..*", '', filename)

        with open(file=filename, mode="w", encoding="utf8") as file:
            file.write("digraph {} {{".format(graph_name))

            for s in self.states:
                if s.is_initial:
                    file.write("\nq -> {}".format(s.name))

            for t in self.transitions:
                file.write(t.as_gv_string())

            file.write("\nq [shape=point]")

            for s in self.states:
                if s.is_final:
                    file.write("\n{} [shape=doublecircle]".format(s.name))

            file.write("\n}")


def get_args():
    parser = argparse.ArgumentParser(
        description="Convert xml described automatas to graphviz and vice versa")

    parser.add_argument("input", help="Input filename", metavar="input_file.ext")
    parser.add_argument("-ox", help="Output xml filename",
                        metavar="xxx.(xml|jff)", required=False)
    parser.add_argument("-og", help="Output graphviz filename",
                        metavar="xxx.gv", required=False)

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    c = Converter(args.input)

    if args.ox:
        c.to_xml(args.ox)
    if args.og:
        c.to_gv(args.og)
