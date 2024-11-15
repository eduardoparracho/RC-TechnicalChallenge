from scrapper import CensusExtractor
from zip_parser import ZipParser
from db_connector import Connector

def extract_data(extractor, unzipper, connector):
    
    """
    Orchestrates the extraction of data from the IBGE website and its population into a database.

    Parameters
    ----------
    extractor : CensusExtractor
        Object responsible for extracting the data from the IBGE website.
    unzipper : ZipParser
        Object responsible for unzipping the extracted data and creating DataFrames out of it.
    connector : Connector
        Object responsible for connecting to the database and populating it with the extracted data.

    Returns
    -------
    int
        1 if successful, otherwise 0
    """
    if not extractor.run():
        print("Terminating execution - extraction failed")
        return 0
    
    df_country,df_district,df_region = unzipper.run(extractor.get_zip_dir(), extractor.get_zip_list())
    if df_country.empty or df_district.empty or df_region.empty:
        print("Terminating execution - dataframe creation failed")
        return 0

    if not connector.populate_tables(df_country,df_district,df_region):
        print("Terminating execution - table population failed")
        return 0
    
    return 1
    
def main():
    
    """
    Main function of the program. It will download the zip files, extract them, parse them into DataFrames, 
    populate the database with the data, and then enter an optional command loop where you can query the database.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    zip_dir = 'zipfiles'
    unzip_dir = 'extraction'
    db_path = 'data/census.db'
    
    extractor = CensusExtractor(zip_dir)
    unzipper = ZipParser(unzip_dir)
    connector = Connector(db_path)
    db_status = connector.get_db_status()
    
    if db_status:
        print('No database found. Downloading data...')
        if extract_data(extractor,unzipper,connector):
            print("Execution completed successfully")
        else:
            return
    else:
        while True:
            inp = input(''' Database seems to already exist. Do you want to re-download data? (Y/N)''').lower()
            if inp == 'y':
                if extract_data(extractor,unzipper,connector):
                    print("Execution completed successfully")
                    break
                else:
                    return
            if inp != 'n' and inp != 'y':
                print('Type "Y" for Yes, "N" for No')
            if inp == 'n':
                break
            
    while True:   
        inp = input('''
    You can now access the table via commands. Type 'country=',district=' or region=' to automatically retrieve values from the db\n
    You can also use modifier 'type=all' to values from subsquent tables\n
    e.g. "country=Brasil,type=all" will retrieve gini values from all districts of Brasil\n
    and "district=Amazonas,type=all" will retrieve gini values from all regions of Amazonas\n
    You can also sql query normally by starting the input with 'query='\n
    Press enter to exit\n
              ''')
        
        if inp == "":
            break
        
        if inp.startswith("query="):
            print(connector.query_from_db(inp.lstrip("query=")))
            continue
        
        query = inp.split(",")

        if len(query) == 2 and query[1] == "type=all":
            type = 'all'
        elif (len(query) == 2 and query[1] == "type=single") or len(query) == 1:
            type = 'single'
        else:
            print("Invalid input")
            continue
            
        query = query[0].split("=")
        if query[0] == "country":
            result = connector.get_gini_from_db(country=query[1],type=type)
            print(result)
        elif query[0] == "region":
            result = connector.get_gini_from_db(region=query[1],type=type)
            print(result)
        elif query[0] == "district":
            result = connector.get_gini_from_db(district=query[1],type=type)
            print(result)
        else:
            print("Invalid input")
    
if __name__ == "__main__":
    main()