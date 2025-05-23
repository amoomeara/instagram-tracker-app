from setuptools import setup

APP = ['tracker.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pandas', 'matplotlib', 'fpdf'],
    'includes': ['tkinter'],
    'excludes': ['jaraco.text', 'PyInstaller', 'PySide2', 'test', 'unittest'],
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
