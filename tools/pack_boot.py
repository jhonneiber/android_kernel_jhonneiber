#!/usr/bin/env python3
"""
Infinix Hot 30 (X6831) Boot Image Packer (Android Boot Image v2)
100% Accurate Header Calculation & Binary Layout
"""
import argparse
import hashlib
import os
import struct
import sys

def pad_to_page(data, page_size):
    rem = len(data) % page_size
    if rem != 0:
        return data + b"\x00" * (page_size - rem)
    return data

def compute_boot_id(kernel, ramdisk, dtb):
    h = hashlib.sha1()
    h.update(kernel)
    h.update(struct.pack("<I", len(kernel)))
    h.update(ramdisk)
    h.update(struct.pack("<I", len(ramdisk)))
    h.update(b"")
    h.update(struct.pack("<I", 0)) # second
    h.update(b"")
    h.update(struct.pack("<I", 0)) # recovery dtbo
    h.update(dtb)
    h.update(struct.pack("<I", len(dtb)))
    digest = h.digest()
    return digest.ljust(32, b"\x00")

def pack_boot(kernel_path, ramdisk_path, dtb_path, output_path, pad_to_partition=False):
    page_size = 2048
    header_version = 2
    kernel_addr = 0x40080000
    ramdisk_addr = 0x47c80000
    second_addr = 0
    tags_addr = 0x4bc80000
    dtb_addr = 0x4bc80000
    os_version = 402653574 # Android 12/13 (2024-06)
    cmdline = b"bootopt=64S3,32N2,64N2 buildvariant=user"

    with open(kernel_path, "rb") as f:
        kernel_data = f.read()
    with open(ramdisk_path, "rb") as f:
        ramdisk_data = f.read()
    with open(dtb_path, "rb") as f:
        dtb_data = f.read()

    kernel_size = len(kernel_data)
    ramdisk_size = len(ramdisk_data)
    dtb_size = len(dtb_data)
    second_size = 0
    recovery_dtbo_size = 0
    recovery_dtbo_offset = 0
    header_size = 1660

    # Build 1660-byte v2 header
    hdr = bytearray(1660)
    # Magic (8)
    hdr[0:8] = b"ANDROID!"
    # Sizes & Addrs (32)
    struct.pack_into("<IIIIIIII", hdr, 8, kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size, second_addr, tags_addr, page_size)
    # Header version (4), OS version (4)
    struct.pack_into("<II", hdr, 40, header_version, os_version)
    name = b"CY-X6831-V7520"
    hdr[48:48+len(name)] = name
    # Cmdline (512 bytes at offset 64)
    hdr[64:64+len(cmdline)] = cmdline
    # ID (32 bytes at offset 576)
    hdr[576:608] = compute_boot_id(kernel_data, ramdisk_data, dtb_data)
    # Extra cmdline (1024 bytes at offset 608)
    # Recovery dtbo size (4), offset (8), header_size (4) at offset 1632
    struct.pack_into("<IQI", hdr, 1632, recovery_dtbo_size, recovery_dtbo_offset, header_size)
    # DTB size (4), DTB addr (8) at offset 1648
    struct.pack_into("<IQ", hdr, 1648, dtb_size, dtb_addr)

    header_page = bytearray(page_size)
    header_page[:1660] = hdr

    out = bytearray()
    out.extend(header_page)
    out.extend(pad_to_page(kernel_data, page_size))
    out.extend(pad_to_page(ramdisk_data, page_size))
    out.extend(pad_to_page(dtb_data, page_size))

    if pad_to_partition:
        target_size = 33554432 # 32 MB
        if len(out) < target_size:
            out.extend(b"\x00" * (target_size - len(out)))

    with open(output_path, "wb") as f:
        f.write(out)

    print(f"[+] Boot image created successfully: {output_path}")
    print(f"    Total size: {len(out)} bytes ({len(out)/(1024*1024):.2f} MB)")
    print(f"    Kernel size: {kernel_size} bytes")
    print(f"    Ramdisk size: {ramdisk_size} bytes")
    print(f"    DTB size: {dtb_size} bytes")
    print(f"    Calculated SHA1 ID: {hdr[576:596].hex()}")

def main():
    parser = argparse.ArgumentParser(description="Pack Infinix Hot 30 (X6831) boot.img")
    parser.add_argument("--kernel", required=True, help="Path to kernel (Image.gz)")
    parser.add_argument("--ramdisk", required=True, help="Path to ramdisk.img")
    parser.add_argument("--dtb", required=True, help="Path to boot.dtb")
    parser.add_argument("--output", required=True, help="Output boot.img path")
    parser.add_argument("--pad-32mb", action="store_true", help="Pad image to 32MB partition size")
    args = parser.parse_args()
    pack_boot(args.kernel, args.ramdisk, args.dtb, args.output, pad_to_partition=args.pad_32mb)

if __name__ == "__main__":
    main()
