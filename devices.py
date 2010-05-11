import subprocess
import os
import time

def run(command):
  try:
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True,
        close_fds=True)
  except Exception, e:
    return None
  return proc.stdout.read()

def get_devices():
  global last_modified
  res = []
  data = run('./devices | cut -f 1,3 -d \' \'')
  new_last_modified = 0
  for line in data.split('\n'):
    if line.startswith('/dev'):
      A = line.split(' ')
      x = os.path.getmtime(A[0])
      if last_modified < x + 0.001:
        res.append(A[1])
        new_last_modified = max(new_last_modified, x + 0.01)
  last_modified = max(new_last_modified, last_modified)
  return res

last_modified = time.time()
while True:
  A = get_devices()
  if len(A) > 0:
    print A
  time.sleep(0.8)
