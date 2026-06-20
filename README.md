# CTF Difficulty Benchmark

A benchmark dataset for three-class difficulty prediction of Capture The Flag (CTF) challenges from solution writeups. The dataset covers 297 challenges from 12 official HackTheBox events (2023--2025), with difficulty labels and temporal train/test splits.

This repository accompanies the paper "Predicting CTF Challenge Difficulty from Solution Writeups: A Benchmark Dataset and NLP Analysis" (Cyber-AI 2026).

## Contents

```
data/
  challenges.json          297 records: labels and metadata (no writeup text)
  feature_metadata.json    feature construction parameters and provenance
  llm_predictions.json     zero-shot LLM baseline outputs
  splits/
    temporal_train.csv     206 challenges from 2023--2024 events (benchmark split)
    temporal_test.csv       91 challenges from 2025 events (benchmark split)
    random_train.csv       random split, auxiliary
    random_test.csv        random split, auxiliary
    cv_folds.json          5-fold cross-validation indices
fetch_writeups.py          reconstructs writeup text from HackTheBox repos
```

## Writeup text

The writeup text is not redistributed here. The text is authored by HackTheBox and published in their official repositories under their own terms. This release contains the labels, metadata, and derived features. The text is retrieved from the source.

To reconstruct the full text locally:

```
python3 fetch_writeups.py
```

This reads `data/challenges.json`, downloads each writeup from the corresponding HackTheBox public repository, and writes `data/writeups.json` with the `writeup_text` field populated. The script uses only the Python standard library. Challenges that cannot be matched are reported at the end of the run. After it completes, `data/writeups.json` contains the complete dataset, including the writeup text, and is equivalent to the full corpus used in the paper. This file is what feature extraction and model training run on.

A small number of challenges (10 of 297, mostly the fullpwn category) use a non-standard writeup layout and are not retrieved automatically. These can be added manually from the source repositories.

## Data schema

Each record in `challenges.json` contains:

| Field | Description |
|---|---|
| `challenge_name` | Challenge name |
| `category` | One of: blockchain, crypto, forensics, fullpwn, hardware, misc, pwn, reversing, web |
| `difficulty` | Three-class label: Beginner, Intermediate, Advanced |
| `difficulty_original` | Original HackTheBox label: Very Easy, Easy, Medium, Hard, Insane |
| `ctf_event` | Source event repository |
| `year` | Event year |
| `writeup_length` | Character count of the original writeup |

The three-class label merges the original five levels: Very Easy and Easy to Beginner, Medium to Intermediate, Hard and Insane to Advanced.

## Splits

The temporal split is the benchmark partition. It trains on 2023--2024 events and tests on 2025 events. Report results on this split. The random split and cross-validation folds are auxiliary and provided for reference.

## Citation

```
@inproceedings{jimenez2026ctf,
  author    = {Jimenez, Jhaell and Kim, Yoohwan and Jo, Ju-Yeon},
  title     = {Predicting {CTF} Challenge Difficulty from Solution Writeups: A Benchmark Dataset and {NLP} Analysis},
  booktitle = {2026 International Conference on Cybersecurity and AI-Based Systems (Cyber-AI)},
  year      = {2026}
}
```

## License

The labels, metadata, derived features, and splits in this repository are released under CC BY 4.0. The writeup text retrieved by `fetch_writeups.py` remains subject to HackTheBox's terms.