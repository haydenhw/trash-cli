from optparse import OptionParser
from trashcli import version
from trashcli.cli.util import NoWrapFormatter
from trashcli.filesystem import Path
from trashcli.trash import GlobalTrashCan
from trashcli.trash import logger

class RestoreCommandLine(object):
    def __init__(self,restorer):
        self.restorer = restorer
    
    def execute(self,args):
        parser = OptionParser(
            usage="%prog [OPTION]... FILE [DEST]",
            description=("Restore the trashed file specified by SOURCE " + 
                         "in DEST (or its original location)."),
            version="%%prog %s" % version,
            formatter=NoWrapFormatter())

        (options, args) = parser.parse_args(args)
        
        if len(args) == 0: 
            parser.error("Please specify the trashed file to be restored.")
        elif len(args) == 1 :
            self.restorer.restore_latest(Path(args[0]))
        elif len(args) == 2:
            self.restorer.restore_latest(Path(args[0]), Path(args[1]))
        else :
            parser.error("Too many arguments, one or two expected, %s given." 
                          % len(args))


def last_trashed(trashed_file1, trashed_file2):
    """
    Returns the TrashedFile more recently trashed. 
    In the case the are trashed at the same time return the first one.
    """
    if trashed_file1 == None:
        return trashed_file2
    
    if trashed_file2 == None:
        return trashed_file1
    
    if trashed_file1.deletion_date < trashed_file2.deletion_date :
        return trashed_file2
    
    if trashed_file1.deletion_date > trashed_file2.deletion_date:
        return trashed_file1
    
    return trashed_file1

class TrashNotFoundError(IOError):
    pass

def find_latest(trashcan, path):
    def is_the_expected_path(trashed_file):
        result=(trashed_file.path == path)
        if result:
            logger.debug("Matched path =`%s'", trashed_file.path)
        else :
            logger.debug("Skipped path = `%s'", trashed_file.path)
        return result 
        
    
    list1 = filter(is_the_expected_path, trashcan.trashed_files())
    latest = reduce(last_trashed, list1, None)
    if latest == None:
        raise TrashNotFoundError("Trashed file with specified path"
                                 "not found : `%s'" % path)
    return latest

class Restorer(object):
    def __init__(self, trashcan, find_latest=find_latest):
        self.trashcan = trashcan
        self.find_latest = find_latest
        
    def restore_latest(self, path, dest=None):
        """
        restore(path: Path, dest: Path)
        
        Restore the specified source to the specified destination.
        """
        latest=self.find_latest(self.trashcan, path)
        latest.restore(dest)


def main():
    import sys
    trashcan = GlobalTrashCan()
    restorer = Restorer(trashcan)
    cmd = RestoreCommandLine(restorer)
    cmd.execute(sys.argv[1:])