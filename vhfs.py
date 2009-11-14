#!/usr/bin/env python
# Use `tail -f LOG` to read the log in real-time (as it is written).
# Also, mount with `./memfs.py MOUNTPOINT -d` to have FUSE print out its own
# debugging messages (which are in some cases more, and some cases less useful
# than mine).

import fuse

import os
import stat
import errno
import datetime
import time
import calendar
import logging
import copy
import sys
import traceback

# models import
from elixir import *
from models import *
from vhfs_parser import *

from vhfs_exceptions import VHFSException
from exceptions import Exception
from path_interpreter import PathInterpreter
from path_interpreter import Path

STORAGE_DIR='/tmp'

metadata.bind = "sqlite:///vhfs.sqlite"
metadata.bind.echo = False

LOG_FILENAME = "log/LOG"
logging.basicConfig(filename=LOG_FILENAME, level = logging.DEBUG)
ROOT_TAG_NAME = u'tag'

sys.stdout = open('log/stdout.log', 'w')
sys.stderr = open('log/stderr.log', 'w')

setup_all()
create_all()

# FUSE version at the time of writing. Be compatible with this version.
fuse.fuse_python_api = (0, 2)

class Stat(fuse.Stat):

    DIRSIZE = 4096

    def __init__(self, st_mode, st_size, st_nlink=1, st_uid=None, st_gid=None,
            dt_atime=None, dt_mtime=None, dt_ctime=None):

        self.st_mode = st_mode
        self.st_ino = 0         
        self.st_dev = 0         
        self.st_nlink = st_nlink
        if st_uid is None:
            st_uid = os.getuid()
        self.st_uid = st_uid
        if st_gid is None:
            st_gid = os.getgid()
        self.st_gid = st_gid
        self.st_size = st_size
        now = datetime.datetime.utcnow()
        self.dt_atime = dt_atime or now
        self.dt_mtime = dt_mtime or now
        self.dt_ctime = dt_ctime or now

    def __repr__(self):
        return ("<Stat st_mode %s, st_nlink %s, st_uid %s, st_gid %s, "
            "st_size %s>" % (self.st_mode, self.st_nlink, self.st_uid,
            self.st_gid, self.st_size))

    def _get_dt_atime(self):
        return self.epoch_datetime(self.st_atime)
    def _set_dt_atime(self, value):
        self.st_atime = self.datetime_epoch(value)
    dt_atime = property(_get_dt_atime, _set_dt_atime)

    def _get_dt_mtime(self):
        return self.epoch_datetime(self.st_mtime)
    def _set_dt_mtime(self, value):
        self.st_mtime = self.datetime_epoch(value)
    dt_mtime = property(_get_dt_mtime, _set_dt_mtime)

    def _get_dt_ctime(self):
        return self.epoch_datetime(self.st_ctime)
    def _set_dt_ctime(self, value):
        self.st_ctime = self.datetime_epoch(value)

    dt_ctime = property(_get_dt_ctime, _set_dt_ctime)

    @staticmethod
    def datetime_epoch(dt):
        return calendar.timegm(dt.timetuple())

    @staticmethod
    def epoch_datetime(seconds):
        return datetime.datetime.utcfromtimestamp(seconds)

    def set_times_to_now(self, atime=False, mtime=False, ctime=False):
        now = datetime.datetime.utcnow()
        if atime:
            self.dt_atime = now
        if mtime:
            self.dt_mtime = now
        if ctime:
            self.dt_ctime = now

    def check_permission(self, uid, gid, flags):
        if flags == os.F_OK:
            return True
        user = (self.st_mode & 0700) >> 6
        group = (self.st_mode & 070) >> 3
        other = self.st_mode & 07
        if uid == self.st_uid:
            mode = user | group | other
        elif gid == self.st_gid:
            mode = group | other
        else:
            mode = other
        if flags & os.R_OK:
            if mode & os.R_OK == 0:
                return False
        if flags & os.W_OK:
            if mode & os.W_OK == 0:
                return False
        if flags & os.X_OK:
            if uid == 0:
                if mode & 0111 == 0:
                    return False
            else:
                if mode & os.X_OK == 0:
                    return False
        return True

class FSObject(object):
    def __repr__(self):
        return "<%s %s>" % (type(self).__name__, self.name)


class VHFSDir(FSObject):
    def __init__(self, name, mode, uid, gid, parent=None):
        self.name = str(name)
        self.stat = Stat(mode, Stat.DIRSIZE, st_nlink=2, st_uid=uid,
            st_gid=gid)
        self.files = {}
        self.parent = parent

