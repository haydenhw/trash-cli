# Copyright (C) 2011 Andrea Francia Trivolzio(PV) Italy

from trashcli.trash import TrashDirs
from nose.tools import istest, assert_in, assert_not_in
from mock import Mock

@istest
class TestTrashDirs_listing:
    @istest
    def the_method_2_is_always_in(self):
        self.uid = 123
        self.volumes = ['/usb']

        assert_in('/usb/.Trash-123', self.trashdirs())

    @istest
    def the_method_1_is_in_if_it_is_a_sticky_dir(self):
        self.uid = 123
        self.volumes = ['/usb']
        self.having_sticky_Trash_dir()

        assert_in('/usb/.Trash/123', self.trashdirs())

    @istest
    def the_method_1_is_not_considered_if_not_sticky_dir(self):
        self.uid = 123
        self.volumes = ['/usb']
        self.having_non_sticky_Trash_dir()

        assert_not_in('/usb/.Trash/123', self.trashdirs())

    @istest
    def should_return_home_trashcan_when_XDG_DATA_HOME_is_defined(self):
        self.environ['XDG_DATA_HOME'] = '~/.local/share'

        assert_in('~/.local/share/Trash', self.trashdirs())

    def trashdirs(self):
        result = []
        def append(trash_dir, volume):
            result.append(trash_dir)
        collect = Mock()
        collect.found_trash_dir.side_effect = append
        class FileReader:
            def list_volumes(_):
                return self.volumes
            def is_sticky_dir(_, path):
                return self.Trash_dir_is_sticky
            def exists(_, path):
                return True
            def is_symlink(_, path):
                return False
        TrashDirs(
            environ=self.environ,
            getuid=lambda:self.uid,
            fs = FileReader(),
        ).list_trashdirs(collect)
        return result

    def setUp(self):
        self.uid = -1
        self.volumes = ()
        self.Trash_dir_is_sticky = not_important_for_now()
        self.environ = {}
    def having_sticky_Trash_dir(self): self.Trash_dir_is_sticky = True
    def having_non_sticky_Trash_dir(self): self.Trash_dir_is_sticky = False

def not_important_for_now(): None

from nose.tools import assert_equals
from mock import MagicMock
@istest
class Describe_AvailableTrashDirs_when_parent_is_unsticky:
    def setUp(self):
        self.error_log = MagicMock()
        self.fs = MagicMock()
        self.dirs = TrashDirs(environ =  {}, getuid = lambda:123,
                                       fs = self.fs)
        self.fs.list_volumes.return_value = ['/topdir']
        self.fs.is_sticky_dir.side_effect = (
                lambda path: {'/topdir/.Trash':False}[path])

    def test_it_should_report_skipped_dir_non_sticky(self):
        self.fs.exists.side_effect = (
                lambda path: {'/topdir/.Trash/123':True}[path])

        self.dirs.list_trashdirs(self.error_log)

        (self.error_log.top_trashdir_skipped_because_parent_not_sticky.
                assert_called_with('/topdir/.Trash/123'))

    def test_it_shouldnot_care_about_non_existent(self):
        self.fs.exists.side_effect = (
                lambda path: {'/topdir/.Trash/123':False}[path])

        self.dirs.list_trashdirs(self.error_log)

        assert_equals([], self.error_log.
                top_trashdir_skipped_because_parent_not_sticky.mock_calls)

@istest
class Describe_AvailableTrashDirs_when_parent_is_symlink:
    def setUp(self):
        self.error_log = MagicMock()
        self.fs = MagicMock()
        self.dirs = TrashDirs(environ =  {}, getuid = lambda:123,
                                       fs = self.fs)
        self.fs.list_volumes.return_value = ['/topdir']
        self.fs.exists.side_effect = (lambda path: {'/topdir/.Trash/123':True}[path])


    def test_it_should_skip_symlink(self):
        self.fs.is_sticky_dir.return_value = True
        self.fs.is_symlink.return_value    = True

        self.dirs.list_trashdirs(self.error_log)

        (self.error_log.top_trashdir_skipped_because_parent_is_symlink.
                assert_called_with('/topdir/.Trash/123'))

