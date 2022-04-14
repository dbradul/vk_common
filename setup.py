import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vk_common",
    version="0.0.1",
    author="Bradul Dmitriy",
    author_email="dbradul@gmail.com",
    description="VK Common tools for VK-API lib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dbradul/vk_common",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)