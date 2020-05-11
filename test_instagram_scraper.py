import os
import pathlib
import unittest
import numpy as np
import pandas as pd

from PIL import UnidentifiedImageError
from unittest import TestCase
from luigi.mock import MockTarget
from luigi.worker import Worker
from tempfile import TemporaryDirectory
from luigi import LocalTarget

from instagram_scraper.scraper.posts import Posts, Users
from instagram_scraper.scraper.io import atomic_write, atomic_directory
from instagram_scraper.tasks.scrape import ScrapePosts, ScrapeUsers


class FakeFileFailure(IOError):
    pass


def run_task(task):
    """runs luigi tasks"""
    worker = Worker()
    worker.add(task)
    worker.run()


class TaskTests(TestCase):
    def test_users(self):
        """Ensure if task can scrape user account information"""
        with TemporaryDirectory() as tmp:
            mock_output = LocalTarget(tmp + "/test_file")

            class MockScrapeUsers(ScrapeUsers):
                """mock ScrapeUsers with a mock target"""

                def output(self):
                    return mock_output

            run_task(MockScrapeUsers(target=["cscie29"], format="csv"))

            # check if output exists
            self.assertTrue(mock_output.exists())

            df = pd.read_csv(mock_output.path)

            # check if csv is written correctly
            self.assertEqual(df["user"][0], "cscie29")

    def test_posts(self):
        """Ensure if task can scrape post information"""

        with TemporaryDirectory() as tmp:
            mock_output = LocalTarget(tmp + "/test_file")

            class MockScrapePosts(ScrapePosts):
                """mock ScrapePosts with a mock target"""

                def output(self):
                    return mock_output

            run_task(MockScrapePosts(target="cscie29", number=1, format="csv"))

            # check if output exists
            self.assertTrue(mock_output.exists())

            df = pd.read_csv(mock_output.path)

            # check if csv is written correctly
            self.assertEqual(
                df["post_url"][0], "https://www.instagram.com/p/CABs82Pjqpi/"
            )


class PostsTests(TestCase):
    def test_scrape(self):
        """Ensure information is correctly scraped from post and attributes are created"""
        post = Posts("cscie29", 1)
        self.assertEqual(post.caption[0], "this is a caption")
        self.assertEqual(post.post_url[0], "https://www.instagram.com/p/CABs82Pjqpi/")

        # check dataframe creation
        self.assertEqual(post.df.columns[-1], "hashtags")


class UsersTests(TestCase):
    def test_scrape(self):
        """Ensure information is correctly scraped from user account and attributes are created"""
        user = Users("cscie29")
        self.assertEqual(user.following[0], "2")
        self.assertEqual(user.posts[0], "1")

        # check dataframe creation
        self.assertEqual(user.df.columns[-1], "following")


#
class AtomicWriteTests(TestCase):
    def test_atomic_write(self):
        """Ensure file exists after being written successfully"""

        with TemporaryDirectory() as tmp:
            fp = os.path.join(tmp, "asdf.txt")

            with atomic_write(fp, "w") as f:
                assert not os.path.exists(fp)
                tmpfile = f.name
                f.write("asdf")

            assert not os.path.exists(tmpfile)
            assert os.path.exists(fp)

            with open(fp) as f:
                self.assertEqual(f.read(), "asdf")

    def test_same_file(self):
        """Ensure when code fails, new temp file is not the same temp file"""

        with TemporaryDirectory() as tmp:
            fp = os.path.join(tmp, "asdf.txt")

            with self.assertRaises(FakeFileFailure):
                with atomic_write(fp, "w") as f:
                    old_name = f.name
                    raise FakeFileFailure()

                with atomic_write(fp, "w") as f:
                    new_name = f.name
                    pass

                assert not old_name == new_name

    def test_file_extension(self):
        """Ensure temp file extension is same as target"""

        with TemporaryDirectory() as tmp:
            fp = os.path.join(tmp, "asdf.tar.gz")

            with atomic_write(fp, "w") as f:
                assert pathlib.Path(f.name).suffixes == pathlib.Path(fp).suffixes


class AtomicDirectoriesTest(TestCase):
    def test_write(self):
        """Ensure that directory is created"""
        with TemporaryDirectory() as tmp:
            images_path = os.path.join(tmp, "images")
            fp = os.path.join(images_path, "picture_0.jpg")
            url = "https://scontent-sjc3-1.cdninstagram.com/v/t51.2885-15/e35/96213616_1357060731156136_5737633214514504373_n.jpg?_nc_ht=scontent-sjc3-1.cdninstagram.com&_nc_cat=104&_nc_ohc=XLsKXQBv0cIAX_wg9vu&oh=75a909bc7b847bb20fb0361d552196ee&oe=5EE31C98"
            test_array = np.array([url])
            atomic_directory(test_array, "picture_*.jpg", images_path, 1)
            self.assertTrue(os.path.exists(fp))

    def test_failure(self):
        """Ensure that images are not saved when one image isn't saved"""
        with TemporaryDirectory() as tmp:
            images_path = os.path.join(tmp, "images")
            fp = os.path.join(images_path, "picture_0.jpg")
            pic1 = "https://scontent-sjc3-1.cdninstagram.com/v/t51.2885-15/e35/96213616_1357060731156136_5737633214514504373_n.jpg?_nc_ht=scontent-sjc3-1.cdninstagram.com&_nc_cat=104&_nc_ohc=XLsKXQBv0cIAX_wg9vu&oh=75a909bc7b847bb20fb0361d552196ee&oe=5EE31C98"
            pic2 = "https://www.google.com"
            test_array = np.array([pic1, pic2])
            try:
                atomic_directory(test_array, "picture_*.jpg", images_path, 2)
            except UnidentifiedImageError:
                pass

            # image should not exist since the second url is not an image
            self.assertFalse(os.path.exists(fp))


if __name__ == "__main__":
    unittest.main()
