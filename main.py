from scrapper import CensusExtractor

def main():
    extractor = CensusExtractor('zipfiles')
    if not extractor.run():
        print("Terminating execution")
        return
    

if __name__ == "__main__":
    main()