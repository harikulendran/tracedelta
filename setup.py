from setuptools import setup

DEPS = [ "pyperclip", "click", "rich" ]

setup(
    name="tracedelta",
    version="1.0.0",
    author="Hari Kulendran",
    author_email="me@hari.dev",
    description="calculate timestamp deltas from log traces",
    entry_points={ "console_scripts": [ "tracedelta=main:run" ] },
    install_requires=DEPS
)
