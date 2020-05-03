import pandas as pd
import numpy as np
import os

from luigi import Parameter, Task, LocalTarget
from tempfile import TemporaryDirectory

from scrapper.posts import Posts

class ScrapePosts(Task):
    """"""

    LOCAL_ROOT = os.path.abspath("data")

    target = Parameter(default="#tag")
    number = Parameter(default="9")
    user = Parameter(default=None)
    password = Parameter(default=None)

    def output(self):
        return LocalTarget(self.LOCAL_ROOT +"/%s_posts.csv" % self.target)

    def run(self):
        n = int(self.number)
        posts = Posts(self.target, n, self.user, self.password)
        df = posts.df

        with self.output().temporary_path() as temp_output_path:

            with TemporaryDirectory() as tmp:
                os.mkdir(tmp+'/t')
                number = range(self.number)
                for n in number:
                    file_name = tmp +"/t/picture" +str(n)+".jpg"
                    df['image'][n].save(file_name)
                if os.path.exists(tmp + "/t/picture" +str(self.number-1)+".jpg"):
                    os.rename(tmp+"/t", self.LOCAL_ROOT + "/images")

            if os.path.exists(self.LOCAL_ROOT + "/images" + "/picture" +str(self.number-1)+".jpg"):
                df['image'] = df['image'].apply(np.array)
                df.to_csv(temp_output_path, index=False)

