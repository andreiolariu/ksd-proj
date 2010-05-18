import signal
import pyinotify
import time
import Queue

from index import IndexFiles

from libs.indexmanager import FolderManager

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
      self.queue = queue
    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname
        self.queue.put(('+', event.pathname))
        #self.indexer.index(None, {'+': event.pathname})

    def process_IN_DELETE(self, event):
        print "Removing:", event.pathname
        self.queue.put(('-', event.pathname))
        #self.indexer.index(None, {'-': event.pathname})

    def process_IN_MODIFY(self, event):
        print "Modifying:", event.pathname
        self.queue.put(('-', event.pathname))
        self.queue.put(('+', event.pathname))
        #self.indexer.index(None, {'-': event.pathname, '+': event.pathname})

class Monitor(object):

  def __init__(self):
    self.runsignal = True
    signal.signal(signal.SIGINT, self.sigint_handler)

    # The watch manager stores the watches and provides operations on watches
    self.wm = pyinotify.WatchManager()

    self.queue = Queue.Queue()
    handler = HandleEvents(self.queue)
    self.notifier = pyinotify.ThreadedNotifier(self.wm, handler)
    self.notifier.start()
    self.manager = FolderManager()

  def run(self):
    indexer = IndexFiles()
    while self.runsignal:
      for folder in self.manager.get_followed():
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY
        self.wm.add_watch(folder, mask, rec=True)
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
  monitor = Monitor()
  monitor.run()
  print 'Monitor stopped.'
