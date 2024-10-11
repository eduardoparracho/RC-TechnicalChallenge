import requests
import bs4
import os
class CensusExtractor():
    def __init__(self,dir):
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        self.dir = dir
        self.zip_list = list()
        
    def fetch_zip_list(self):
               
        try:
            response = requests.get("https://ftp.ibge.gov.br/Censos/Censo_Demografico_1991/Indice_de_Gini")
        except requests.exceptions.ConnectionError as e:
            return e
            
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table')
            rows = table.find_all('tr')
            for row in rows[1:]:
                cols = row.find_all('td')
                for el in cols:
                    if '.zip' in el.text:
                        self.zip_list.append(el.text.rstrip())
        
        return response.status_code
    
    def download_zip(self,region_zip):
        try:
            response = requests.get(f"https://ftp.ibge.gov.br/Censos/Censo_Demografico_1991/Indice_de_Gini/{region_zip}")
        except requests.exceptions.ConnectionError as e:
            return e
            
        if response.status_code == 200:
            path = f"{self.dir}/{region_zip}" 
            
            with open(path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                file.close()
            
        return response.status_code

    def run(self):
        status = self.fetch_zip_list()
        if status != 200:
            print(f"Unable to access IBGE - {status}")
            return 0
        
        if len(self.zip_list) == 0:
            print("No region files found")
            return 0
        else:
            print(f"{len(self.zip_list)} region files found: {self.zip_list}")
            
        for region_zip in self.zip_list:
            stauts = self.download_zip(region_zip)
            if stauts != 200:
                print(f"Error when attempting to download {region_zip} - {stauts}")
                return 0
            else:
                print(f"Downloaded {region_zip} Sucessfully")
        print("Done")
        return 1