import os
import gzip
import time
import simplejson as json

from libs.filehandle import ok_to_index

import config

class CachedFileDB(object):

  def __init__(self, label, time=0):
    self.db_path = '%s/%s.gz' % (config.STORE_DIR, label)
    self._last_read = 0
    self._time = time

  def _read(self):
    if time.time() - self._last_read < self._time:
      # Too soon to re-read the database.
      return

    try:
      f = gzip.open(self.db_path, 'rb')
      content = f.read()
      f.close()
      self._last_read = time.time()
    except:
      content = None

    if content:
      self.data = json.loads(content)
    else:
      self.data = None

  def _save(self):
    if not os.path.exists(config.STORE_DIR):
      # Create the store dir if missing.
      os.mkdir(config.STORE_DIR)

    f = gzip.open(self.db_path, 'wb')
    f.write(json.dumps(self.data))
    f.close()

class FolderManager(CachedFileDB):

  def __init__(self):
    CachedFileDB.__init__(self, 'followed')

  def follow(self, path):
    self._read()
    if self.data is None:
      self.data = []
    for following in self.data:
      parent = following
      if not parent.endswith('/'):
        parent += '/'
      # We are already following one this folder through one of its parents.
      if path.startswith(parent):
        return
    self.data.append(path)
    self._save()

  def unfollow(self, path):
    self._read()
    if self.data is None:
      self.data = []
    try:
      self.data.remove(path)
      self._save()
    except:
      pass

  def get_followed(self):
    self._read()
    if not self.data:
      return []
    else:
      return self.data

class IndexManager(CachedFileDB):

  def __init__(self):
    CachedFileDB.__init__(self, 'files')
    # Temporary remember the timestamp of each file. This is needed
    # because of the difference between scanning the folder and actually
    # indexing those files.
    self.cache = {}

  def _scan_folder(self, root):
    files = {}
    # Crawl directory for files
    for root, dirnames, filenames in os.walk(root):
      for filename in filenames:
        if ok_to_index(filename):
          path = os.path.join(root, filename)
          last_modified = os.stat(path).st_mtime
          files[path] = last_modified
    return files

  def get_files_to_index(self, root):
    """
      Returns a dict with the files that need to be indexed.
    """
    self._read()
    if self.data is None:
      self.data = {}

    files = self._scan_folder(root)
    self.cache.update(files)
    to_add = []
    to_remove = []
    to_update = []
    for filename, last_modified in files.items():
      if filename not in self.data:
        to_add.append(filename)
      elif last_modified > self.data[filename]:
        to_update.append(filename)
    for filename in self.data:
      if filename.startswith(root) and filename not in files:
        to_remove.append(filename)

    result = {'+': to_add,
              '-': to_remove}
    # Files that need updating will be removed from the indexed and re-added.
    result['+'].extend(to_update)
    result['-'].extend(to_update)

    return result

  def mark_as_indexed(self, updated, removed):
    """
      Marks one or more files as indexed.
    """
    self._read()
    if self.data is None:
      self.data = {}

    for filename in updated:
      # What was this file's last_modified timestamp?
      if filename in self.cache:
        last_modified = self.cache.pop(filename)
      else:
        last_modified = os.stat(filename).st_mtime
      self.data[filename] = last_modified

    for filename in removed:
      if filename in self.data:
        del self.data[filename]

    self._save()
