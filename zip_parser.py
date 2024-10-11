from zipfile import ZipFile
import os

class ZipParser:
    def __init__(self, dir): 
        if not os.path.exists(dir):
            os.makedirs(dir)
            
        self.dir = dir   
        self.unzip_list = list()
            
    def get_unzip_list(self):
        return self.unzip_list
    
    def unzip_file(self, file_dir):
        with ZipFile(file_dir, 'r') as zipObj:
            zipObj.extractall(path=self.dir)
            self.unzip_list.append(zipObj.namelist())
            zipObj.close()

    def run(self, zip_dir, file_list):
        print("Beginning to parse zip files...")
        for file in file_list:
            path = f"{zip_dir}/{file}"
            if os.path.isfile(path):
                print(f"Unzipping {file}")
                self.unzip_file(path)
            else:
                print(f"{file} not found")
        
        