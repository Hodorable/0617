import sys
import logging
import time
import os
 
ref = time.strftime('%Y-%m-%d',time.localtime(time.time()))
filename = r'/opt/stack/logs/PolicyUI_'+ref+"_error.log"
def create_file(filename):
    if os.path.exists(filename):
      pass
    else:
      os.system(r'touch %s' % filename)
      f = open(filename, 'w')
      f.close()
def Log(message):
    if os.path.exists(filename):
      pass
    else:
      os.system(r'touch %s' % filename)
    logger=logging.getLogger() 
    handler=logging.FileHandler(filename)
    logger.addHandler(handler)
    logger.setLevel(logging.NOTSET)
    logger.info(message)
 
if __name__ == '__main__':
 
    Log("PolicyUI_Log")
