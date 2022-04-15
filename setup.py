import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vk_common",
    version="0.0.4",
    author="Bradul Dmitriy",
    author_email="dbradul@gmail.com",
    description="VK Common tools for VK-API lib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dbradul/vk_common",
    install_requires=["vk-api", "requests", "pydantic", "python-dotenv"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)