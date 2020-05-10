from atomicwrites import atomic_write as _backend_writer, AtomicWriter
import pathlib
from contextlib import contextmanager


class SuffixWriter(AtomicWriter):
    """Similar to AtomicWriter but the temp file will have
    the exact same extension(s) as the target file"""

    def __init__(self, path, **open_kwargs):
        super().__init__(path, **open_kwargs)

        # extracts extension (even multiple extensions) from target
        list_extension = pathlib.Path(self._path).suffixes
        self.extension = "".join(list_extension)


    def get_fileobject(self, **kwargs):
        """Return the temporary file with correct extension(s) to use"""

        # change suffix to take the extracted extension(s)
        suffix = self.extension
        return super().get_fileobject(suffix=suffix, **kwargs)


# change ability to yield either file path or file
# set default writer_cls to our new SuffixWriter
@contextmanager
def atomic_write(file, mode="w", as_file=True, new_default="asdf", **kwargs):

    with _backend_writer(file, mode=mode, writer_cls=SuffixWriter, **kwargs) as f:

        # yield file 'f' if as_file=True, otherwise yields filepath 'file'
        if as_file:
            yield f
        else:
            yield f.name