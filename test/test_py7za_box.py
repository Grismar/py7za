import unittest
from pathlib import Path
from shutil import rmtree
from py7za.py7za_box import box, CLI_DEFAULTS
from conffu import Config
from zipfile import ZipFile
from os import chdir, getcwd

chdir(Path(__file__).parent)
CLI_DEFAULTS['output'] = 'q'


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

    async def test_box_round_trip(self):
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': '*.csv'}))
        self.assertFalse(Path('data/source/x.csv').is_file(), 'original is gone after box')
        self.assertTrue(Path('data/source/x.csv.zip').is_file(), 'archive exists after box')
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': '*.csv.zip', 'unbox': True}))
        self.assertTrue(Path('data/source/x.csv').is_file(), 'original is back after unbox')
        self.assertFalse(Path('data/source/x.csv.zip').is_file(), 'archive removed after unbox')

    async def test_box_overwrite_zip(self):
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': 'x.csv', 'delete': False}))
        self.assertTrue(Path('data/source/x.csv.zip').is_file(), 'archive exists after first box')
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': 'x.csv'}))
        self.assertFalse(Path('data/source/x.csv').is_file(), 'original is gone after box')
        with ZipFile('data/source/x.csv.zip') as zf:
            self.assertEqual(1, len(zf.filelist), 'Only one file in resulting archive')

    async def _do_test_overwrite(self, mode=None):
        with open('data/source/x.csv') as f:
            content = f.read()
        await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': 'x.csv', 'delete': False}))
        with open('data/source/x.csv', 'a') as f:
            f.write('extra')
            new_content = content + 'extra'
        if mode is None:
            await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': 'x.csv.zip', 'unbox': True}))
        else:
            await box(Config(CLI_DEFAULTS | {'root': 'data/source', 'glob': 'x.csv.zip', 'unbox': True,
                                             'overwrite': mode}))
        return content, new_content

    async def test_box_overwrite_source_skip_default(self):
        content, new_content = await self._do_test_overwrite()
        self.assertFalse(Path('data/source/x.csv.zip').is_file(), 'archive is gone after unbox')
        self.assertTrue(Path('data/source/x.csv').is_file(), '"original" file exist')
        with open('data/source/x.csv') as f:
            self.assertEqual(new_content, f.read(), 'Content of original file untouched, no overwrite')

    async def test_box_overwrite_source_all(self):
        content, new_content = await self._do_test_overwrite('a')
        self.assertFalse(Path('data/source/x.csv.zip').is_file(), 'archive is gone after unbox')
        self.assertTrue(Path('data/source/x.csv').is_file(), '"original" file exist')
        with open('data/source/x.csv') as f:
            self.assertEqual(content, f.read(), 'Content of original file back to original, overwritten')

    async def test_box_overwrite_source_rename_new(self):
        content, new_content = await self._do_test_overwrite('u')
        self.assertFalse(Path('data/source/x.csv.zip').is_file(), 'archive is gone after unbox')
        self.assertTrue(Path('data/source/x.csv').is_file(), '"original" file exist')
        with open('data/source/x.csv') as f:
            self.assertEqual(new_content, f.read(), 'Content of original file untouched, no overwrite')
        self.assertTrue(Path('data/source/x_1.csv').is_file(), 'extracted file was renamed')
        with open('data/source/x_1.csv') as f:
            self.assertEqual(content, f.read(), 'Extracted file contains original content')

    async def test_box_overwrite_source_rename_existing(self):
        content, new_content = await self._do_test_overwrite('t')
        self.assertFalse(Path('data/source/x.csv.zip').is_file(), 'archive is gone after unbox')
        self.assertTrue(Path('data/source/x.csv').is_file(), '"original" file exist')
        with open('data/source/x.csv') as f:
            self.assertEqual(content, f.read(), 'extracted file to original name, original content')
        self.assertTrue(Path('data/source/x_1.csv').is_file(), 'existing file was renamed')
        with open('data/source/x_1.csv') as f:
            self.assertEqual(new_content, f.read(), 'Existing files still contains new content')
