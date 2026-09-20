"""Fetch a single member out of the remote SWORD zip on Zenodo without
downloading the whole 3.9 GB archive.

Zenodo serves HTTP Range requests, so we read the zip central directory,
locate the member's compressed byte span, pull it with N parallel range
requests, and inflate the raw deflate stream to disk.
"""
import argparse, io, os, struct, sys, zlib
from concurrent.futures import ThreadPoolExecutor

import requests
from remotezip import RemoteZip

URL = ("https://zenodo.org/records/22259077/files/"
       "SWORD_v17c_netcdf.zip?download=1")


def data_offset(url, info):
    """Local file headers carry their own name/extra lengths; the member's
    compressed bytes start after them, not at info.header_offset."""
    r = requests.get(url, headers={"Range": f"bytes={info.header_offset}-{info.header_offset + 29}"},
                     timeout=60)
    r.raise_for_status()
    sig, _, _, _, _, _, _, _, _, n_len, e_len = struct.unpack("<IHHHHHIIIHH", r.content[:30])
    assert sig == 0x04034b50, f"bad local header signature {sig:#x}"
    return info.header_offset + 30 + n_len + e_len


def fetch_chunk(args):
    url, start, end, idx = args
    for attempt in range(5):
        try:
            r = requests.get(url, headers={"Range": f"bytes={start}-{end}"}, timeout=300)
            r.raise_for_status()
            got = len(r.content)
            if got != end - start + 1:
                raise IOError(f"short read {got} != {end - start + 1}")
            return idx, r.content
        except Exception as e:
            if attempt == 4:
                raise
            print(f"  chunk {idx} retry {attempt + 1}: {e}", file=sys.stderr)
    raise RuntimeError("unreachable")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--member", default="netcdf/na_sword_v17c.nc")
    p.add_argument("--out", required=True)
    p.add_argument("--url", default=URL)
    p.add_argument("--workers", type=int, default=8)
    a = p.parse_args()

    with RemoteZip(a.url) as z:
        info = z.getinfo(a.member)
    print(f"{a.member}: {info.file_size/1e6:.1f} MB raw, "
          f"{info.compress_size/1e6:.1f} MB compressed, method {info.compress_type}")

    start = data_offset(a.url, info)
    end = start + info.compress_size - 1
    n = a.workers
    step = (info.compress_size + n - 1) // n
    jobs = []
    for i in range(n):
        s = start + i * step
        e = min(s + step - 1, end)
        if s <= e:
            jobs.append((a.url, s, e, i))

    print(f"pulling {len(jobs)} ranges with {n} workers ...")
    parts = [None] * len(jobs)
    with ThreadPoolExecutor(max_workers=n) as ex:
        for idx, buf in ex.map(fetch_chunk, jobs):
            parts[idx] = buf
            print(f"  chunk {idx} done ({len(buf)/1e6:.1f} MB)", flush=True)

    raw = b"".join(parts)
    assert len(raw) == info.compress_size, f"{len(raw)} != {info.compress_size}"

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    if info.compress_type == 0:                       # stored
        with open(a.out, "wb") as f:
            f.write(raw)
    else:                                              # raw deflate
        d = zlib.decompressobj(-zlib.MAX_WBITS)
        with open(a.out, "wb") as f:
            for i in range(0, len(raw), 1 << 22):
                f.write(d.decompress(raw[i:i + (1 << 22)]))
            f.write(d.flush())

    size = os.path.getsize(a.out)
    assert size == info.file_size, f"inflated {size} != expected {info.file_size}"
    print(f"wrote {a.out} ({size/1e6:.1f} MB) -- size matches central directory")


if __name__ == "__main__":
    main()