class VHFSLink(FSObject):

    def __init__(self, name, destination, mode, uid, gid, parent=None):
        self.name = name
        self.stat = Stat(mode, len(destination), st_nlink=1, st_uid=uid,
            st_gid=gid)
        self.destination = destination
        self.parent = parent

    def read(self, size, offset):
        logging.debug("data: %r" % self.data)
        logging.debug("returned: %r" % self.data[offset:offset+size])
        self.stat.set_times_to_now(atime=True)
        return self.data[offset:offset+size]

    def write(self, buf, offset):
        if offset < len(self.data):
            before = self.data[:offset]
            after = self.data[offset+len(buf):]
        else:
            if offset > len(self.data):
                self.truncate(offset)
            before = self.data
            after = ''
        self.data = before + buf + after
        self.stat.st_size = len(self.data)
        self.stat.set_times_to_now(mtime=True)
        return len(buf)

    def truncate(self, size):
        if size < len(self.data):
            self.data = self.data[:size]
            self.stat.st_size = size
        elif size > len(self.data):
            self.data = self.data + '\0'*(size-len(self.data))
            self.stat.st_size = size
        self.stat.set_times_to_now(mtime=True)

class VHFS(fuse.Fuse):
    def __init__(self, *args, **kwargs):
        logging.info("Mounting file system")
        super(VHFS, self).__init__(*args, **kwargs)
        logging.info('MOUNTPOINT: ' + `self.fuse_args.mountpoint`)
        #self.__prepare_db()
        #self.__mdmgr = MetaDataManager.getInstance()
        #logging.info(args)
        #logging.info(kwargs)

    def __get_context(self):
        '''
            Property getter method for the instance variable context.
        '''
        context           = PathContext()
        calling_func_name = sys._getframe(1).f_code.co_name
        context.operation = calling_func_name
        return context

    context = property(__get_context)
    '''@ivar: Current context.
       @type: PathContext 
    '''

    #def __prepare_db(self):
        #tag = Tag.query().limit(2).filter(Tag.name==ROOT_TAG_NAME).all()
        #if len(tag) > 1:
            #Tag.table.drop()
            #Tag.table.create()
            #tag = Tag(name=ROOT_TAG_NAME)
            #tag.save()
        #elif len(tag) == 0:
            #tag = Tag(name=ROOT_TAG_NAME)
            #tag.save()
            ## TODO
            #pass
            #logging.info("Root tag '%s' created" % ROOT_TAG_NAME)
        #session.commit()

    def fsinit(self):
        logging.info("File system mounted")
        self.root_dir = Dir('/', stat.S_IFDIR|0755, os.getuid(), os.getgid())

    def fsdestroy(self):
        logging.info("Unmounting file system")

    def statfs(self):
        logging.info("statfs")
        stats = fuse.StatVfs()
        return stats

    # entry (file or directory) exists if:
    #   * every item in path is correct (semantically and syntactically)
    #   * every attribute and tag exists
    #
    # file exists if:
    #   * entry exists
    #   * last node in path is of FileNode type and its doesn't have func_node
    #   * items in path are coherent with the file attributes and tags
    #   
    # directory exists if:
    #   * entry exists
    #   
    # FIXME
    def getattr(self, path):
        logging.debug("getattr: %s" % path)
        #logging.info('MOUNTPOINT: ' + `self.fuse_args.mountpoint`)
        context = PathContext()
        try:
            file_path_len = self.__mdmgr.file_exists(path)
            if file_path_len:
                return Stat(stat.S_IFLNK | 0755, file_path_len, st_nlink = 1, 
                                st_uid = os.getuid(), st_gid = os.getgid())

            if self.__mdmgr.dir_exists(path):
                return Stat(stat.S_IFDIR | 0555, Stat.DIRSIZE, st_nlink = 2, 
                        st_uid = os.getuid(), st_gid = os.getgid())

            raise Exception("Not file nor dir", err_code = 0)

        except Exception, e:
            logging.info("Exception: %s\n%s \n%s" % (e, sys.exc_info(), \
                            traceback.extract_tb(sys.exc_traceback))) 
            return -errno.ENOENT


    # Note: utime is deprecated in favour of utimens.
    def utime(self, path, times):
        atime, mtime = times
        logging.info("utime: %s (atime %s, mtime %s)" % (path, atime, mtime))
        file = self._search_path(path)
        if file is None:
            return -errno.ENOENT
        file.stat.st_atime = atime
        file.stat.st_mtime = mtime
        file.stat.set_times_to_now(ctime=True)
        return 0

    def access(self, path, flags):
        logging.info("access: %s (flags %s)" % (path, oct(flags)))
        return 0

    def readlink(self, path):
        logging.info("readlink: %s" % path)
        file_basename = os.path.basename(path)
        f = File.get_by(name = file_basename)
        if f == None:
            return -errno.EACCES
        return str(f.path)

    def mknod(self, path, mode, rdev):
        logging.info("mknod: %s (mode %s, rdev %s)" % (path, oct(mode), rdev))
        return -errno.EOPNOTSUPP

    def mkdir(self, path, mode):
        logging.info("mkdir: %s (mode %s)" % (path, oct(mode)))
        try:
            err  = None
            path = self.__prepare_path(path)

            if len(path) < 2 or path[-2].func_node == None or \
                not path[-2].func_node.name in [UNSPECIFIED_SYM, 'children', 'default']:
                raise VHFSException(msg="Second from the end node does not have correct method call", err_code = errno.EBADMSG)

            pr   = PathInterpreter(path)
            pr.resolve_ambigous_nodes()

            # last node may be ambigous
            path2 = Path(pr.get_path()[0:-1])
            path  = pr.get_path()

            if (len(path.get_nodes_with_subnodes_of_type(TagNode)) < 1 \
                or not isinstance(path2[-1], TagNode)):
                raise VHFSException(msg="Second from the end node isn't tag", err_code = errno.EBADMSG)

            #if not isinstance(path[-2], TagNode):
                #pi = path[-2]
                #if isinstance(pi. AmbigousNode) and not (pr.is_name_of_tag(pi.name) \
                    #and pr.is_key_of_attribute(pi.name)):
                    #return -errno.EBADMSG

            md      = MetaDataManager.getInstance()
            parent  = tmp_parent = md.get_tag(path[-2].name)
            new_tag = md.get_tag(path[-1])
            
            if new_tag != None:
                raise VHFSException(msg='Every Tag can have only one parent tag', \
                        err_code = errno.EEXIST)

            #if len(path) > 2:
                #for node in reversed(path[:-3]):
                    #curr = md.get_tag(node.name)
                    #if curr == None:
                        #raise VHFSException(msg='Tag %s does not exists: %s' % path[-1], \
                               #err_code = errno.ENOENT)
                    #if curr.parent <> tmp_parent:
                        #raise VHFSException(msg='Tag %s is not parent of tag %s' \
                                #% (tmp_parent, curr), err_code = errno.ENOENT)
                    #tmp_parent = curr

            new_tag = Tag(name=path[-1].name, parent = parent)
            new_tag.save()
            session.commit()
            md.add_tag(new_tag)

        except Exception, e:
            logging.info("Exception: %s\n%s \n%s" % (e, sys.exc_info(), \
                            traceback.extract_tb(sys.exc_traceback))) 
            return -e.err_code
        return 0

    def _unlink(self, fileobj):
        parent = fileobj.parent
        if parent is None:
            return -errno.EBUSY
        del parent.files[fileobj.name]
        parent.stat.set_times_to_now(mtime=True)
        return 0

    def unlink(self, path):
        logging.info("unlink: %s" % path)
        file = self._search_path(path)
        if file is None:
            return -errno.ENOENT
        return self._unlink(file)

    def rmdir(self, path):
        logging.info("rmdir: %s" % path)
        #dir = self._search_path(path)
        #if dir is None:
            #return -errno.ENOENT
        #if not isinstance(dir, Dir):
            #return -errno.ENOTDIR
        #if len(dir.files) > 0:
            #return -errno.ENOTEMPTY
        #r = self._unlink(dir)
        #if r == 0:
            #dir.parent.stat.st_nlink -= 1

        #tag = Tag.get_by(name=u'')
        return r

    def symlink(self, target, name):
        logging.info("symlink: target %s, name: %s" % (target, name))
        if os.path.isfile(target):
            self.__mdmgr.index_file()
        f = File(path = target)
        f.save()
        session.commit()
        f.name = File.transformed_name(f.name)
        path   = self.__prepare_path(name)
        pr     = PathInterpreter(path)
        pr.resolve_ambigous_nodes()
        path = pr.get_path()
        tag_nodes = path.get_nodes_with_subnodes_of_type(TagNode)
        # FIXME problem with negation operation
        tags = Tag.query.filter(Tag.name.in_([t.name for t in tag_nodes])).all()
        f.tags.extend(tags)
        attr_nodes = path.get_nodes_with_subnodes_of_type(AttributeNode)
        attr_nodes = filter(lambda a_node: a_node.func_node.name == 'equal', attr_nodes)
        attrs = [Attribute(key = a.key, value = a.func_node.arg_list[0]) for a in attr_nodes]
        f.attributes.extend(attrs)
        f.save()
        session.commit()
        return 0

    def link(self, target, name):
        logging.info("link: target %s, name: %s" % (target, name))
        return -errno.EOPNOTSUPP

    def rename(self, old, new):
        logging.info("rename: target %s, name: %s" % (old, new))
        return -errno.EOPNOTSUPP

    def chmod(self, path, mode):
        logging.info("chmod: %s (mode %s)" % (path, oct(mode)))
        return -errno.EOPNOTSUPP

    def chown(self, path, uid, gid):
        logging.info("chown: %s (uid %s, gid %s)" % (path, uid, gid))
        return -errno.EOPNOTSUPP

    def truncate(self, path, size):
        logging.info("truncate: %s (size %s)" % (path, size))
        file = self._search_path(path)
        if file is None:
            return -errno.ENOENT
        if not isinstance(file, File):
            return -errno.EISDIR
        file.truncate(size)
        return 0

    def opendir(self, path):
        logging.info("opendir: %s" % path)
        mode = stat.S_IFDIR | 0777
        dir = VHFSDir('test', mode, os.getuid(), os.getgid())
        logging.info(dir)
        return dir

    def releasedir(self, path, dh):
        logging.info("releasedir: %s (dh %s)" % (path, dh))

    def fsyncdir(self, path, datasync, dh):
        logging.info("fsyncdir: %s (datasync %s, dh %s)"
            % (path, datasync, dh))

    def readdir(self, path, offset, dh):
        logging.info("readdir: %s (offset %s, dh %s)" % (path, offset, dh))
        context           = self.context
        context.path      = path
        context.offset    = offset
        try:
		    interpreter = PathInterpreter(c)
            items       = interpreter.interpret()
		    for item in items:
			    yield fuse.Direntry(str(dir))
        except VHFSException, e:
            logging.info("Exception: %s\n%s \n%s" % (e, sys.exc_info(), 
                            traceback.extract_tb(sys.exc_traceback))) 
            return e.err_code
        return 0

    def open(self, path, flags):
        logging.info("open: %s (flags %s)" % (path, oct(flags)))
        file = self._search_path(path)
        if file is None:
            return -errno.ENOENT
        if not isinstance(file, File):
            return -errno.EISDIR
        accessflags = 0
        if flags & os.O_RDONLY:
            accessflags |= os.R_OK
        if flags & os.O_WRONLY:
            accessflags |= os.W_OK
        if flags & os.O_RDWR:
            accessflags |= os.R_OK | os.W_OK
        if file.stat.check_permission(self.GetContext()['uid'],
            self.GetContext()['gid'], accessflags):
            return file
        else:
            return -errno.EACCES

    def fgetattr(self, path, fh):
        logging.debug("fgetattr: %s (fh %s)" % (path, fh))
        return fh.stat

    def release(self, path, flags, fh):
        logging.info("release: %s (flags %s, fh %s)" % (path, oct(flags), fh))

    def fsync(self, path, datasync, fh):
        logging.info("fsync: %s (datasync %s, fh %s)" % (path, datasync, fh))

    def flush(self, path, fh):
        logging.info("flush: %s (fh %s)" % (path, fh))

    def read(self, path, size, offset, fh): 
        logging.info("read: %s (size %s, offset %s, fh %s)" % (path, size, offset, fh))
        return fh.read(size, offset)

    def write(self, path, buf, offset, fh):
        logging.info("write: %s (offset %s, fh %s)" % (path, offset, fh))
        logging.debug("  buf: %r" % buf)
        return fh.write(buf, offset)

    def ftruncate(self, path, size, fh):
        logging.info("ftruncate: %s (size %s, fh %s)" % (path, size, fh))
        fh.truncate(size)
        return 0

def main():
    # Our custom usage message
    usage = """
    VHFS: A demo FUSE file system.
    """ + fuse.Fuse.fusage
    server = VHFS(version="%prog " + fuse.__version__,
        usage=usage, dash_s_do='setsingle')
    server.parse(errex=1)
    server.multithreaded = 0
    try:
        server.main()
    except fuse.FuseError, e:
        logging.info("File system unmounted")
        logging.info(str(e))

if __name__ == '__main__':
    main()

logging.info("File system unmounted")
