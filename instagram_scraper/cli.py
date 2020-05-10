import argparse

from luigi import build

from instagram_scraper.tasks.scrape import DownloadImages, ScrapeUsers

parser = argparse.ArgumentParser(description='Download Instagram posts and users')
parser.add_argument("--posts", default='ralphthecorgi')
parser.add_argument('--users', nargs='+')
parser.add_argument("-n", "--number", default='9')
parser.add_argument("-u", "--username")
parser.add_argument("-p", "--password")
parser.add_argument("-f", "--format", default='parquet')


def main(args=None):
    """Runs the luigi ScrapePosts task given args"""
    args = parser.parse_args()
    if args.users:
        build([
            ScrapeUsers(
                target=args.users,
                user=args.username,
                password=args.password,
                format=args.format
            )], local_scheduler=True)

    else:
        build([
            DownloadImages(
                target=args.posts,
                number=args.number,
                user=args.username,
                password=args.password,
                format=args.format
            )], local_scheduler=True)
