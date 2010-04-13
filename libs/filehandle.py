import os, commands

from libs.utils import strip_tags, get_md5
# File types to be indexed
INDEX = ['pdf', 'doc', 'html', 'txt']
# How many files to send to tika in one batch
BATCH = 200

def get_files(root):
  ''' Create a list of file dictionaries containing path and content '''
  files = []
  # Crawl directory for files
  for root, dirnames, filenames in os.walk(root):
    for filename in filenames:
      if ok_to_index(filename):
        path = os.path.join(root, filename)
        f = {}
        f['filename'] = filename
        f['path'] = path
        files.append(f)
  # Process the files in batches
  for i in range(0, len(files) / BATCH + 1):
    get_content(files[BATCH * i : min(len(files), BATCH * (i + 1))])
  return files
  
def ok_to_index(filename):
  ''' Decide if to index the content or skip it'''
  extension = filename.split('.')[-1]
  extension = extension.lower()
  return (extension in INDEX)

def get_content(files):
  ''' Given a batch of files, send them to tika 
    and parse the content returned
  '''
  # Create command
  command = 'java -jar vendor/tika-app-0.7.jar -x'
  for f in files:
    command += ' "%s"' % f['path']
  # Get output
  output = commands.getoutput(command)
  # The output for each file has the following structure:
  #<argument>file-path</argument><html>...content</html>
  output = output.strip('\n').split('<argument>')[2:]
  content_dex = {}
  for piece in output:
    if '<html' not in piece:
      print 'weird content: %s' % piece[:100]
      continue
    
    try:  
      path, content = piece.split('</argument>')
      path = path.replace('\n', ' ')
      # Strip tags
      content = strip_tags(content.replace('\n', ' '))
    except:
      print 'weird: %s' % piece[:100]
    key = get_md5(path)                    
    content_dex[key] = content
  # Add content to file dictionaries
  for f in files:
    key = get_md5(f['path'])
    if key not in content_dex:
      print 'no content for %s' % f['path']
    f['content'] = content_dex.get(key, '') 
  

