import glob
import json
import pandas as pd
from typing import List, Dict, Optional, Any
from itertools import chain
from dataclasses import dataclass
from tqdm.auto import tqdm

from opencc import OpenCC
from deep_translator import GoogleTranslator

translator_s2t = OpenCC(config="s2t")
translator_t2s = OpenCC(config="t2s")

@dataclass
class OneMention:
    mention: str # zh-cn
    offset: str
    label: Optional[str]=None # the same as type
    type: Optional[str]=None  # the same as type
    mention_tw: Optional[str]=None # zh-tw
    guid: Optional[str]=None
    start_idx: Optional[int]=None
    end_idx: Optional[int]=None
    def __post_init__(self):
        if self.offset is not None:
            self.offset = int(self.offset)
            self.start_idx = self.offset
            self.end_idx = int(self.offset) + len(self.mention)
            if self.label is not None:
                self.label = translator_s2t.convert(self.label)
                self.type = self.label
            if self.type is not None:
                self.type = translator_s2t.convert(self.type)
                self.label = self.type
            self.mention_tw = translator_s2t.convert(self.mention)

@dataclass
class MentionText:
    text: str
    mention_data: List[OneMention]
    def get_mentions(self, lang: str="zh-tw", label: str="symptom"):
        mentions = []
        for m in self.mention_data:
            if m.label != label:
                continue
            if lang == "zh-cn":
                m_text = m.mention
            elif lang == "zh-tw":
                m_text = m.mention_tw
            mentions.append(m_text)
        return mentions

def load_json_data(path: str, to_mention_text: bool=True) -> List[MentionText]:
    with open(path) as f:
        f_lst = f.readlines()
    data = [json.loads(f) for f in f_lst]

    if to_mention_text:
        for A in data:
            text = A['text']
            mention_data = A['mention_data']
        data = [
            MentionText(A['text'], [OneMention(**m) for m in A['mention_data']])
            for A in data
        ]
    return data

def get_data(data_dir: str, dataset: str="cMedQANER"):
    assert dataset in [
        "cMedQANER",
        "cEHRNER",
    ]
    train_data = load_json_data(f"{data_dir}/{dataset}/train.json")
    dev_data = load_json_data(f"{data_dir}/{dataset}/dev.json")
    test_data = load_json_data(f"{data_dir}/{dataset}/test.json")
    all_data = train_data + dev_data + test_data

    ALL_LABELS = sorted(set([cc.label for c in all_data for cc in c.mention_data]))
    print(f"ALL_LABELS: {ALL_LABELS}")
    return all_data, ALL_LABELS

def _get_mentions_zhtw(data, labels):
    all_mentions = {}
    for label in labels:
        mentions_ = [cont.get_mentions(lang="zh-tw", label=label) for cont in data]
        all_mentions[label] = sorted(set(chain.from_iterable(mentions_)))
    return all_mentions

def convert_zhtw_to_en(v: List[str]):
    translator_t2en = GoogleTranslator(source='chinese (traditional)', target='en')
    v_out = []
    for idx, vv in enumerate(tqdm(v, total=len(v))):
        try:
            v_out.append(translator_t2en.translate(vv))
        except:
            translator_t2en = GoogleTranslator(source='chinese (traditional)', target='en')
            v_out.append(translator_t2en.translate(vv))
    return v_out

def to_json(all_mentions: Dict[str, Any], save_file: str):
    assert save_file.endswith(".json")
    with open(save_file, "w") as f:
        json.dump(all_mentions, f)

def get_all_mentions(data, labels, lang="zh-tw", save_file: Optional[str]=None):
    all_mentions = _get_mentions_zhtw(data, labels)

    if lang == "zh-tw":
        if save_file is not None:
            to_json(all_mentions, save_file)
        return all_mentions

    elif lang == "en":
        all_mentions_en = {}
        for k, v in all_mentions.items():
            print(k, len(v))
            v_out = convert_zhtw_to_en(v)
            all_mentions_en[f"{k}"] = v_out

        if save_file is not None:
            to_json(all_mentions_en, save_file)

        return all_mentions_en
    else:
        raise ValueError(f"Invalid lang: {lang}")

if __name__ == "__main__":

    data_dir = "ChineseBLUE/data"
    DATASET = "cEHRNER" # "cMedQANER"
    output_dir = 'processed_data_chineseblue'

    data, label = get_data(data_dir=data_dir, dataset=DATASET)

    all_mentions = get_all_mentions(
        data,
        label,
        lang='zh-tw',
        save_file=f"{output_dir}/{DATASET}_mentions.json",
    )

    # all_mentions_en = get_all_mentions(
    #     data,
    #     label,
    #     lang='en',
    #     save_file=f"{output_dir}/{DATASET}_mentions_en.json",
    # )
