import io
import pathlib
import os
import urllib.request

from atomicwrites import atomic_write as _backend_writer, AtomicWriter
from contextlib import contextmanager
from PIL import Image
from tempfile import TemporaryDirectory


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


def atomic_directory(array, fileglob, directory, ntimes):
    """
    atomically writes images to directory only if all images are written
    :param array: array of images objects
    :param fileglob: naming pattern to save each image to
    :param directory: name of directory to create and write to
    :param ntimes: number of images to save
    :return: None
    """

    # checks if directory already exists
    if not os.path.exists(directory):
        with TemporaryDirectory() as tmp:

            # create temp dir to rename later
            os.mkdir(tmp + "/t")
            for n in range(ntimes):

                # create file name to save image to
                file_name = fileglob.replace("*", str(n))
                temp_name = tmp + "/t/" + file_name
                with atomic_write(temp_name, overwrite=True) as f:

                    # opens and saves image to temp file
                    request = urllib.request.urlopen(array[n]).read()
                    img = io.BytesIO(request)
                    image = Image.open(img)

                    # scale down image
                    image.thumbnail((100, 100), Image.LANCZOS)
                    image.save(f)

                # check if number of files are correct and last file exists, then renames directory
                if (
                    os.path.exists(tmp + "/t/" + fileglob.replace("*", str(ntimes - 1)))
                    and len(
                        [
                            name
                            for name in os.listdir(tmp + "/t/")
                            if os.path.isfile(tmp + "/t/" + name)
                        ]
                    )
                    == ntimes
                ):
                    os.rename(tmp + "/t", directory)
    else:
        raise FileExistsError("File already exists!!!")
