from scrapper import CensusExtractor

def main():
    zip_dir = 'zipfiles'
    extractor = CensusExtractor(zip_dir)
    
    if not extractor.run():
        print("Terminating execution")
        return
    
    
    

if __name__ == "__main__":
    main()