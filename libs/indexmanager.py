import gzip
import simplejson as json

from libs.filehandle import ok_to_index

from config import STORE_DIR

class IndexManager(object):

  def __init__(self):
    # Temporary remember the timestamp of each file. This is needed
    # because of the difference between scanning the folder and actually
    # indexing those files.
    self.cache = {}

  def _read(self):
    try:
      f = gzip.open('%s/files.gz' % STORE_DIR, 'rb')
      content = f.read()
      f.close()
    except:
      content = None

    if content:
      self.indexed = json.loads(content)
    else:
      self.indexed = {}

  def _save(self):
    if not os.path.exists(STORE_DIR):
      # Create the store dir if missing.
      os.mkdir(STORE_DIR)

    f = gzip.open('%s/files.gz' % STORE_DIR, 'wb')
    f.write(json.dumps(self.indexed))
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
      elif last_modified > indexed[filename]:
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
      self.data[filename] = last_modified

    for filename in removed:
      if filename in self.data:
        del self.data[filename]

    self._save()














    # end of file
