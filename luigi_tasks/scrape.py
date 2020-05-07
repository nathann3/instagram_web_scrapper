import pandas as pd
import numpy as np
import os

from luigi import Parameter, Task, LocalTarget
from tempfile import TemporaryDirectory

from scrapper.io import atomic_write
from scrapper.posts import Posts

class ScrapePosts(Task):
    """"""

    LOCAL_ROOT = os.path.abspath("data")

    target = Parameter(default="#tag")
    number = Parameter(default="9")
    user = Parameter(default=None)
    password = Parameter(default=None)
    format = Parameter(default="parquet")

    def output(self):
        return LocalTarget(self.LOCAL_ROOT +"/{}_posts.{}".format(self.target, self.format))

    def run(self):
        n = int(self.number)
        posts = Posts(self.target, n, self.user, self.password)
        df = posts.df
        output_directory = self.LOCAL_ROOT + "/" + self.target + "_images"
        with self.output().temporary_path() as temp_output_path:

            atomic_directory(df['image'], "picture_*.jpg", output_directory, n)

            if os.path.exists(output_directory):
                df['image'] = df['image'].apply(np.array)

                if self.format.lower() == "parquet":
                    df['image'] = df['image'].apply(lambda x: x.tolist())
                    df.to_parquet(temp_output_path, index=False)

                elif self.format.lower() == "csv":
                    df.to_csv(temp_output_path, index=False)

                else:
                    raise ValueError("output should be parquet or csv")

def atomic_directory(array, fileglob, directory, ntimes):
    if not os.path.exists(directory):
        with TemporaryDirectory() as tmp:
            os.mkdir(tmp+'/t')
            for n in range(ntimes):
                file_name = fileglob.replace('*', str(n))
                temp_name = tmp + "/t/" + file_name
                with atomic_write(temp_name, overwrite=True) as f:
                    array[n].save(f)

                if (
                        os.path.exists(tmp + "/t/" + fileglob.replace("*", str(ntimes - 1)))
                        and len([name for name in os.listdir(tmp + "/t/") if os.path.isfile(tmp+"/t/"+name)])
                        == ntimes
                ):
                    os.rename(tmp + "/t", directory)
    else:
        raise FileExistsError("File already exists!!!")

