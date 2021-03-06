import os, commands

from libs.utils import strip_tags, get_md5
from config import *

def get_last_modified(root):
  ''' Gets the latest last_modified timestamp for the files in a folder ''' 
  last_modified = 0
  for root, dirnames, filenames in os.walk(root):
    for filename in filenames:
      path = os.path.join(root, filename)
      last_modified = max(last_modified, os.stat(path).st_mtime)
  return last_modified

def get_files(history):
  ''' Create a list of file dictionaries containing path and content 
  Skip files which didn't change from the last indexation
  '''
  files = []
  for path in history['+']:
    f = {}
    f['filename'] = path.split('/')[-1]
    f['path'] = path
    files.append(f)
  # Process the files in batches
  for i in range(0, len(files) / BATCH_TIKA + 1):
    start = BATCH_TIKA * i
    stop = min(len(files), BATCH_TIKA * (i + 1))
    if start < stop:
      get_content(files[start:stop])
  return files

def ok_to_index(filename):
  ''' Decide if to index the content or skip it'''
  extension = filename.split('.')[-1]
  extension = extension.lower()
  return (extension in INDEX_TYPES)

def get_content(files):
  ''' Given a batch of files, send them to tika 
    and parse the content returned
  '''
  # Create command
  command = 'java -jar vendor/tika-app-0.7.jar -t'
  for f in files:
    command += ' "%s"' % f['path']
  # Get output
  output = commands.getoutput(command.encode('utf-8'))
  # The output for each file has the following structure:
  #<argument>file-path</argument><html>...content</html>
  output = output.strip('\n').split('<argument>')[2:]
  idx = 0
  for piece in output:
    content = ''
    try:
      path, content = piece.split('</argument>')
      path = path.replace('\n', ' ')
      # Strip tags
      content = strip_tags(content.replace('\n', ' '))
      content = content.strip()
    except:
      print 'weird: %s' % piece[:100]
    if not content:
      print 'no content for %s' % files[idx]['path']
    files[idx]['content'] = content
    idx += 1
