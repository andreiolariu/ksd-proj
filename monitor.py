import signal
import pyinotify
import time
import Queue

from index import IndexFiles

from libs.indexmanager import FolderManager
from libs.lrucache import LRUCache

def run(command):
  try:
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True,
        close_fds=True)
  except Exception, e:
    return None
  return proc.stdout.read()

class HandleEvents(pyinotify.ProcessEvent):
    def __init__(self, queue):
      pyinotify.ProcessEvent.__init__(self)
      self.lrucache = LRUCache(1000)
      self.queue = queue

    def recent(self, pathname):
      # Was this file just modified a few seconds ago?
      last_detection = 0
      if pathname in self.lrucache:
        last_detection = self.lrucache[pathname]
      self.lrucache[pathname] = time.time()
      return time.time() - last_detection < 2

    def process_IN_CREATE(self, event):
      if self.recent(event.pathname):
        return
      print "Creating:", event.pathname
      self.queue.put(('+', event.pathname))

    def process_IN_DELETE(self, event):
      if self.recent(event.pathname):
        return
      print "Removing:", event.pathname
      self.queue.put(('-', event.pathname))

    def process_IN_MODIFY(self, event):
      if self.recent(event.pathname):
        return
      print "Modifying:", event.pathname
      self.queue.put(('-', event.pathname))
      self.queue.put(('+', event.pathname))

class Monitor(object):

  def __init__(self):
    self.runsignal = True
    signal.signal(signal.SIGINT, self.sigint_handler)

    # The watch manager stores the watches and provides operations on watches
    self.wm = pyinotify.WatchManager()

    self.queue = Queue.Queue()
    handler = HandleEvents(self.queue)
    self.manager = FolderManager()
    self.notifier = pyinotify.ThreadedNotifier(self.wm, handler)
    self.notifier.start()

  def run(self):
    indexer = IndexFiles()
    while self.runsignal:
      for folder in self.manager.get_followed():
        if not self.wm.get_wd(folder):
          mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY #| pyinotify.IN_MOVED_TO
          self.wm.add_watch(folder, mask, rec=True)
          print 'Monitoring folder %s...' % folder
      try:
        data = self.queue.get(False)
      except:
        data = None
      if data:
        if data[0] == '+':
          indexer.index_files(add=[data[1]])
        else:
          indexer.index_files(remove=[data[1]])
      time.sleep(5)

  def sigint_handler(self, signal, frame):
    print 'Stopping monitor...'
    self.notifier.stop()
    self.runsignal = False

if __name__ == '__main__':
  print 'Starting monitor...'
  monitor = Monitor()
  monitor.run()
  print 'Monitor stopped.'
