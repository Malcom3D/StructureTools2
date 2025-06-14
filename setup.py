from setuptools import setup
import os

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "freecad", "StructureTools2", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.StructureTools2',
      version=str(__version__),
      packages=['freecad',
                'freecad.StructureTools2'],
      maintainer="Malcom3D",
      maintainer_email="malcom3d.gpl@gmail.com",
      url="https://www.freecad.org",
      description="Workbench for 2d and 3d structural analysis",
      install_requires=['numpy','scipy','sympy'],
      include_package_data=True)
