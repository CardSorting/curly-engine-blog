from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    help = 'Drop all tables and reset database'

    def handle(self, *args, **options):
        self.stdout.write('Dropping all tables...')
        
        with connection.cursor() as cursor:
            # Disable foreign key constraints temporarily
            cursor.execute('SET CONSTRAINTS ALL DEFERRED')
            
            # Get all table names
            cursor.execute("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # Drop all tables
            for table in tables:
                if table != 'django_migrations':  # Keep migrations table
                    cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                    self.stdout.write(f'Dropped table: {table}')
            
            # Clear migrations table
            cursor.execute('TRUNCATE TABLE django_migrations RESTART IDENTITY')
            
        self.stdout.write(self.style.SUCCESS('All tables dropped successfully!'))
