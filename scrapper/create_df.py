import pandas as pd


class Create_DataFrame:

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, '_' + self.name)

    def __set__(self, instance, value):
        val = self.create_df(value)
        return setattr(instance, '_' + self.name, val)

    def __set_name__(self, owner, name):
        self.name = name

    def create_df(self, dict):
        data = {
            "post_url": self.post_urls,
            "image": self.get_image(dict['image_urls']),
            "image_url": dict['image_urls'],
            "username": dict['username'],
            "picture_caption": dict['caption'],
            "picture_likes": dict['likes'],
            "datetime_posted": dict['time'],
        }
        df = pd.DataFrame(data)
        df["datetime_posted"] = pd.to_datetime(df["datetime_posted"])
        df['hashtags'] = df['picture_caption'].str.findall(r"#\w+")
        return df