from setuptools import find_packages, setup


with open("requirements.txt") as rf:
    requirements = rf.readlines()
with open("README.md") as rf:
    readme = rf.read()

setup(
    name='sqldirect',
    version='0.1.0',
    url="https://github.com/gpcimino/sqldirect",
    description='A Micro ORM for Python3',
    long_description=readme,
    author='Giampaolo Cimino',
    author_email='gcimino@gmail.com',
    license='Apache-2.0',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3'
    ],
    keywords=['python3', 'sql', 'orm', 'database', 'oop', 'microorm'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points="",
    install_requires=requirements,
    extras_require=dict(
        postgresql=[
            'psycopg2'
        ]
    )
)
