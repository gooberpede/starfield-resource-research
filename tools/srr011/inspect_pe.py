"""Read the pinned retail PE as data and print bounded native checks to stdout."""

import argparse
from bisect import bisect_right
from collections import defaultdict
import hashlib
from pathlib import Path
import re
import struct

from capstone import Cs, CS_ARCH_X86, CS_GRP_CALL, CS_GRP_JUMP, CS_MODE_64, CS_OP_IMM, CS_OP_MEM
from capstone.x86_const import X86_REG_RIP


SHA256 = "7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28"
BASE = 0x140000000


class RetailImage:
    def __init__(self, path):
        self.data = path.read_bytes()
        digest = hashlib.sha256(self.data).hexdigest()
        if digest != SHA256:
            raise ValueError(f"Unexpected executable SHA-256: {digest}")
        pe, = struct.unpack_from("<I", self.data, 0x3C)
        machine, count = struct.unpack_from("<HH", self.data, pe + 4)
        opt_size, = struct.unpack_from("<H", self.data, pe + 20)
        opt = pe + 24
        magic, = struct.unpack_from("<H", self.data, opt)
        base, = struct.unpack_from("<Q", self.data, opt + 24)
        if (self.data[pe:pe + 4], machine, magic, base) != (b"PE\0\0", 0x8664, 0x20B, BASE):
            raise ValueError("Expected the pinned AMD64 PE32+ layout")
        self.sections = {}
        for index in range(count):
            offset = opt + opt_size + 40 * index
            name, virtual_size, rva, raw_size, raw = struct.unpack_from("<8sIIII", self.data, offset)
            self.sections[name.rstrip(b"\0").decode("ascii")] = (BASE + rva, min(virtual_size, raw_size), raw)
        self.text, text_size, _ = self.sections[".text"]
        self.text_end = self.text + text_size
        directory, size = struct.unpack_from("<II", self.data, opt + 112 + 3 * 8)
        rows = struct.iter_unpack("<III", self.read(BASE + directory, size))
        self.ranges = sorted({
            (BASE + start, BASE + end) for start, end, _ in rows
            if self.text <= BASE + start < BASE + end <= self.text_end
        })
        self.starts = [start for start, _ in self.ranges]
        self.decoder = Cs(CS_ARCH_X86, CS_MODE_64)
        self.decoder.detail = True

    def read(self, address, count):
        for start, size, raw in self.sections.values():
            if start <= address < address + count <= start + size:
                offset = raw + address - start
                return self.data[offset:offset + count]
        raise ValueError(f"Range {address:#x}+{count:#x} is not file-backed")

    def decode(self, start, end):
        return list(self.decoder.disasm(self.read(start, end - start), start))

    def extent(self, position):
        index = bisect_right(self.starts, position) - 1
        if index >= 0:
            start, end = self.ranges[index]
            if start <= position < end:
                return start, end
        return None


def targets_of(instruction):
    if instruction.group(CS_GRP_JUMP) or instruction.group(CS_GRP_CALL):
        for operand in instruction.operands:
            if operand.type == CS_OP_IMM:
                yield "branch", operand.imm
    for operand in instruction.operands:
        if operand.type == CS_OP_MEM and operand.mem.base == X86_REG_RIP:
            yield "rip", instruction.address + instruction.size + operand.mem.disp


def print_instruction(instruction):
    refs = " ".join(f"{kind}={target:#x}" for kind, target in targets_of(instruction))
    print(f"{instruction.address:#x} {instruction.mnemonic} {instruction.op_str} {refs}".rstrip())


def scan(image, targets):
    code = image.read(image.text, image.text_end - image.text)
    candidates = defaultdict(set)
    # Byte prefilters are permissive. Only a decoded operand in the selected
    # exception range promotes a hit to a verified reference.
    for match in re.finditer(rb"(?=([\xe8\xe9]|\x0f[\x80-\x8f]))", code):
        offset = match.end(1)
        if offset + 4 <= len(code):
            target = image.text + offset + 4 + struct.unpack_from("<i", code, offset)[0]
            if target in targets:
                candidates[image.text + match.start()].add(("branch", target))
    for match in re.finditer(rb"[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]", code):
        offset = match.end()
        if offset + 4 <= len(code):
            zero = image.text + offset + 4 + struct.unpack_from("<i", code, offset)[0]
            for target in targets.intersection(range(zero, zero + 5)):
                candidates[image.text + match.start()].add(("rip", target))
    print(f".text [{image.text:#x}, {image.text_end:#x}), "
          f"{len(image.ranges)} exception ranges, {len(candidates)} candidate byte positions")
    verified = set()
    decoded = {}
    for position, expected in sorted(candidates.items()):
        extent = image.extent(position)
        if extent is None:
            print(f"{position:#x} outside selected exception ranges {sorted(expected)}")
            continue
        if extent not in decoded:
            decoded[extent] = image.decode(*extent)
        instructions = decoded[extent]
        if not instructions or instructions[-1].address + instructions[-1].size != extent[1]:
            print(f"{position:#x} partial decode from {extent[0]:#x}")
        for ins in instructions:
            if not ins.address <= position < ins.address + ins.size:
                continue
            for kind, target in expected.intersection(targets_of(ins)):
                if (ins.address, kind, target) not in verified:
                    verified.add((ins.address, kind, target))
                    print(f"verified range={extent[0]:#x} {kind}={target:#x}", end=" ")
                    print_instruction(ins)
            break
    print(f"{len(verified)} distinct decoded references")
    for target in sorted(targets):
        pattern = re.compile(re.escape(struct.pack("<Q", target)))
        for name, (start, size, raw) in image.sections.items():
            for match in pattern.finditer(image.data, raw, raw + size):
                print(f"qword {target:#x} {name} {start + match.start() - raw:#x}")


def address(text):
    return int(text, 16)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("scan", "functions"):
        sub.add_parser(name).add_argument("addresses", type=address, nargs="+")
    for name in ("window", "data"):
        command = sub.add_parser(name)
        command.add_argument("start", type=address)
        command.add_argument("size", type=address, help="hexadecimal byte count")
    args = parser.parse_args()
    try:
        image = RetailImage(args.image)
        print(f"SHA-256 {SHA256}, base {BASE:#x}")
        if args.command == "scan":
            scan(image, set(args.addresses))
        elif args.command == "data":
            contents = image.read(args.start, args.size)
            printable = "".join(chr(byte) if 32 <= byte < 127 else "." for byte in contents)
            print(f"{args.start:#x} {contents.hex(' ')}  {printable}")
        elif args.command == "window":
            for ins in image.decode(args.start, args.start + args.size):
                print_instruction(ins)
        else:
            for start in args.addresses:
                extent = image.extent(start)
                if extent is None or start != extent[0]:
                    raise ValueError(f"{start:#x} is not a selected exception-range start; use window")
                print(f"Range [{start:#x}, {extent[1]:#x})")
                instructions = image.decode(*extent)
                for ins in instructions:
                    print_instruction(ins)
                decoded_end = instructions[-1].address + instructions[-1].size if instructions else start
                print(f"Decoded through {decoded_end:#x} (exclusive)")
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
