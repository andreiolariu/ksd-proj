from libs.indexmanager import FolderManager

if __name__ == '__main__':
  manager = FolderManager()
  for followed in manager.get_followed():
    # index(followed)
