from zipfile import ZipFile
import os
import pandas as pd

class ZipParser:
    def __init__(self, dir): 
        """
        Initialize a ZipParser object.

        Parameters
        ----------
        dir : str
            Path to the directory where the zip files are located.

        Attributes
        ----------
        dir : str
            Path to the directory where the zip files are located.
        unzip_list : list
            List of unzipped files.
        df_country, df_district, df_region : pandas.DataFrame
            DataFrames to store the data from the unzipped files.

        Returns
        -------
        None
        """
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        self.dir = dir   
        self.unzip_list = list()
        
        self.df_country = pd.DataFrame(columns=['state', 'gini'])
        self.df_district = pd.DataFrame(columns=['state', 'gini','country_id'])
        self.df_region = pd.DataFrame(columns=['state', 'gini','district_id'])
            
    def get_unzip_list(self):
        """
        Get the list of unzipped files.

        Returns
        -------
        list
            List of unzipped files.
        """
        return self.unzip_list
    
    def __unzip_file(self, file_dir):
        """
        Unzip a zip file and add the extracted file name to the unzip_list.

        Parameters
        ----------
        file_dir : str
            Path to the zip file to be unzipped.

        Returns
        -------
        None
        """
        try:
            with ZipFile(file_dir, 'r') as zipObj:
                zipObj.extractall(path=self.dir)
                self.unzip_list += (zipObj.namelist())
                zipObj.close()
        except FileNotFoundError:
            print(f"Error: The file {file_dir} was not found.")
        except PermissionError:
            print(f"Error: Insufficient permissions to read the file {file_dir}.")
        except Exception as e:
            print(f"An error occurred while extracting {file_dir}: {e}")

    def __create_dataframes(self):
        """
        Create DataFrames for country, district and region from the unzipped files.

        It reads each Excel file, extracts the state and Gini index columns, and assigns them to the
        appropriate DataFrame. 
        The DataFrames are cleaned,renamed and reordered to match the expected format of the DB tables.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        df_country = pd.DataFrame(columns=['state', 'gini'])
        df_district = pd.DataFrame(columns=['state', 'gini','country_id'])
        df_region = pd.DataFrame(columns=['state', 'gini','district_id'])
        
        for file in self.unzip_list:
            df = pd.read_excel(self.dir + "/" + file)
            df.columns = ['state','gini']
            df.gini = df.gini.replace("...", None)
            df.dropna(subset=['state'],inplace=True)
            
            df_country = pd.concat([df_country, df.iloc[0:1].copy()], ignore_index=True)
            df_country.drop_duplicates(inplace=True)
            country_id = df_country.index.max()
            
            df1 = df.iloc[1:2].copy()
            df1['country_id'] = country_id

            df_district = pd.concat([df_district, df1], ignore_index=True)
            df_district.drop_duplicates(inplace=True)
            district_id = df_district.index.max()
            
            df2 = df.iloc[2:].copy()
            df2['district_id'] = district_id
            
            df_region = pd.concat([df_region,df2], ignore_index=True)
            df_region.drop_duplicates(inplace=True)
            df_region.state = df_region.state.str.replace(' - ..$', '', regex=True)
            
            
        df_country.columns = ['country_name','gini_index']
        df_district.columns = ['district_name','gini_index','country_id']
        df_region.columns = ['region_name','gini_index','district_id']

        df_district = df_district[['country_id','district_name','gini_index']]
        df_region = df_region[['district_id','region_name','gini_index']]

        df_country = df_country.reset_index()
        df_country.rename(columns={'index': 'country_id'}, inplace=True)
        df_district = df_district.reset_index()
        df_district.rename(columns={'index': 'district_id'}, inplace=True)
        df_region = df_region.reset_index()
        df_region.rename(columns={'index': 'region_id'}, inplace=True)

        self.df_country = df_country.copy()
        self.df_district = df_district.copy()
        self.df_region = df_region.copy()
                      
    def run(self, zip_dir, file_list):
        """
        Parse a list of zip files and return the resulting DataFrames.

        Parameters
        ----------
        zip_dir : str
            Path to the directory containing the zip files.
        file_list : list
            List of zip file names to parse.

        Returns
        -------
        tuple
            A tuple of three DataFrames, one for country, district, and region data, respectively.
        """
        print("Beginning to parse zip files...")
        for file in file_list:
            path = f"{zip_dir}/{file}"
            if os.path.isfile(path):
                print(f"Unzipping {file}")
                self.__unzip_file(path)
            else:
                print(f"{file} not found")
                
        self.__create_dataframes()
        
        return self.df_country, self.df_district, self.df_region            
    