import sqlite3
import pandas as pd
from typing import Literal
class Connector:
    def __init__(self,db_name):
        self.db_name = db_name
        self.create_tables()
        
        
    def create_tables(self):
        conn = sqlite3.connect(self.db_name)
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
        try:
            with sqlite3.connect(self.db_name) as conn:
                df_country.to_sql('Countries', conn, if_exists='replace',index=False)
                df_district.to_sql('Districts', conn, if_exists='replace',index=False)
                df_region.to_sql('Regions', conn, if_exists='replace',index=False)
        except sqlite3.OperationalError as e:
            return e
        return 1
    
    def query_from_db(self,sql):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cur = conn.execute(sql)
                res = cur.fetchall()
        except sqlite3.OperationalError as e:
            return e
        return res
    
    def get_gini_from_db(self,type:Literal["single", "all"] = "single",country=None,district=None,region=None):
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
        
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.execute(sql)
            gini = cur.fetchall()
            
        return gini
    
        