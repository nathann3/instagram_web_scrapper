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
        data = dict
        df = pd.DataFrame(data)
        if "image_likes" in df.columns:
            df["image_likes"] = df["image_likes"].apply(lambda x: int(x.replace(',', '')))

        if "datetime_posted" in df.columns:
            df["datetime_posted"] = pd.to_datetime(df["datetime_posted"])

        if 'image_caption' in df.columns:
            df['hashtags'] = df['image_caption'].str.findall(r"#\w+")
        return df