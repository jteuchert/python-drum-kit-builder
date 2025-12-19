""" This script lets you generate a standalone version (with .exe) of the Python script.
The result may be large in size, since this method is not yet optimized for this particular project."""

from cx_Freeze import setup, Executable

setup(
    name="Kit Builder",
    version="1.0",
    description="Kit Builder",
    executables=[Executable("kit_builder_v1.py")]
)