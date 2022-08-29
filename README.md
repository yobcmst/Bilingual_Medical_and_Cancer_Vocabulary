# TODO

- [x] Basic preprocessor for CMedQANER & cEHRNER, python src/chineseBlue_ner.py
- [x] cMedQANER (zh-tw) + (en), save to json file

# Data Source (1): ChineseBLUE
- https://github.com/alibaba-research/ChineseBLUE

```
|─── cMedQANER
|    ├── cMedQANER.tar.gz
|    ├── dev.json
|    ├── dev.txt
|    ├── test.json
|    ├── test.txt
|    ├── train.json
|    └── train.txt
├── cEHRNER
|    ├── cEHRNER.tar.gz
|    ├── dev.json
|    ├── dev.txt
|    ├── test.json
|    ├── test.txt
|    ├── train.json
|    └── train.txt
```

# Data Source (2): CHIP2021
- https://github.com/DataArk/CHIP2021-Task1-Top1
```
    git clone https://github.com/DataArk/CHIP2021-Task1-Top1
    python src/ckip2021_task1_top1.py
```
