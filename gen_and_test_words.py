from fa_generator import XML_Generator
from random import randint

alpbt = ['a', 'b', 'c']


class WordGenerator:
    def __init__(self, n: int, alphabet: list):
        self.number_of_words = n
        self.alphabet = alphabet

        self.word_list = []

        self.generate_words()

    def generate_words(self) -> None:
        for i in range(self.number_of_words):
            nof_chars = randint(1, self.number_of_words)
            word = ''

            for j in range(nof_chars):
                word += self.alphabet[randint(0, len(self.alphabet)-1)]

            self.word_list.append(word)


class WordTest:
    def __init__(self, word_gen: WordGenerator, fa_gen: XML_Generator):
        self.word_list = word_gen.word_list
        self.fa_generator = fa_gen

        self.accepted = []
        self.rejected = []

        self.test()

    def test(self) -> None:
        for word in self.word_list:
            out = self.fa_generator.test_word(word)
            if out[1] == True:
                self.accepted.append(out[0])
            else:
                self.rejected.append(out[0])

    def generate_results(self) -> None:
        self.fa_generator.print_as_matrix()
        self.fa_generator.gen_jff_file("word_test.jff")

        print("Accepted:", self.accepted, '\n')
        print("Rejected:", self.rejected, '\n')

    def interesting_case(self) -> None:
        attempt = 1
        while len(self.accepted) < 2:
            print('Attempt no', attempt, '\r', end='')
            attempt += 1

            self.fa_generator.reset_generator()
            self.fa_generator.gen_fa()

            self.accepted = []
            self.rejected = []

            self.test()

        print()


if __name__ == "__main__":
    test = WordTest(WordGenerator(10, alpbt), XML_Generator(5, 3, alpbt))

    test.interesting_case()
    test.generate_results()
