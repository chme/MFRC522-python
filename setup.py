from setuptools import setup

setup(name='MFRC522-python',
      version='0.0.1',
      description='Raspberry Pi Python library for SPI RFID RC522 module',
      author="Christian Meffert",
      author_email="christian.meffert@googlemail.com",
      url='https://github.com/chme/MFRC522-python',
      install_requires=['spidev', 'RPi.GPIO', 'cmd2'],
      packages=['mfrc522'],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
          "Operating System :: POSIX :: Linux",
      ],
      entry_points={
          'console_scripts': [
              'mfrc522-cli=mfrc522.mfrc522_cli:main'
          ]
      }
      )
