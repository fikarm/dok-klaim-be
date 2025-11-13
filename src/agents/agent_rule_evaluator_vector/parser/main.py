"""
Main file untuk membuat dataset yang nantinya
akan digunakan untuk melatih algoritma SVM.
"""

import pymupdf
import pandas as pd
from pathlib import Path
from datetime import datetime
from src.agents.agent_rule_evaluator_vector.parser.schema import NamaBerkas
from src.agents.agent_rule_evaluator_vector.parser.reader import DokumenKlaim
from src.agents.agent_rule_evaluator_vector.parser.extractor import extractors


INPUTS_DIR = Path("inputs")
OUTPUTS_DIR = Path("outputs")
DATASET_DIR = Path("dataset")


def simpan_sampel(nama_berkas: NamaBerkas, nosep: str, content: str):
    berkas_dir = Path(OUTPUTS_DIR, nama_berkas.name)
    berkas_dir.mkdir(parents=True, exist_ok=True)
    outpath = Path(berkas_dir, nosep + ".txt")
    with open(outpath, "w") as f:
        f.write(content)


def ekstraksi_semua_berkas():
    for path in INPUTS_DIR.iterdir():
        print()
        print()
        print("File: ", path, "...", end="")

        if not path.is_file():
            print("bukan file, skip")
            continue

        print()

        with pymupdf.open(path) as pdf:
            try:
                dokklaim = DokumenKlaim(pdf)

                # loop setiap ekstraktor
                for nama_berkas in extractors:
                    print(">> ektraksi berkas", nama_berkas, "...", end="")
                    content = dokklaim.get_berkas(nama_berkas)

                    if content:
                        print("Konten: ", content[:10], "...")
                        simpan_sampel(nama_berkas, dokklaim.no_sep, content)
                    else:
                        print("___TIDAK ADA KONTEN___")
            except ValueError as e:
                print(e)
                continue


def make_dataset():
    dataset: dict[str, list[str]] = {"content": [], "label": []}

    # loop folder berkas
    # nama folder akan menjadi label di dataset
    for dir_berkas in OUTPUTS_DIR.iterdir():

        if not dir_berkas.is_dir():
            continue

        # loop file
        for filepath in dir_berkas.iterdir():

            if not filepath.is_file():
                continue

            with open(filepath, "r") as berkas:
                label = dir_berkas.name
                content = berkas.read()

                # tambahkan konten dan label di dataset csv
                dataset["content"].append(content)
                dataset["label"].append(label)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    dataset_path = Path(DATASET_DIR, f"{timestamp}.csv")
    df = pd.DataFrame(dataset)
    df.to_csv(dataset_path, index=False)

    print(df.head())


def parse():
    ekstraksi_semua_berkas()

    make_dataset()


if __name__ == "__main__":
    parse()
