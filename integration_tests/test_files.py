import unittest

from integration_tests.files import make_unreadable_file, read_file, TempDir


class Test_make_unreadable_file(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = TempDir.make_dir()

    def test(self):
        path = self.tmp_dir.join("unreadable")
        make_unreadable_file(self.tmp_dir.join("unreadable"))
        with self.assertRaises(IOError):
            read_file(path)

    def tearDown(self):
        self.tmp_dir.clean_up()
