import base64
import pandas as pd

from IPython.display import HTML
from io import BytesIO


def image_formatter(im):
    """Helper class to input image into HTML img tag"""
    return f'<img src="data:image/jpeg;base64,{image_base64(im)}">'


def image_base64(im):
    """Helper class to convert image objects as base64"""
    if isinstance(im, str):
        im = get_thumbnail(im)
    with BytesIO() as buffer:
        im.save(buffer, "jpeg")
        return base64.b64encode(buffer.getvalue()).decode()


class Create_DataFrame:
    """Descriptor class that handles creation of Dataframes with given Instagram info"""

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, "_" + self.name)

    def __set__(self, instance, value):
        vals = self.create_df(value)
        setattr(instance, "_" + self.name, vals["df"])
        setattr(instance, "html_df", vals["html_df"])

    def __set_name__(self, owner, name):
        self.name = name

    def create_df(self, dict):
        data = dict
        df = pd.DataFrame(data)

        if "datetime_posted" in df.columns:
            df["datetime_posted"] = pd.to_datetime(df["datetime_posted"])

        # extracts hashtags from captions
        if "caption" in df.columns:
            df["hashtags"] = df["caption"].str.findall(r"#\w+")

        # create dataframe with images inline
        html_df = HTML(df.to_html(formatters={"image": image_formatter}, escape=False))

        return {"df": df, "html_df": html_df}
