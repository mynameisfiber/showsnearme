from setuptools import setup, find_namespace_packages

setup(
    name="showsnearme",
    version="0.2",
    description="Using the ohmyrockness to bring shows to your CLI",
    url="http://github.com/mynameisfiber/showsnearme",
    author="Micha Gorelick",
    license="MIT",
    packages=find_namespace_packages(include=['showsnearme.*']),
    zip_safe=False,
    install_requires=list(open("./requirements.txt")),
    entry_points={"console_scripts": ["showsnearme=showsnearme.cli:main"]},
)
