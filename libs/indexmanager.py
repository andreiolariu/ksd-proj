import os
import gzip
import simplejson as json

from libs.filehandle import ok_to_index

import config

class IndexManager(object):

  def __init__(self):
    # Temporary remember the timestamp of each file. This is needed
    # because of the difference between scanning the folder and actually
    # indexing those files.
    self.cache = {}

  def _read(self):
    try:
      f = gzip.open('%s/files.gz' % config.STORE_DIR, 'rb')
      content = f.read()
      f.close()
    except:
      content = None

    if content:
      obj = json.loads(content)
      self.indexed = obj[0]
      self.followed = obj[1]
    else:
      self.indexed = {}
      self.followed = []

  def _save(self):
    if not os.path.exists(config.STORE_DIR):
      # Create the store dir if missing.
      os.mkdir(config.STORE_DIR)

    f = gzip.open('%s/files.gz' % config.STORE_DIR, 'wb')
    obj = [self.indexed, self.followed]
    f.write(json.dumps(obj))
    f.close()

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

    files = self._scan_folder(root)
    self.cache.update(files)
    to_add = []
    to_remove = []
    to_update = []
    for filename, last_modified in files.items():
      if filename not in self.indexed:
        to_add.append(filename)
      elif last_modified > self.indexed[filename]:
        to_update.append(filename)
    for filename in self.indexed:
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

    for filename in updated:
      # What was this file's last_modified timestamp?
      if filename in self.cache:
        last_modified = self.cache.pop(filename)
      else:
        last_modified = os.stat(path).st_mtime
      self.indexed[filename] = last_modified

    for filename in removed:
      if filename in self.indexed:
        del self.indexed[filename]

    self._save()

  def follow_folder(self, path):
    for following in self.followed:
      # We are already following one this folder through one of its parents.
      if path.startswith(following):
        return
    self.followed.append(path)

    self._save()

  def unfollow_folder(self, path):
    try:
      self.followed.remove(path)

      self._save()
    except:
      pass

  def get_followed_folder(self):
    self._read()

    return self.followed















    # end of file
