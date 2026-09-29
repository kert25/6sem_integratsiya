import struct, sys, glob, os
d = sys.argv[1]
for f in sorted(glob.glob(os.path.join(d, "*.png"))):
    with open(f, "rb") as fh:
        data = fh.read(24)
    ok = data[:8] == b"\x89PNG\r\n\x1a\n"
    w, h = struct.unpack(">II", data[16:24]) if ok else (0, 0)
    print("%-32s %7d b  %dx%d  %s" % (os.path.basename(f), os.path.getsize(f), w, h, "OK" if ok else "BAD"))
