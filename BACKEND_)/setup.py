"""
Setup file for the rule-based chatbot package.
"""
from setuptools import setup, find_packages

setup(
    name="rule_based_chatbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyPDF2>=3.0.0",
        "spacy>=3.5.0",
        "python-dotenv>=1.0.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0",
        "pytesseract>=0.3.10",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A rule-based chatbot for extracting and matching rules from unstructured text",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rule-based-chatbot",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 