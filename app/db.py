import os
import pytz
import uuid
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()
IST = pytz.timezone("Asia/Kolkata")


class RedirectionDatabase:
    def __init__(self):
        DATABASE_URL = os.environ["DATABASE_URL"]
        self.base = declarative_base()
        self.engine = create_engine(DATABASE_URL)
        self.connection = self.engine.connect()
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        logging.debug(f"Database connection established: {self}")
        self.setup_tables()

        self.redirection_table = Table(
            "redirection", self.metadata, autoload=True, autoload_with=self.engine
        )

    def setup_tables(self):
        with open("app/conf/setup_db.sql") as f:
            queries = f.read().strip().split("\n\n")
            for query in queries:
                try:
                    self.connection.execute(query)
                except Exception as e:
                    logging.error(f"Exception while executing query: {query}: {e}")

    def add_new_redirection_url(
        self, source_url, alias_name, create_time, ip_address, browser, platform
    ):
        query = self.redirection_table.insert().values(
            source_url=source_url,
            alias_name=alias_name,
            create_time=create_time,
            ip_address=ip_address,
            browser=browser,
            platform=platform,
        )
        self.connection.execute(query)

    def check_alias_exists(self, alias_name):
        query = self.redirection_table.select().where(
            self.redirection_table.c.alias_name == alias_name
        )
        result = self.connection.execute(query)
        return result.rowcount > 0

    def generate_random_alias_name(self):
        while True:
            alias_name = str(uuid.uuid1().hex[:5])
            if not self.check_alias_exists(alias_name):
                return alias_name

    def get_source_url_from_alias_name(self, alias_name):
        query = self.redirection_table.select().where(
            self.redirection_table.c.alias_name == alias_name
        )
        result = self.connection.execute(query)
        if result.rowcount > 0:
            return result.fetchone().source_url
        else:
            return None


    def get_all_urls_from_ip(self, ip_address):
        query = self.redirection_table.select().where(
            self.redirection_table.c.ip_address == ip_address
        )
        all_results = self.connection.execute(query).fetchall()
        result = []
        for row in all_results:
            (source_url, alias_name, create_time, ip_address, browser, platform) = row
            result.append(
                {
                    "source_url": source_url,
                    "alias_name": alias_name,
                }
            )
        return result

