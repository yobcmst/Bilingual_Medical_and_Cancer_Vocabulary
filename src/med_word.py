import json
import pandas as pd
from itertools import chain
from typing import List
from opencc import OpenCC
from deep_translator import GoogleTranslator


def load_med_word(path: str) -> List[str]:
    """TODO: convert all the zh-tw into en text ?"""
    with open(path, encoding="utf-8") as f:
        f_lst = f.readlines()

    translator = OpenCC("s2t")

    f_lst = [
        translator.convert(t.strip())
        for t in f_lst
    ]
    return f_lst


def _translate_to_en(f_lst: List[str]):
    f_lst_en = []
    f_lst_inp = []
    for idx, t in enumerate(f_lst):
        f_lst_inp.append(t)
        if idx % 100 == 0 and idx != 0:
            t_inp = "\n".join(f_lst_inp)
            if len(t_inp) > 5000:
                print(idx)
            #print(t_inp)
            f_lst_inp = []
            f_lst_en.append(translator.translate(t_inp))

        if idx == 10:
            print(f"idx: {idx} is done...")

    t_inp = "\n".join(f_lst_inp)

    f_lst_en.append(translator.translate(t_inp))
    return f_lst_en


if __name__ == "__main__":
    translator = GoogleTranslator(source="zh-tw", target="en")
    f_lst = load_med_word("Chinese-Word2vec-Medicine/med_word.txt")
    f_lst_en = _translate_to_en(f_lst)
    f_lst_en_all = list(chain.from_iterable([t_text.split("\n") for t_text in f_lst_en]))

    len(f_lst_en_all)

    df = pd.DataFrame({"text": f_lst, "text_en": f_lst_en_all})

    records = df.to_dict("records")

    with open("processed_data/med_words.json", "w") as f:
        json.dump(records, f)