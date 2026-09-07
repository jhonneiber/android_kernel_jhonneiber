#!/bin/bash
set -e

export ARCH=arm64
export SUBARCH=arm64
export HEADER_ARCH=arm64

# Default clang toolchain configuration
export CC=${CC:-clang}
export LD=${LD:-ld.lld}
export AR=${AR:-llvm-ar}
export NM=${NM:-llvm-nm}
export OBJCOPY=${OBJCOPY:-llvm-objcopy}
export OBJDUMP=${OBJDUMP:-llvm-objdump}
export STRIP=${STRIP:-llvm-strip}
export CROSS_COMPILE=${CROSS_COMPILE:-aarch64-linux-gnu-}
export CROSS_COMPILE_COMPAT=${CROSS_COMPILE_COMPAT:-arm-linux-gnueabi-}

DEFCONFIG="infinix_x6831_defconfig"
OUT_DIR="${OUT_DIR:-out}"

echo "=========================================================="
echo " Building Kernel Port: Infinix Hot 30 (X6831)"
echo " Base: Xiaomi Redmi 12 (fire-t-oss) Linux 4.19.191"
echo " Target Config: ${DEFCONFIG}"
echo " Out Dir:       ${OUT_DIR}"
echo "=========================================================="

mkdir -p "${OUT_DIR}"

echo "[*] Step 1: Generating .config from ${DEFCONFIG}..."
make O="${OUT_DIR}" ARCH=arm64 "${DEFCONFIG}"
make O="${OUT_DIR}" ARCH=arm64 olddefconfig

echo "[*] Step 2: Compiling Kernel (Image.gz)..."
make -j"$(nproc 2>/dev/null || echo 4)" O="${OUT_DIR}"     ARCH=arm64     CC="${CC}"     LD="${LD}"     AR="${AR}"     NM="${NM}"     OBJCOPY="${OBJCOPY}"     OBJDUMP="${OBJDUMP}"     STRIP="${STRIP}"     CROSS_COMPILE="${CROSS_COMPILE}"     CROSS_COMPILE_COMPAT="${CROSS_COMPILE_COMPAT}"     Image.gz

if [ -f "${OUT_DIR}/arch/arm64/boot/Image.gz" ]; then
    echo "=========================================================="
    echo " [+] Kernel compilation successful!"
    echo "     Output: ${OUT_DIR}/arch/arm64/boot/Image.gz"
    echo "=========================================================="
else
    echo "[-] Build failed: Image.gz not found!"
    exit 1
fi
