# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2024, Tiny Tapeout LTD
# Author: Uri Shaked

import argparse
from typing import List, Set
import klayout.db as pya

WORD_BITS = 8


def unchunk_data(cols: int, word_bits: int, words_per_row: int, data: List[List[int]]):
    """
    Unchunks and unscrambles data that was previously chunked and scrambled. This is meant to reverse
    the chunk_data function.
    """
    bits_per_row = cols
    unscrambled_chunked = []

    # Unscramble each row
    for row_data in data:
        unscrambled_data = [
            0
        ] * bits_per_row  # Initialize with zeros to the size of a row
        for bit in range(word_bits):
            for word in range(words_per_row):
                unscrambled_data[bit + word * word_bits] = row_data.pop(0)
        unscrambled_chunked.append(unscrambled_data)

    # Flatten the list and remove padding zeros from the end of the last row
    flat_data = [bit for row in unscrambled_chunked for bit in row]
    # Remove padding zeros that were added to the last row in chunk_data
    while flat_data[-1] == 0:
        flat_data.pop()

    return flat_data


parser = argparse.ArgumentParser(description="Dump a binary from a ROM GDS file")
parser.add_argument("input_gds", help="Input GDS ROM file")
args = parser.parse_args()

layout = pya.Layout()
layout.read(args.input_gds)

top_cell_name = layout.top_cell().name
array_cell = layout.cell(f"{top_cell_name}_rom_base_array")
zero_cell_name = f"{top_cell_name}_rom_base_zero_cell"
one_cell_name = f"{top_cell_name}_rom_base_one_cell"

cols: Set[int] = set()
rows: Set[int] = set()
for instance in array_cell.each_inst():
    if instance.cell.name in [zero_cell_name, one_cell_name]:
        cols.add(instance.bbox().left)
        rows.add(instance.bbox().top)

sorted_cols = sorted(list(cols))
sorted_rows = sorted(list(rows))
bitmap = [[0 for _ in range(len(sorted_cols))] for _ in range(len(sorted_rows))]
for instance in array_cell.each_inst():
    if instance.cell.name in [zero_cell_name, one_cell_name]:
        row = sorted_rows.index(instance.bbox().top)
        col = sorted_cols.index(instance.bbox().left)
        bitmap[row][col] = 1 if instance.cell.name == one_cell_name else 0
# Top (last) row is always ones, remove it
del bitmap[-1]

decoded = unchunk_data(
    cols=len(sorted_cols),
    word_bits=WORD_BITS,
    words_per_row=len(sorted_cols) // WORD_BITS,
    data=bitmap,
)

# Reconstruct bytes from bits
bytes = []
for i in range(len(decoded) // 8):
    bytes += [int("".join(str(x) for x in decoded[i * 8 : (i + 1) * 8]), 2)]

# Hex dump
for i in range(0, len(bytes), 16):
    print(
        " ".join(f"{x:02X}" for x in bytes[i : i + 16]).ljust(49),
        "".join(chr(x) if 32 <= x < 127 else "." for x in bytes[i : i + 16]),
    )
