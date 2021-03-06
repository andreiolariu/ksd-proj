import os, threading, time, sys
from datetime import datetime

import lucene

from libs.textcat import NGram, _NGram
from libs.indexmanager import IndexManager, FolderManager
from config import *
from libs.filehandle import get_files

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

  def __init__(self):
    # Create index directory
    lucene.initVM(lucene.CLASSPATH)
    if not os.path.exists(STORE_DIR):
      os.mkdir(STORE_DIR)
    self.store = lucene.SimpleFSDirectory(lucene.File(STORE_DIR))
    self.im = IndexManager()
    
  def index_files(self, add=[], remove=[]):
    ''' 
      Index (add/remove/update) a given list of files
    '''
    # Show ticker
    #ticker = Ticker()
    #threading.Thread(target=ticker.run).start()
    history = {'+': add,
               '-': remove}
    self.__index(history)
    
  def index_folder(self, folder):
    '''
      Index a folder
    '''
    # Get list of files indexed
    history = self.im.get_files_to_index(folder)
    print '\n%s files to be indexed' % len(history['+'])
    self.__index(history)
    
  def __index(self, history):
    # Get content for all files
    print '\nFetching content'
    docs = self.__fetch_files(history)
    # Detect language for each file and group by it
    batches = self.__detect_language(docs)
    
    # Remove missing and updated files
    if history['-']:
      analyzer = lucene.StandardAnalyzer(lucene.Version.LUCENE_CURRENT)
      writer = lucene.IndexWriter(self.store, analyzer, \
                        lucene.IndexWriter.MaxFieldLength.LIMITED)
      for path in history['-']:
        writer.deleteDocuments(lucene.Term("path", path))
        print 'deleted %s' % path
      writer.optimize()
      writer.close()
      self.im.mark_as_indexed([], history['-'])
    
    # For each batch of files with the same language, analyze and index it
    for language, batch in batches.iteritems():
      if language:
        print '\nIndexing %s file(s) in %s' % (len(batch), language)
      else:
        print '\nIndexing %s file(s) without a detectable language' % len(batch)
        language = DEFAULT_LANGUAGE
        
      # Initialize analyzer with a language-specific stemmer
      analyzer = lucene.SnowballAnalyzer(lucene.Version.LUCENE_CURRENT, \
                                        language)
      writer = lucene.IndexWriter(self.store, analyzer,
                                lucene.IndexWriter.MaxFieldLength.LIMITED)
      writer.setMaxFieldLength(1048576)
        
      # Index files
      indexed = []
      for document in batch:
        writer.addDocument(document)
        print document['path']
        indexed.append(document['path'])
      writer.optimize()
      writer.close()
      self.im.mark_as_indexed(indexed, [])
    
    #ticker.tick = False

  def __detect_language(self, docs):
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
      if not language:
        language = DEFAULT_LANGUAGE
      language = language.capitalize()
      doc.add(lucene.Field("language", language,
                             lucene.Field.Store.YES,
                             lucene.Field.Index.NOT_ANALYZED))
      if language not in batches:
        batches[language] = []
      batches[language].append(doc)
    return batches
        
  def __fetch_files(self, history):
    files_list = get_files(history)
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
      except Exception, e:
        print 'could not index %s: %s' % (f['path'], e)
    return docs

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print IndexFiles.__doc__
    sys.exit(1)

  # Start Java VM
  #print 'lucene', lucene.VERSION
  start = datetime.now()
  #try:
  indexer = IndexFiles()
  FolderManager().follow(sys.argv[1])
  indexer.index_folder(sys.argv[1])
  end = datetime.now()
  print end - start
  #except Exception, e:
   # print "Failed: ", e

