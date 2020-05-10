import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="instagram_web_scraper",
    version="0.1.0",
    packages=setuptools.find_packages(),
    install_requires=[
        "pandas",
        "ipython",
        "selenium",
        "pillow",
        "luigi",
        "pyarrow",
        "atomicwrites",
    ]
)
