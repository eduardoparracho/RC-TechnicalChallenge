import sqlite3
import pandas as pd
from typing import Literal
import os

class Connector:
    def __init__(self,db_path):
    
        """
        Initialize a Connector object and set up the database.

        Parameters
        ----------
        db_path : str
            The name of the database file.

        Returns
        -------
        int
            Returns 1 if the database is newly created with tables, 
            otherwise returns 0 if the database already exists.
        """
    
        self.db_path = db_path
        self.status = 0
        
        if not self.__check_for_db(): 
            self.__create_tables()
            self.status = 1
        else:
            self.status = 0
        
    def get_db_status(self):
        return self.status
    
    def __check_for_db(self):
        if os.path.isfile(self.db_path):
            return 1
        else:
            return 0
        
        
    def __create_tables(self):
        """
        Create the tables in the database if they don't exist.

        Countries table - country_id, country_name, gini_index
        Districts table - district_id, country_id, district_name, gini_index
        Regions table - region_id, district_id, region_name, gini_index

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Countries (
                country_id INTEGER PRIMARY KEY,
                country_name TEXT NOT NULL,
                gini_index REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Districts (
                district_id INTEGER PRIMARY KEY,
                country_id INTEGER,
                district_name TEXT NOT NULL,
                gini_index REAL,
                FOREIGN KEY (country_id) REFERENCES Country(country_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Regions (
                region_id INTEGER PRIMARY KEY,
                district_id INTEGER,
                region_name TEXT NOT NULL,
                gini_index REAL,
                FOREIGN KEY (district_id) REFERENCES Districts(district_id)
            )
        ''')
        conn.commit()
        conn.close()
        return 1
    
    def populate_tables(self,df_country:pd.DataFrame,df_district:pd.DataFrame,df_region:pd.DataFrame):
        """
        Populate the tables in the database with the given DataFrames.

        Parameters
        ----------
        df_country : pandas.DataFrame
            DataFrame with columns 'country_id','country_name' and 'gini_index'.
        df_district : pandas.DataFrame
            DataFrame with columns 'district_id', 'district_name', 'gini_index', and 'country_id'.
        df_region : pandas.DataFrame
            DataFrame with columns 'region_id', 'region_name', 'gini_index', and 'district_id'.

        Returns
        -------
        int
            1 if successful, otherwise an sqlite3.OperationalError
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                df_country.to_sql('Countries', conn, if_exists='replace',index=False)
                df_district.to_sql('Districts', conn, if_exists='replace',index=False)
                df_region.to_sql('Regions', conn, if_exists='replace',index=False)
        except sqlite3.OperationalError as e:
            return e
        return 1
    
    def query_from_db(self,sql):
        """
        Execute a SQL query in the database and return the result.

        Parameters
        ----------
        sql : str
            SQL query to execute.

        Returns
        -------
        list
            List of tuples with the result of the query. If an sqlite3.OperationalError occurs, returns the error.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute(sql)
                res = cur.fetchall()
                conn.commit()
        except sqlite3.OperationalError as e:
            return e
        return res
    
    def get_gini_from_db(self,type:Literal["single", "all"] = "single",country=None,district=None,region=None):
        """
        Get the Gini index for a given country, district, or region.

        Parameters
        ----------
        type : str, optional
            Type of query to execute. 'single' will return the Gini index for the given
            country, district, or region. 'all' will return the Gini index for all districts
            in the given country, or all regions in the given district. The default is 'single'.
        country : str, optional
            Country name to query.
        district : str, optional
            District name to query.
        region : str, optional
            Region name to query.

        Returns
        -------
        list
            List of tuples with the result of the query. The first element of the tuple is the
            name of the country, district, or region, and the second element is the Gini index.
            If an sqlite3.OperationalError occurs, returns the error.
        """
        
        if region:
            sql = f"SELECT region_name,gini_index FROM Regions WHERE region_name = '{region}'"
        elif district:
            if type == 'single':
                sql = f"SELECT district_name,gini_index FROM Districts WHERE district_name = '{district}'"
            if type == 'all':
                sql = f"SELECT region_name,gini_index FROM Regions WHERE district_id IN (SELECT district_id FROM Districts WHERE district_name = '{district}')"
        elif country:
            if type == 'single':
                sql = f"SELECT country_name,gini_index FROM Countries WHERE country_name = '{country}'"
            if type == 'all':
                sql = f"SELECT district_name,gini_index FROM Districts WHERE country_id IN (SELECT country_id FROM Countries WHERE country_name = '{country}')"
        
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(sql)
            gini = cur.fetchall()
            
        return gini
    
        