import requests
import bs4
import os
class CensusExtractor():
    def __init__(self,dir):
        """
        Initialize a CensusExtractor object.
        
        Parameters
        ----------
        dir : str
            Path to the directory where the zip files will be stored.
        
        Attributes
        ----------
        dir : str
            Path to the directory where the zip files are located.
        zip_list : list
            List of zip files.
        
        Returns
        -------
        None
        """
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.dir = dir
        self.zip_list = list()
        
    def get_zip_list(self):
        """
        Get the list of zip files.
        
        Returns
        -------
        list
            List of zip file names.
        """
        return self.zip_list
    
    def __fetch_zip_list(self):  
        """
        Fetch the list of zip files from the IBGE website.

        Returns
        -------
        int
            HTTP status code.
        """
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
    
    def __download_zip(self,district_zip):
        """
        Download a zip file from the IBGE website.

        Parameters
        ----------
        district_zip : str
            Name of the zip file to be downloaded.

        Returns
        -------
        int
            HTTP status code.
        """
        try:
            response = requests.get(f"https://ftp.ibge.gov.br/Censos/Censo_Demografico_1991/Indice_de_Gini/{district_zip}")
        except requests.exceptions.ConnectionError as e:
            return e
            
        if response.status_code == 200:
            path = f"{self.dir}/{district_zip}" 
            
            with open(path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                file.close()
            
        return response.status_code

    def run(self):
        """
        Download all zip files from the IBGE website.

        Returns
        -------
        int
            1 if successful, 0 if any error occurs.
        """
        status = self.__fetch_zip_list()
        if status != 200:
            print(f"Unable to access IBGE - {status}")
            return 0
        
        if len(self.zip_list) == 0:
            print("No region files found")
            return 0
        else:
            print(f"{len(self.zip_list)} region files found: {self.zip_list}")
            
        for district_zip in self.zip_list:
            stauts = self.__download_zip(district_zip)
            if stauts != 200:
                print(f"Error when attempting to download {district_zip} - {stauts}")
                return 0
            else:
                print(f"Downloaded {district_zip} Sucessfully")
        print("Done")
        return 1