from zipfile import ZipFile
import os

class ZipParser:
    def __init__(self, dir):
        self.dir = dir    
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)