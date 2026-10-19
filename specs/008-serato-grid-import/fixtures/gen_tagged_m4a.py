#!/usr/bin/env python3
"""Inyecta átomo freeform '----:com.serato.dj:beatgrid' en un .m4a (pruebas).

Uso: gen_tagged_m4a.py entrada.m4a salida.m4a
Crea la cadena moov/udta/meta/ilst si falta y actualiza tamaños ancestros.
Payload: mismo de gen_tagged_mp3.py (markers cada 0.5 s, terminal 120 BPM).
"""
import struct
import sys


def payload() -> bytes:
    body = b"".join(struct.pack(">fI", t, 1) for t in (0.0, 0.5, 1.0, 1.5))
    body += struct.pack(">ff", 2.0, 120.0)
    return b"\x01\x00" + struct.pack(">I", 5) + body


def atom(name: bytes, body: bytes) -> bytes:
    return struct.pack(">I", 8 + len(body)) + name + body


def freeform(mean: bytes, name: bytes, data: bytes) -> bytes:
    # Como Serato real: átomo data tipo 1 (texto) con base64 del contenido
    # GEOB (mime NUL filename-vacío NUL descriptor NUL payload).
    import base64
    geob = b"application/octet-stream\x00\x00Serato BeatGrid\x00" + payload()
    return atom(b"----", atom(b"mean", b"\x00\x00\x00\x00" + mean)
                + atom(b"name", b"\x00\x00\x00\x00" + name)
                + atom(b"data", struct.pack(">II", 1, 0)
                       + base64.b64encode(geob)))


def parse_atoms(buf: bytes, off: int, end: int):
    out = []
    while off + 8 <= end:
        size = struct.unpack(">I", buf[off:off + 4])[0]
        name = buf[off + 4:off + 8]
        if size == 0:
            size = end - off
        if size < 8:
            break
        out.append((name, off, off + size))
        off += size
    return out


def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    data = bytearray(open(src, "rb").read())
    top = parse_atoms(data, 0, len(data))
    moov = next((a for a in top if a[0] == b"moov"), None)
    assert moov, "sin moov"
    mo, m0, m1 = moov
    inner = parse_atoms(data, m0 + 8, m1)
    udta = next((a for a in inner if a[0] == b"udta"), None)

    ff = freeform(b"com.serato.dj", b"beatgrid", payload())
    if udta is None:
        ilst = atom(b"ilst", ff)
        meta = atom(b"meta", b"\x00\x00\x00\x00" + atom(b"hdlr",
            b"\x00\x00\x00\x00\x00mdirappl\x00" * 1) + ilst)
        # hdlr mínimo válido
        new_udta = atom(b"udta", meta)
        data[m1:m1] = new_udta
        for name, off, end in reversed(top):
            if name == b"moov":
                ns = struct.unpack(">I", data[off:off + 4])[0] + len(new_udta)
                data[off:off + 4] = struct.pack(">I", ns)
    else:
        u0, u1 = udta[1], udta[2]
        sub = parse_atoms(data, u0 + 8, u1)
        meta = next((a for a in sub if a[0] == b"meta"), None)
        if meta is None:
            new_meta = atom(b"meta", b"\x00\x00\x00\x00" + atom(b"ilst", ff))
            data[u1:u1] = new_meta
            for a in (udta, moov):
                ns = struct.unpack(">I", data[a[1]:a[1] + 4])[0] + len(new_meta)
                data[a[1]:a[1] + 4] = struct.pack(">I", ns)
        else:
            mta0, mta1 = meta[1], meta[2]
            # meta tiene 4 bytes de versión/flags antes de los hijos
            kids = parse_atoms(data, mta0 + 12, mta1)
            ilst = next((a for a in kids if a[0] == b"ilst"), None)
            if ilst is None:
                new_ilst = atom(b"ilst", ff)
                data[mta1:mta1] = new_ilst
                for a in (meta, udta, moov):
                    ns = struct.unpack(">I", data[a[1]:a[1] + 4])[0] + len(new_ilst)
                    data[a[1]:a[1] + 4] = struct.pack(">I", ns)
            else:
                i0, i1 = ilst[1], ilst[2]
                data[i1:i1] = ff
                for a in (ilst, meta, udta, moov):
                    ns = struct.unpack(">I", data[a[1]:a[1] + 4])[0] + len(ff)
                    data[a[1]:a[1] + 4] = struct.pack(">I", ns)
    open(dst, "wb").write(bytes(data))
    print("escrito", dst)


if __name__ == "__main__":
    main()
