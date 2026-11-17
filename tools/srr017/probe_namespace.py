"""Print pinned PE instructions and call sites for the SRR-017 source witness."""

import argparse
from pathlib import Path
from struct import unpack

from tools.srr011.inspect_pe import RetailImage, print_instruction, scan


WINDOWS = (
    (0x140573774, 0x140573794),
    (0x142011503, 0x14201152F),
    (0x14200A5D2, 0x14200A616),
    (0x140598430, 0x1405984C5),
    (0x1405B78C0, 0x1405B79A0),
    (0x140599680, 0x1405996CF),
    (0x14059974C, 0x140599770),
    (0x14059FCF0, 0x14059FE23),
    (0x14058E453, 0x14058E508),
    (0x14058E577, 0x14058E657),
    (0x1405E0DE1, 0x1405E0EBE),
    (0x1405E3980, 0x1405E3A2B),
    (0x1405DC730, 0x1405DC887),
    (0x140573968, 0x140573974),
    (0x140597319, 0x140597350),
    (0x1405973F0, 0x1405973FF),
    (0x140597C6A, 0x140597C9D),
    (0x140597939, 0x140597979),
    (0x1405B694C, 0x1405B6966),
    (0x1405B5BE0, 0x1405B5BF9),
    (0x1405B99D8, 0x1405B9A25),
    (0x1405B9F52, 0x1405B9FD9),
    (0x1405BA022, 0x1405BA05D),
    (0x1405BA09F, 0x1405BA13C),
    (0x1405BA1D5, 0x1405BA1F4),
    (0x1405BA859, 0x1405BA881),
    (0x1428E4330, 0x1428E4366),
    (0x1427D8950, 0x1427D89B2),
    (0x1427D7FD6, 0x1427D8005),
    (0x1427D95DD, 0x1427D9692),
    (0x1427FB1A0, 0x1427FB1C3),
)
TABLES = (0x144B29B80, 0x144DA7FB8, 0x144D9C578, 0x144D9C498, 0x144D9D0B8)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("retail_pe", type=Path)
    args = parser.parse_args()
    image = RetailImage(args.retail_pe)
    for table in TABLES:
        locator, = unpack("<Q", image.read(table - 8, 8))
        type_rva, = unpack("<I", image.read(locator + 12, 4))
        name = image.read(0x140000000 + type_rva + 16, 100).split(b"\0", 1)[0].decode("ascii")
        methods = ", ".join(f"{target:#x}" for target in unpack("<10Q", image.read(table, 80)))
        print(f"{name} vtable {table:#x} locator {locator:#x}: {methods}")
    print("startup relative Data string suffix:", image.read(0x144CB45DD, 5))
    for start, end in WINDOWS:
        for instruction in image.decode(start, end):
            print_instruction(instruction)
    scan(image, {0x1405994A0, 0x14059FCF0, 0x1405E0D50, 0x1405E3980, 0x1405DC730, 0x144D25050,
                 0x1405972B0, 0x140597A70, 0x1405B9750, 0x1405B9950, 0x1461FAB68})


if __name__ == "__main__":
    main()
