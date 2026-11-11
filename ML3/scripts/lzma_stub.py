"""Stub out the missing `lzma` stdlib module so torchvision can be imported.

This Python distribution (bundled with LibreOffice) was built without the
optional `_lzma` C extension. torchvision only touches `lzma` for a couple of
rarely-used dataset download helpers we never call, so a dummy module that
raises if actually used is sufficient to unblock the import.
"""
import sys
import types


def install():
    if "lzma" in sys.modules and getattr(sys.modules["lzma"], "_is_stub", False):
        return
    try:
        import lzma  # noqa: F401
        return  # real lzma works, nothing to do
    except ModuleNotFoundError:
        pass

    fake = types.ModuleType("lzma")
    fake._is_stub = True

    def _stub(*a, **k):
        raise NotImplementedError("lzma is not available in this environment")

    class _FakeLZMAFile:
        def __init__(self, *a, **k):
            raise NotImplementedError("lzma is not available in this environment")
        def read(self, *a, **k): raise NotImplementedError
        def write(self, *a, **k): raise NotImplementedError
        def seek(self, *a, **k): raise NotImplementedError
        def tell(self, *a, **k): raise NotImplementedError

    for name in [
        "open", "compress", "decompress", "LZMACompressor",
        "LZMADecompressor", "FORMAT_XZ", "FORMAT_ALONE", "FORMAT_RAW",
        "CHECK_NONE", "CHECK_CRC32", "CHECK_CRC64", "CHECK_SHA256",
        "CHECK_UNKNOWN", "PRESET_DEFAULT", "PRESET_EXTREME",
        "FILTER_LZMA1", "FILTER_LZMA2",
    ]:
        setattr(fake, name, _stub)
    fake.LZMAFile = _FakeLZMAFile
    fake.LZMAError = type("LZMAError", (Exception,), {})
    sys.modules["lzma"] = fake
