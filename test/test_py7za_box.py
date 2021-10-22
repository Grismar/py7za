import unittest
from pathlib import Path
from shutil import rmtree
from py7za._py7za_box import box, CLI_DEFAULTS
from conffu import Config
from zipfile import ZipFile
from os import chdir, getcwd

chdir(Path(__file__).parent)


class TestPy7zaBox(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        test = Path('.')
        rmtree(test / 'data')
        (test / 'data/source/sub').mkdir(parents=True, exist_ok=True)
        (test / 'data/target').mkdir(parents=True, exist_ok=True)
        with open('data/.gitignore', 'w') as f:
            f.write('*\n!.gitignore')
        with open('data/source/x.csv', 'w') as f:
            f.write('A,B,C\n1,2,3\n')
        with open('data/source/sub/test.txt', 'w') as f:
            f.write('Testing, 1, 2, 3')
        with open('data/source/sub/y.csv', 'w') as f:
            f.write('X,Y,Z\n0,0,0\n')
        with open('data/source/sub/hello.txt', 'w') as f:
            f.write('Hello\nWorld\n')

    def tearDown(self) -> None:
        test = Path('.')
        rmtree(test / 'data')
        (test / 'data').mkdir(parents=True, exist_ok=True)
        with open('data/.gitignore', 'w') as f:
            f.write('*\n!.gitignore')

    async def test_box_inplace(self):
        with open('data/source/x.csv', 'rb') as f:
            original_content = f.read()
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': '*.csv'}))
        with ZipFile('data/source/x.csv.zip') as zf:
            with zf.open('x.csv') as f:
                self.assertEqual(original_content, f.read(), 'zipped content is identical')
        self.assertFalse(Path('data/source/x.csv').is_file(), 'original was removed')

    async def test_box_inplace_wd(self):
        wd = getcwd()
        chdir('data/source')
        with open('x.csv', 'rb') as f:
            original_content = f.read()
        await box(Config(CLI_DEFAULTS | {'glob': '*.csv'}))
        with ZipFile('x.csv.zip') as zf:
            with zf.open('x.csv') as f:
                self.assertEqual(original_content, f.read(), 'zipped content is identical')
        self.assertFalse(Path('x.csv').is_file(), 'original was removed')
        chdir(wd)

    async def test_box_no_delete(self):
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': '*.csv', 'delete': False}))
        self.assertTrue(Path('data/source/x.csv').is_file(), 'original was not removed')

    async def test_box_create_folders(self):
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'target': 'data/target', 'glob': '**/*.csv',
                                         'delete': False}))
        with ZipFile('data/target/x.csv.zip') as zf:
            with zf.open('x.csv') as fz:
                with open('data/source/x.csv', 'rb') as f:
                    self.assertEqual(f.read(), fz.read(), 'zipped content in root is identical')
        self.assertTrue(Path('data/target/sub/y.csv.zip').is_file(), 'file in folder zipped to sub-folder')
        with ZipFile('data/target/sub/y.csv.zip') as zf:
            with zf.open('y.csv') as fz:
                with open('data/source/sub/y.csv', 'rb') as f:
                    self.assertEqual(f.read(), fz.read(), 'zipped content in sub-folder is identical')

    async def test_box_zip_structure(self):
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'target': 'data/target', 'glob': '**/*.csv',
                                         'delete': False, 'create_folders': False, 'zip_structure': True}))
        with ZipFile('data/target/x.csv.zip') as zf:
            with zf.open('x.csv') as fz:
                with open('data/source/x.csv', 'rb') as f:
                    self.assertEqual(f.read(), fz.read(), 'zipped content in root is identical')
        self.assertTrue(Path('data/target/y.csv.zip').is_file(), 'file in folder zipped to root')
        with ZipFile('data/target/y.csv.zip') as zf:
            with zf.open('sub/y.csv') as fz:
                with open('data/source/sub/y.csv', 'rb') as f:
                    self.assertEqual(f.read(), fz.read(), 'zipped content in sub-folder is identical')
