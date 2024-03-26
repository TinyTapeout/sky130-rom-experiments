# ROM Utilities

This directory contains a collection of utilities for working with ROMs hardened by the OpenRAM compiler. They work directly on the GDSII files and are not dependent on the OpenRAM compiler.

## Setup

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Dumping a ROM from GDS

To dump a ROM from a GDS file, use the `rom_dump.py` script. It takes the GDS file as input and outputs the ROM contents in a hexadecimal format.

```bash
python rom_dump.py <input_rom.gds>
```

## Replacing ROM contents in GDS

To replace the contents of a ROM in a GDSII file, use the `rom_burn.py` script. It takes the GDS file and the new ROM contents (as a binary file) as input and outputs a new GDS file with the updated ROM contents.

```bash
python rom_burn.py <input_rom.gds> <new_rom_data.bin> <output_rom.gds>
```

