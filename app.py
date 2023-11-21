#!/usr/bin/python3

from Modules.PoontoTitle import Title
import pandas as pd
import multiprocessing
import os
import sys
from time import perf_counter

class Worksheet:

    def __init__(self, filename, directory='Worksheets'):
        self.filename = filename
        self.directory = directory
        self.path = os.path.join(directory, filename)
        self.outpath = os.path.join('Output', f'TitlesFix___{filename}')
        self.df = pd.read_excel(self.path)
        self.titles = self.df[self.df.columns[0]].to_list()


def import_worksheets() -> list[Worksheet]:
    files = os.listdir('Worksheets')
    worksheets: list[Worksheet] = []
    for file in files:
        worksheets.append(Worksheet(file))
    return worksheets


def process_worksheets(worksheets: list[Worksheet], threads=multiprocessing.cpu_count() // 2):

    threaded = False
    if len(sys.argv) > 1:
        if '-threaded' in sys.argv:
            threaded = True

    for worksheet in worksheets:
        if threaded and threads > 1:
            with multiprocessing.Pool(threads) as pool:
                results = pool.map(Title, worksheet.titles)
        else:
            results = [Title(title) for title in worksheet.titles]
        df = pd.DataFrame([result.get_tuple() for result in results], columns = ['OG', 'FIX', 'Log', 'More Editing'])
        df.to_excel(worksheet.outpath, index=False)


def main():
    process_worksheets(import_worksheets())
    


if __name__ == "__main__":
    multiprocessing.freeze_support()
    start = perf_counter()
    main()
    print(perf_counter() - start)
