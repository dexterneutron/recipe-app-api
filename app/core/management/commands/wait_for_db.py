"""
Django command to wait for the database to be available.
"""
import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Entrypoint for command"""
        self.stdout.write("Waiting for database...")
        db_connnection = None
        while not db_connnection:
            try:
                self.check(databases=["default"])
                db_connnection = True
            except (OperationalError, Psycopg2Error):
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)
        self.stdout.write("Database available!")

    def check(self, *args, **options):
        pass
