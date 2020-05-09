import argparse

from luigi import build

from .tasks.stylize import Stylize

parser = argparse.ArgumentParser(description='Style picture with pre-trained model')
parser.add_argument("-i", "--image", default='luigi.jpg')
parser.add_argument("-m", "--model", default='rain_princess.pth')
parser.add_argument("-s", "--scale", default='2')



def main(args=None):
    """Runs the luigi Scrape task given args"""
    args = parser.parse_args()
    build([
        Stylize(
            image=args.image,
            model=args.model,
            scale=args.scale
        )], local_scheduler=True)