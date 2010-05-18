from libs.indexmanager import FolderManager
from index import IndexFiles

if __name__ == '__main__':
  manager = FolderManager()
  indexer = IndexFiles()
  for followed in manager.get_followed():
    print 'Updating folder %s...' % followed
    indexer.index_folder(followed)
  print 'Updated.'
