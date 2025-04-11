from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="valluvarai",
    version="0.1.0",
    author="ValluvarAI Team",
    author_email="info@valluvarai.com",
    description="An AI-powered storytelling & literary companion for Tamil ethics, emotions, and culture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/valluvarai/valluvarai",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "valluvarai": ["kural_data/*.json"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "valluvarai-ui=valluvarai.ui.streamlit_app:main",
        ],
    },
)
