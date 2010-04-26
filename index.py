import os, threading, time, sys
from datetime import datetime

import lucene

from libs.textcat import NGram, _NGram
from libs.filehandle import get_files
from config import *


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

  def __init__(self, storeDir):
    # Create index directory
    if not os.path.exists(storeDir):
      os.mkdir(storeDir)
    self.store = lucene.SimpleFSDirectory(lucene.File(storeDir))
    
  def index(self, root):
    ''' 
      Index files in the folder root
    '''
    # Show ticker
    ticker = Ticker()
    threading.Thread(target=ticker.run).start()
    
    # Get content for all files
    print '\nFetching content'
    docs = self.fetch_files(root)
    # Remove files with no content
    tmp = []
    for doc in docs:
      if doc['content']:
        tmp.append(doc)
    docs = tmp
    # Detect language for each file and group by it
    batches = self.detect_language(docs)
    
    # For each batch of files with the same language, analyze and index it
    for language, batch in batches.iteritems():
      if language:
        print '\nIndexing %s file(s) in %s' % (len(batch), language)
      else:
        print '\nIndexing %s file(s) without a detectable language' % len(batch)
        language = 'English'
        
      # Initialize analyzer with a language-specific stemmer
      analyzer = lucene.SnowballAnalyzer(lucene.Version.LUCENE_CURRENT, \
                                        language)
      writer = lucene.IndexWriter(self.store, analyzer, True,
                                lucene.IndexWriter.MaxFieldLength.LIMITED)
      writer.setMaxFieldLength(1048576)
      
      # Index files
      for document in batch:
        writer.addDocument(document)
      writer.optimize()
      writer.close()
      
    ticker.tick = False

  def detect_language(self, docs):
    '''
      Adds a 'language' field to documents which have content in a supported
      language
    '''
    batches = {}
    l = NGram('libs/LM') # Textcat language detector
    for doc in docs:
      language = ''
      if doc['content'] and len(doc['content']) > 5:
        language = l.classify(str(doc['content'][:1000].encode('utf8')))
      if language not in SUPPORTED_LANGUAGES:
        language = ''
      if language:
        language = language.capitalize()
        doc.add(lucene.Field("language", language,
                             lucene.Field.Store.YES,
                             lucene.Field.Index.NOT_ANALYZED))
      if language not in batches:
        batches[language] = []
      batches[language].append(doc)
    return batches
        
  def fetch_files(self, root):
    files_list = get_files(root)
    docs = []
    for f in files_list:
      try:
        doc = lucene.Document()
        doc.add(lucene.Field("name", f['filename'],
                             lucene.Field.Store.YES,
                             lucene.Field.Index.NOT_ANALYZED))
        doc.add(lucene.Field("path", f['path'],
                             lucene.Field.Store.YES,
                             lucene.Field.Index.NOT_ANALYZED))
        doc.add(lucene.Field("content", f['content'],
                             lucene.Field.Store.YES,
                             lucene.Field.Index.ANALYZED,
                             lucene.Field.TermVector.WITH_POSITIONS_OFFSETS))
        docs.append(doc)
      except:
        print 'could not index %s' % f['path']
    return docs

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print IndexFiles.__doc__
    sys.exit(1)
  # Start Java VM
  lucene.initVM(lucene.CLASSPATH)
  print 'lucene', lucene.VERSION
  start = datetime.now()
  #try:
  indexer = IndexFiles('index')
  indexer.index(sys.argv[1])
  end = datetime.now()
  print end - start
  #except Exception, e:
   # print "Failed: ", e

