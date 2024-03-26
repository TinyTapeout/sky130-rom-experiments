# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2024, Tiny Tapeout LTD
# Author: Uri Shaked

import argparse
from typing import List, Set

import klayout.db as pya

WORD_BITS = 8


def chunk_data(cols: int, word_bits: int, words_per_row: int, raw_data: List[int]):
    """
    Chunks a flat list of bits into rows based on the calculated ROM sizes. Handles scrambling of data.
    Source: compile/rom_config.py from OpenRAM compiler
    """
    bits_per_row = cols

    chunked_data = []

    for i in range(0, len(raw_data), bits_per_row):
        row_data = raw_data[i : i + bits_per_row]
        if len(row_data) < bits_per_row:
            row_data = [0] * (bits_per_row - len(row_data)) + row_data
        chunked_data.append(row_data)

    scrambled_chunked = []

    for row_data in chunked_data:
        scambled_data = []
        for bit in range(word_bits):
            for word in range(words_per_row):
                scambled_data.append(row_data[bit + word * word_bits])
        scrambled_chunked.append(scambled_data)
    return scrambled_chunked


parser = argparse.ArgumentParser(description="Burn a binary into a ROM GDS file")
parser.add_argument("input_gds", help="Input GDS ROM file")
parser.add_argument("input_bin", help="Input binary file (to burn)")
parser.add_argument("output_gds", help="Output GDS file")
args = parser.parse_args()

layout = pya.Layout()
layout.read(args.input_gds)

with open(args.input_bin, "rb") as f:
    data = f.read()
    data = "".join(f"{n:08b}" for n in data)
    data = list(data)
    raw_data = [int(x) for x in data]

top_cell_name = layout.top_cell().name
array_cell = layout.cell(f"{top_cell_name}_rom_base_array")
zero_cell_name = f"{top_cell_name}_rom_base_zero_cell"
one_cell_name = f"{top_cell_name}_rom_base_one_cell"
zero_cell = layout.cell(zero_cell_name)
one_cell = layout.cell(one_cell_name)

cols: Set[int] = set()
rows: Set[int] = set()
for instance in array_cell.each_inst():
    if instance.cell.name in [zero_cell_name, one_cell_name]:
        cols.add(instance.bbox().left)
        rows.add(instance.bbox().top)

sorted_cols = sorted(list(cols))
sorted_rows = sorted(list(rows))

bitmap = chunk_data(
    cols=len(sorted_cols),
    word_bits=WORD_BITS,
    words_per_row=len(sorted_cols) // WORD_BITS,
    raw_data=raw_data,
)

for instance in array_cell.each_inst():
    if instance.cell.name in [zero_cell_name, one_cell_name]:
        row = sorted_rows.index(instance.bbox().top)
        col = sorted_cols.index(instance.bbox().left)
        if row + 1 == len(sorted_rows):
            continue  # Top row is always ones
        instance.cell = one_cell if bitmap[row][col] else zero_cell

layout.write(args.output_gds)
