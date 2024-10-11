from scrapper import CensusExtractor
from zip_parser import ZipParser

def main():
    
    zip_dir = 'zipfiles'
    unzip_dir = 'extraction'
    
    extractor = CensusExtractor(zip_dir)
    
    if not extractor.run():
        print("Terminating execution")
        return
    
    unzipper = ZipParser(unzip_dir)
    unzipper.run(zip_dir, extractor.get_zip_list())
    
    
    

if __name__ == "__main__":
    main()