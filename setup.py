import setuptools

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
