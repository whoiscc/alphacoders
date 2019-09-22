import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="alphacoders",
    version="1.0.0",
    description="Download wallpapers from Alpha Coders",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/whoiscc/alphacoders",
    author="Correctizer",
    author_email="correctizer@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["alphacoders"],
    include_package_data=True,
    install_requires=["aiohttp", "lxml"],
    # entry_points={
    #     "console_scripts": [
    #         "realpython=reader.__main__:main",
    #     ]
    # },
)