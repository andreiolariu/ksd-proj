import os, threading, time, lucene, sys
from datetime import datetime

from content import extract_content

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""

class Ticker(object):

  def __init__(self):
    self.tick = True

  def run(self):
    while self.tick:
      sys.stdout.write('.')
      sys.stdout.flush()
      time.sleep(1.0)

class IndexFiles(object):
  """Usage: python IndexFiles <doc_directory>"""

  def __init__(self, root, storeDir, analyzer):

    if not os.path.exists(storeDir):
      os.mkdir(storeDir)
    store = lucene.SimpleFSDirectory(lucene.File(storeDir))
    writer = lucene.IndexWriter(store, analyzer, True,
                                lucene.IndexWriter.MaxFieldLength.LIMITED)
    writer.setMaxFieldLength(1048576)
    self.indexDocs(root, writer)
    ticker = Ticker()
    print 'optimizing index',
    threading.Thread(target=ticker.run).start()
    writer.optimize()
    writer.close()
    ticker.tick = False
    print 'done'

  def indexDocs(self, root, writer):
    files_dex = get_files(root)
    for root, dirnames, filenames in os.walk(root):
      for filename in filenames:
        try:
          path = os.path.join(root, filename)
          try:
            content = extract_content(path)
          except Exception, e:
            content = None
            print 'Failed getting content from %s: %s' % (path, e)
          if not content:
            continue
          print "adding", filename
          doc = lucene.Document()
          doc.add(lucene.Field("name", filename,
                               lucene.Field.Store.YES,
                               lucene.Field.Index.NOT_ANALYZED))
          doc.add(lucene.Field("path", path,
                               lucene.Field.Store.YES,
                               lucene.Field.Index.NOT_ANALYZED))
          if len(content) > 0:
            doc.add(lucene.Field("contents", content,
                                 lucene.Field.Store.NO,
                                 lucene.Field.Index.ANALYZED))
          else:
            print "warning: no content in %s" % filename
          writer.addDocument(doc)
        except Exception, e:
          print "Failed in indexDocs:", e

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print IndexFiles.__doc__
    sys.exit(1)
  # Start Java VM
  lucene.initVM(lucene.CLASSPATH)
  print 'lucene', lucene.VERSION
  start = datetime.now()
  try:
      
    IndexFiles(sys.argv[1], "index", lucene.StandardAnalyzer(lucene.Version.LUCENE_CURRENT))
    end = datetime.now()
    print end - start
  except Exception, e:
    print "Failed: ", e

