import os
import json
import copy
import codecs
import random
import numpy as np
import pandas as pd


def get_task_data(data_path):
    with codecs.open(data_path, mode='r', encoding='utf8') as f:
        reader = f.readlines(f)    
        
    data_list = []

    for dialogue_ in reader:
        dialogue_ = json.loads(dialogue_)
        
        _dialog_id = dialogue_['dialog_id']
        
        for content_idx_, contents_ in enumerate(dialogue_['dialog_info']):

            terms_ = contents_['ner']

            if len(terms_) != 0:
                idx_ = 0
                for _, term_ in enumerate(terms_):
                    
                    entity_ = dict()

                    entity_['dialogue'] = dialogue_
                    
                    entity_['sentence_id'] = dialogue_['dialog_info'][content_idx_]['sentence_id']
                    
                    _text = dialogue_['dialog_info'][content_idx_]['text']
                    _text_list = list(_text)
                    _text_list.insert(term_['range'][0], '[unused1]')
                    _text_list.insert(term_['range'][1]+1, '[unused2]')
                    _text = ''.join(_text_list)
                    
                    if content_idx_ - 1 >= 0 and len(dialogue_['dialog_info'][content_idx_-1]) < 40:
                        forward_text = dialogue_['dialog_info'][content_idx_-1]['sender'] + ':' + dialogue_['dialog_info'][content_idx_-1]['text'] + ';'
                    else:
                        forward_text = ''
                    
                    if contents_['sender'] == '医生':
                        
                        if content_idx_ + 1 >= len(dialogue_['dialog_info']):
                            entity_['text_a'] = forward_text + dialogue_['dialog_info'][content_idx_]['sender'] + ':' + _text
                        else:
                            entity_['text_a'] = forward_text + dialogue_['dialog_info'][content_idx_]['sender'] + ':' + _text + ';'
                            temp_index = copy.deepcopy(content_idx_) + 1
                        
                            speaker_flag = False
                            sen_counter = 0
                            while True:

                                if dialogue_['dialog_info'][temp_index]['sender'] == '患者':
                                    sen_counter += 1
                                    speaker_flag = True
                                    entity_['text_a'] += dialogue_['dialog_info'][temp_index]['sender'] + ':' + dialogue_['dialog_info'][temp_index]['text'] + ';'
                                
                                if sen_counter > 3:
                                    break
                                
                                temp_index += 1
                                if temp_index >= len(dialogue_['dialog_info']):
                                    break
                                    
                    elif contents_['sender'] == '患者':
                        if content_idx_ + 1 >= len(dialogue_['dialog_info']):
                            entity_['text_a'] = forward_text + dialogue_['dialog_info'][content_idx_]['sender'] + ':' + _text
                        else:
                            entity_['text_a'] = forward_text + dialogue_['dialog_info'][content_idx_]['sender'] + ':' + _text + ';'
                            temp_index = copy.deepcopy(content_idx_) + 1
                        
                            speaker_flag = False
                            sen_counter = 0
                            while True:

                                sen_counter += 1
                                speaker_flag = True
                                entity_['text_a'] += dialogue_['dialog_info'][temp_index]['sender'] + ':' + dialogue_['dialog_info'][temp_index]['text'] + ';'
                                
                                if sen_counter > 3:
                                    break
                                
                                temp_index += 1
                                if temp_index >= len(dialogue_['dialog_info']):
                                    break
                    else:
                        entity_['text_a'] = forward_text + dialogue_['dialog_info'][content_idx_]['sender'] + ':' + _text
                        
                    if term_['name'] == 'undefined':
                        add_text = '|没有标准化'
                    else:
                        add_text = '|标准化为' + term_['name']
                        
                    entity_['text_b'] = term_['mention'] + add_text
                    entity_['text_b_copy'] = term_['mention'] 
                    entity_['start_idx'] = term_['range'][0]
                    entity_['end_idx'] = term_['range'][1] - 1
                    entity_['type'] = term_['type']
                    
                    try:
                        entity_['label_b'] = term_['name']
                    except:
                        print(contents_)
                        print(term_)
                    entity_['label'] = term_['attr']
                    entity_['dialog_id'] = _dialog_id
                    idx_ += 1
                    
                    if entity_['label'] == '':
                        continue
                    
                    if len(entity_) == 0:
                        continue
                        
                    data_list.append(entity_)
                
            
    data_df = pd.DataFrame(data_list)

    data_df = data_df.loc[:,['dialog_id', 'sentence_id', 'text_b_copy', 'text_a', 'text_b', 'start_idx', 'end_idx', 'type', 'label_b', 'label', 'dialogue']]

    return data_df


if __name__ == "__main__":
    # https://github.com/DataArk/CHIP2021-Task1-Top1
    data_df = get_task_data("CHIP2021-Task1-Top1/data/source_datasets/fliter_train_result2.txt")
    data_df = data_df[data_df['label_b'] != 'undefined'].reset_index(drop=True)
    #data_df.to_csv("chip2021-task1-top1.csv", index=False)
