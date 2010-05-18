'''
  Least recently updated cache
'''

#TODO(ditzone): Method to remove a key.

class LRUCache(object):
  '''
    A dicitonary with fixed size. We keep a queue with all the keys.
    When a key is accesed we move the key to the end of the queue.
    When we need to delete a key we remove the key from the beginning
    of the queue.
  '''

  def __init__(self, size):
    self._dex = {}
    self._size = size
    self._head = None
    self._end = None

  def __len__(self):
    return len(self._dex)

  def __contains__(self, key):
    if self._dex.has_key(key):
      self._refresh_key(key)
      return True
    else:
      return False

  def __setitem__(self, key, value):
    if (len(self._dex) >= self._size) and (key not in self._dex):
      obsolete = self._head
      self._head = self._dex[self._head]['next']
      del self._dex[self._head]['prev']
      del self._dex[obsolete]
    if key not in self._dex:
      self._dex[key] = {'val': value}
    else:
      self._dex[key]['val'] = value
    self._refresh_key(key)

  def __getitem__(self, key):
    if key in self._dex:
      self._refresh_key(key)
      return self._dex[key]['val']
    raise Exception('Key Error: %s' % key)

  def _refresh_key(self, key):
    if self._end == key:
      return
    item = self._dex[key]
    if 'prev' in item:
      if 'next' in item:
        self._dex[item['prev']]['next'] = item['next']
      else:
        del self._dex[item['prev']]['next']
        self._end = item['prev']
    if 'next' in item:
      if 'prev' in item:
        self._dex[item['next']]['prev'] = item['prev']
      else:
        del self._dex[item['next']]['prev']
        self._head = item['next']
    if self._end is not None:
      self._dex[self._end]['next'] = key
      item['prev'] = self._end
      self._end = key
    else:
      self._end = self._head = key
    if 'next' in item:
      del item['next']

  def __iter__(self):
    if self._head is None:
      raise StopIteration
    key = self._head
    while 'next' in self._dex[key]:
      yield key
      key = self._dex[key]['next']
    yield key
    raise StopIteration

if __name__ == "__main__":
  cache = LRUCache(25)
  for i in range(50):
    cache[i] = str(i)
  print '46', cache[46]
  print 46 in cache
  print 5 in cache
  for c in cache:
    print c
