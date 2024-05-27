from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open('README.md') as f:
    long_description = f.read()

setup(
    name='ground_control',
    version='0.1',
    packages=find_packages(),
    install_requires=required,
    author=['Pablo RAOULT', 'Molka JELASSI', 'Denis RAKULAN', 'Benjamin ELKAYS'],
    author_email=['praoult-prestataire@ina.fr', 'mjelassi-prestataire@ina.fr', 'drakulan-prestataire@ina.fr', 'belkays@ina.fr'],
    description='Ground truth application for 2IA',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://git.infra.sas.ina/ia/code/ground-control/backend',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.10',
)
