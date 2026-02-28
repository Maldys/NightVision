#!/usr/bin/env python3
import os
import time
import mmap
import struct
import fcntl
from PIL import Image

FLAG_FILE = "/run/nightvision_ready"

FBIOGET_VSCREENINFO = 0x4600
FBIOGET_FSCREENINFO = 0x4602

def fb_get_var(fd):
    # struct fb_var_screeninfo is ~160 bytes on arm/linux; read plenty
    buf = bytearray(160)
    fcntl.ioctl(fd, FBIOGET_VSCREENINFO, buf, True)

    # xres, yres, xres_virtual, yres_virtual, xoffset, yoffset, bits_per_pixel
    xres, yres, _, _, _, _, bpp = struct.unpack_from("<7I", buf, 0)
    return xres, yres, bpp

def fb_get_line_length(fd):
    # fb_fix_screeninfo is larger; read more than 64 to be safe
    buf = bytearray(128)
    fcntl.ioctl(fd, FBIOGET_FSCREENINFO, buf, True)

    # In Linux fb_fix_screeninfo, line_length is a 32-bit field after:
    # id[16], smem_start (ulong), smem_len (u32), type(u32), type_aux(u32),
    # visual(u32), xpanstep(u16), ypanstep(u16), ywrapstep(u16), padding(u16),
    # line_length(u32)  -> common offset 44
    line_length = struct.unpack_from("<I", buf, 44)[0]
    return line_length

def rgba_to_rgb565_bytes(img_rgba: Image.Image) -> bytes:
    """Convert RGBA -> RGB565 little-endian, alpha blended on black."""
    img = img_rgba.convert("RGBA")
    # Alpha blend to black: (rgb * a) / 255
    r, g, b, a = img.split()
    r = r.point(lambda x: x)
    g = g.point(lambda x: x)
    b = b.point(lambda x: x)

    # Convert to raw bytes for speed
    rp = r.tobytes()
    gp = g.tobytes()
    bp = b.tobytes()
    ap = a.tobytes()

    out = bytearray(img.width * img.height * 2)
    o = 0
    for i in range(img.width * img.height):
        alpha = ap[i]
        # blend with black => scale by alpha
        rr = (rp[i] * alpha) // 255
        gg = (gp[i] * alpha) // 255
        bb = (bp[i] * alpha) // 255

        v = ((rr & 0xF8) << 8) | ((gg & 0xFC) << 3) | (bb >> 3)
        out[o] = v & 0xFF
        out[o + 1] = (v >> 8) & 0xFF
        o += 2
    return bytes(out)

def rgba_to_bgr24_bytes(img_rgba: Image.Image) -> bytes:
    """RGBA -> BGR24, alpha blended on black."""
    img = img_rgba.convert("RGBA")
    r, g, b, a = img.split()
    rp, gp, bp, ap = r.tobytes(), g.tobytes(), b.tobytes(), a.tobytes()

    out = bytearray(img.width * img.height * 3)
    o = 0
    for i in range(img.width * img.height):
        alpha = ap[i]
        rr = (rp[i] * alpha) // 255
        gg = (gp[i] * alpha) // 255
        bb = (bp[i] * alpha) // 255
        out[o] = bb
        out[o + 1] = gg
        out[o + 2] = rr
        o += 3
    return bytes(out)

def rgba_to_bgra32_bytes(img_rgba: Image.Image) -> bytes:
    """RGBA -> BGRA32 (little endian), alpha blended on black, A set to 255."""
    img = img_rgba.convert("RGBA")
    r, g, b, a = img.split()
    rp, gp, bp, ap = r.tobytes(), g.tobytes(), b.tobytes(), a.tobytes()

    out = bytearray(img.width * img.height * 4)
    o = 0
    for i in range(img.width * img.height):
        alpha = ap[i]
        rr = (rp[i] * alpha) // 255
        gg = (gp[i] * alpha) // 255
        bb = (bp[i] * alpha) // 255
        out[o] = bb
        out[o + 1] = gg
        out[o + 2] = rr
        out[o + 3] = 255
        o += 4
    return bytes(out)

def write_to_fb(fb, w, h, bpp, line_length, img_rgba: Image.Image):
    if bpp == 16:
        pixel_bytes = 2
        raw = rgba_to_rgb565_bytes(img_rgba)
    elif bpp == 24:
        pixel_bytes = 3
        raw = rgba_to_bgr24_bytes(img_rgba)
    elif bpp == 32:
        pixel_bytes = 4
        raw = rgba_to_bgra32_bytes(img_rgba)
    else:
        raise RuntimeError(f"Unsupported framebuffer bpp={bpp}. Expected 16/24/32.")

    expected_row = w * pixel_bytes
    raw_row_stride = expected_row

    # Write row-by-row respecting framebuffer line_length
    for y in range(h):
        src_off = y * raw_row_stride
        row = raw[src_off:src_off + expected_row]
        dst_off = y * line_length
        fb[dst_off:dst_off + expected_row] = row

def main():
    fb_path = "/dev/fb0"
    img1_path = "/home/malda/NightVision/src/img/logo_wht.png"
    img2_path = "/home/malda/NightVision/src/img/logo_red.png"
    

    # (Volitelné) pro debug: uvidíš v journalctl
    print("[fb_show] starting")

    fd = os.open(fb_path, os.O_RDWR)
    try:
        w, h, bpp = fb_get_var(fd)
        line_length = fb_get_line_length(fd)
        fb_size = line_length * h

        print(f"[fb_show] fb={fb_path} {w}x{h} bpp={bpp} line_length={line_length} fb_size={fb_size}")

        fb = mmap.mmap(fd, fb_size, mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ)
        try:
            img = Image.open(img1_path).convert("RGBA")

            # Přesně na framebuffer (rychlé a deterministické)
            img = img.resize((w, h), Image.NEAREST)

            write_to_fb(fb, w, h, bpp, line_length, img)
            fb.flush()
            print("[fb_show] image drawn")

            # čekání na flag
            while not os.path.exists(FLAG_FILE):
                time.sleep(0.05)

            print("[fb_show] flag detected, exiting")
        finally:
            try:
                img = Image.open(img2_path).convert("RGBA")

                # Přesně na framebuffer (rychlé a deterministické)
                img = img.resize((w, h), Image.NEAREST)

                write_to_fb(fb, w, h, bpp, line_length, img)
                fb.flush()
                print("[fb_show] image drawn")

                # čekání na flag
                while not os.path.exists(FLAG_FILE):
                    time.sleep(0.05)

                print("[fb_show] flag detected, exiting")
            finally:
                fb.close()
    finally:
        os.close(fd)

if __name__ == "__main__":
    main()
