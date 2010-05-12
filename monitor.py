import signal
import pyinotify
import time

from libs.indexmanager import FolderManager

class HandleEvents(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname

    def process_IN_DELETE(self, event):
        print "Removing:", event.pathname

    def process_IN_MODIFY(self, event):
        print "Modifying:", event.pathname

class Monitor(object):

  def __init__(self):
    self.runsignal = True
    signal.signal(signal.SIGINT, self.sigint_handler)

    # The watch manager stores the watches and provides operations on watches
    self.wm = pyinotify.WatchManager()

    self.notifier = pyinotify.ThreadedNotifier(self.wm, HandleEvents())
    self.notifier.start()

    self.manager = FolderManager()

  def run(self):
    while self.runsignal:
      for folder in self.manager.get_followed():
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY
        self.wm.add_watch(folder, mask, rec=True)
      time.sleep(5)

  def sigint_handler(self, signal, frame):
    print 'Stopping monitor...'
    self.notifier.stop()
    self.runsignal = False

if __name__ == '__main__':
  monitor = Monitor()
  monitor.run()
  print 'Monitor stopped.'
