import numpy as np
import os
import pandas as pd

from luigi import Parameter, Task, LocalTarget

from instagram_scraper.scraper.io import atomic_directory
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
