import time
import sys

import lucene

from config import *
from libs.filehandle import get_last_modified

def parse_command(command):
  '''
    Receives the input line command given by the user and parses it to get
    the keyword and the languages to search in
    
    Command examples:
      keyword  --> searches in the default language
      keyword -l all  --> searches in all languages
      keyword -l english spanish romanian  --> searches in these 3 languages
  '''
  params = command.split(' -l ')
  keyword = params[0]
  if len(params) == 1:
    # No given language - use default
    languages = SUPPORTED_LANGUAGES
  else:
    l = params[1].lower()
    # A list of languages -> parse them
    l = l.split(' ')
    languages = []
    for language in l:
      if language in SUPPORTED_LANGUAGES:
        languages.append(language)
    if not languages:
      languages = SUPPORTED_LANGUAGES
  # Capitalize languages
  for i in range(0, len(languages)):
    languages[i] = languages[i].capitalize()
  return (keyword, languages)

def run(searcher, keyword, languages):
  if len(languages) < 4:
    print "Searching for \"%s\" in the language(s) %s" % \
            (keyword, ', '.join(languages))
  else:
    print "Searching for \"%s\" in %s languages" % \
            (keyword, len(languages))
  
  # Construct a list of search results for the requested languages
  scoreDocs = []
  total_count = 0
  for language in languages:
    analyzer_content = lucene.SnowballAnalyzer(lucene.Version.LUCENE_CURRENT, \
                                      language)
    filter = lucene.FieldCacheTermsFilter("language", [language])
    query_content = lucene.QueryParser(lucene.Version.LUCENE_CURRENT, "content",
                              analyzer_content).parse(keyword)
    analyzer_title = lucene.StandardAnalyzer(lucene.Version.LUCENE_CURRENT)
    query_title = lucene.WildcardQuery(lucene.Term("name", "*%s*" % keyword))
    
    query = lucene.BooleanQuery()
    query.add(query_content, lucene.BooleanClause.Occur.SHOULD)
    query.add(query_title, lucene.BooleanClause.Occur.SHOULD)
            
    results = searcher.search(query, filter, 50).scoreDocs
    if len(results) > 0:
      total_count += len(results)
      scoreDocs.append({'query': query,
                        'analyzer': analyzer_content,
                        'results': results,
                        'language': language})
  print "%s total matching documents." % total_count
  
  # Format and print the results with excerpt highlighting
  formatter = lucene.SimpleHTMLFormatter("<<<", ">>>")
  fragmenter = lucene.SimpleFragmenter(50)
  for dex in scoreDocs:
    print 'Results in %s:' % dex['language']
    i = 1
    for scoreDoc in dex['results']:
      doc = searcher.doc(scoreDoc.doc)
      stream = lucene.TokenSources.getAnyTokenStream(searcher.getIndexReader(),\
                              scoreDoc.doc, 'content', doc, dex['analyzer'])
      content = doc['content']
      scorer = lucene.QueryScorer(dex['query'])
      highlighter = lucene.Highlighter(formatter, scorer)
      highlighter.setTextFragmenter(fragmenter)
      fragment = highlighter.getBestFragment(stream, content)
      print '%s)   path: %s' % (i, doc.get("path"))
      print '     fragment: %s' % fragment
      i += 1

if __name__ == '__main__':
  lucene.initVM()
  print 'lucene', lucene.VERSION
  passed = time.time() - get_last_modified(STORE_DIR)
  
  args = sys.argv[1:]
  args = ' '.join(args)
  keyword, languages = parse_command(args)
  
  passed = int(passed / 86400)
  if passed == 0:
    print 'Index updated less than a day ago.'
  elif passed == 1:
    print 'Index updated yesterday.'
  else:
    print 'Index updated %s days ago.' % passed
  directory = lucene.SimpleFSDirectory(lucene.File(STORE_DIR))
  searcher = lucene.IndexSearcher(directory, True)
  run(searcher, keyword, languages)
  searcher.close()

