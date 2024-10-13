from scrapper import CensusExtractor
from zip_parser import ZipParser
from db_connector import Connector

def main():
    
    zip_dir = 'zipfiles'
    unzip_dir = 'extraction'
    db_name = 'census.db'
    
    extractor = CensusExtractor(zip_dir)
    
    if not extractor.run():
        print("Terminating execution - extraction failed")
        return
    
    unzipper = ZipParser(unzip_dir)
    df_country,df_district,df_region = unzipper.run(zip_dir, extractor.get_zip_list())
    
    if df_country.empty or df_district.empty or df_region.empty:
        print("Terminating execution - dataframe creation failed")
        return
    
    connector = Connector(db_name)
    connector.create_tables()
    if not connector.populate_tables(df_country,df_district,df_region):
        print("Terminating execution - table population failed")
        return
    
    print("Execution completed successfully")
    
    while True:
        inp = input('''\n\nYou can now access the table via commands. Type 'country=',district=' or region=' to automatically retrieve values from the db\n
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