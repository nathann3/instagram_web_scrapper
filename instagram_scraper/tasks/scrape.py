import io
import pandas as pd
import numpy as np
import os
import urllib.request

from luigi import Parameter, Task, LocalTarget
from PIL import Image
from tempfile import TemporaryDirectory

from instagram_scraper.scraper.io import atomic_write
from instagram_scraper.scraper.posts import Posts, Users


class ScrapeUsers(Task):
    LOCAL_ROOT = os.path.abspath("data")

    target = Parameter(default="maple.cat")
    user = Parameter(default=None)
    password = Parameter(default=None)
    format = Parameter(default="parquet")

    def output(self):
        return LocalTarget(self.LOCAL_ROOT +"/users.{}".format(self.format.lower()))

    def run(self):
        target = list(self.target)
        users = Users(target)
        df = users.df

        with self.output().temporary_path() as temp_output_path:
            if self.format.lower() == "parquet":
                df.to_parquet(temp_output_path, index=False)

            elif self.format.lower() == "csv":
                df.to_csv(temp_output_path, index=False)

            else:
                raise ValueError("output should be parquet or csv")


class ScrapePosts(Task):
    """"""

    LOCAL_ROOT = os.path.abspath("data")

    target = Parameter(default="#tag")
    number = Parameter(default="9")
    user = Parameter(default=None)
    password = Parameter(default=None)
    format = Parameter(default="parquet")

    def output(self):
        return LocalTarget(self.LOCAL_ROOT +"/{}_posts.{}".format(self.target, self.format.lower()))

    def run(self):
        n = int(self.number)

        posts = Posts(self.target, n, self.user, self.password)
        df = posts.df
        with self.output().temporary_path() as temp_output_path:

            df['image'] = df['image'].apply(np.asarray)

            if self.format.lower() == "parquet":
                df['image'] = df['image'].apply(lambda x: x.tolist())
                df.to_parquet(temp_output_path, index=False)

            elif self.format.lower() == "csv":
                df.to_csv(temp_output_path, index=False)

            else:
                raise ValueError("output should be parquet or csv")

class DownloadImages(Task):
    """"""

    LOCAL_ROOT = os.path.abspath("data")

    target = Parameter(default="#tag")
    number = Parameter(default="9")
    user = Parameter(default=None)
    password = Parameter(default=None)
    format = Parameter(default="parquet")

    def requires(self):
        return ScrapePosts(self.target, self.number, self.user, self.password, self.format)

    def output(self):
        return LocalTarget(self.LOCAL_ROOT +"/{}_images/".format(self.target))

    def run(self):
        n = int(self.number)
        output_directory = self.LOCAL_ROOT + "/" + self.target + "_images"
        df = pd.read_csv(self.input().path)
        atomic_directory(df['image_url'], "picture_*.jpg", output_directory, n)




def atomic_directory(array, fileglob, directory, ntimes):
    if not os.path.exists(directory):
        with TemporaryDirectory() as tmp:
            os.mkdir(tmp+'/t')
            for n in range(ntimes):
                file_name = fileglob.replace('*', str(n))
                temp_name = tmp + "/t/" + file_name
                with atomic_write(temp_name, overwrite=True) as f:
                    request = urllib.request.urlopen(array[n]).read()
                    img = io.BytesIO(request)
                    image = Image.open(img)
                    image.thumbnail((100, 100), Image.LANCZOS)
                    image.save(f)

                if (
                        os.path.exists(tmp + "/t/" + fileglob.replace("*", str(ntimes - 1)))
                        and len([name for name in os.listdir(tmp + "/t/") if os.path.isfile(tmp+"/t/"+name)])
                        == ntimes
                ):
                    os.rename(tmp + "/t", directory)
    else:
        raise FileExistsError("File already exists!!!")
