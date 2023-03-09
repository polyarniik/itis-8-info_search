import os
from collections import defaultdict
from pathlib import Path

import nltk
import pymorphy2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer

BASE_PATH = Path(__file__).parent.parent
FILES_PATH = os.path.join(BASE_PATH, "files")
TOKENS_PATH = os.path.join(Path(__file__).parent.resolve(), "tokens.txt")
LEMMAS_PATH = os.path.join(Path(__file__).parent.resolve(), "lemmas.txt")


def get_text_from_html(file_path):
    with open(file_path) as f:
        soup = BeautifulSoup(f.read(), features="html.parser")
    return " ".join(soup.stripped_strings)


class Lemmatisator:
    BAD_TOKENS_TAGS = set(
        [
            "PREP",
            "CONJ",
            "PRCL",
            "INTJ",
            "LATN",
            "PNCT",
            "NUMB",
            "ROMN",
            "UNKN",
        ]
    )

    def __init__(self):
        nltk.download("stopwords")
        self.stop_words = set(stopwords.words("russian"))
        self.tokenizer = WordPunctTokenizer()
        self.morph_analyzer = pymorphy2.MorphAnalyzer()
        self.tokens = set()
        self.lemmas = defaultdict(set)

    def run_lemmatization(self, text):
        self.tokens.update(self.tokenizer.tokenize(text))
        self.filter_tokens()

    def filter_tokens(self):
        bad_tokens = set()
        for token in self.tokens:
            morph = self.morph_analyzer.parse(token)
            if (
                any([x for x in self.BAD_TOKENS_TAGS if x in morph[0].tag])
                or token in self.stop_words
            ):
                bad_tokens.add(token)
                continue
            if morph[0].score >= 0.5:
                self.lemmas[morph[0].normal_form].add(token)
        self.tokens = self.tokens - bad_tokens

    def write_tokens(self, path):
        with open(path, "w") as f:
            f.write("\n".join(self.tokens))

    def write_lemmas(self, path):
        with open(path, "w") as f:
            for token, lemmas in self.lemmas.items():
                f.write(f"{token}: {' '.join(lemmas)}\n")


if __name__ == "__main__":
    lemmatisator = Lemmatisator()
    pages_texts = []
    for root, _, files in os.walk(FILES_PATH):
        for file in files:
            pages_texts.append(get_text_from_html(os.path.join(root, file)))

    lemmatisator.run_lemmatization(" ".join(pages_texts))
    lemmatisator.write_tokens(TOKENS_PATH)
    lemmatisator.write_lemmas(LEMMAS_PATH)
