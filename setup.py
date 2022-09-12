from setuptools import setup, find_packages

setup(
    name ='pydasp',
    version ='0.0.1',
    author='Paul Taylor',
    author_email='paulthecomposer@yahoo.com',
    description='A package for digital audio signal processing',
    packages=find_packages(),
    py_modules=['adsr_envelope', 'audio_io', 'basic_signals', 'frequency', 'synthesis'],
    install_requires=['numpy', 'SciPy', 'sounddevice'],
    keywords=['python', 'audio', 'DSP', 'music', 'sound', 'audio synthesis', 'composition']
)
