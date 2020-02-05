import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ProtocolAssessment",
    version="1.0.0",
    author="Sumanth Tirumale",
    author_email="sumanth902@gmail.com",
    description="Protocol Assessment is a packet manipulation framework.",
    long_description=long_description,
    # long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['scapy==2.4.3'],
    include_package_data=True,
)
