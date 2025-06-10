import os
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, LargeBinary, DateTime
from datetime import datetime
import sqlite3
import io

# PostgreSQL database configuration
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'postgres')
DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'gestao_img')

# Configure PostgreSQL database
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
engine = create_engine(DATABASE_URL)

def migrate():
    metadata = MetaData()
    
    # Define the images table
    images = Table('images', metadata,
        Column('cpf', String, primary_key=True),
        Column('image_data', LargeBinary, nullable=False),
        Column('content_type', String, nullable=False),
        Column('created_at', DateTime, default=datetime.utcnow)
    )
    
    try:
        # Create the table in PostgreSQL
        metadata.create_all(engine)
        print("PostgreSQL tables created successfully!")
        
        # Check if old SQLite database exists and migrate data if needed
        sqlite_path = os.path.join('data', 'images.db')
        if os.path.exists(sqlite_path):
            print("Found old SQLite database, migrating data...")
            migrate_from_sqlite(sqlite_path, engine)
            print("Data migration completed!")
            
            # Optionally, rename old SQLite database as backup
            backup_path = os.path.join('data', 'images.db.backup')
            os.rename(sqlite_path, backup_path)
            print(f"Old database backed up to {backup_path}")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        raise

def migrate_from_sqlite(sqlite_path, pg_engine):
    # Connect to SQLite database
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        # Get all records from SQLite
        sqlite_cursor.execute("SELECT cpf, image_data, content_type, created_at FROM images")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print("No data to migrate from SQLite")
            return
        
        # Insert records into PostgreSQL
        with pg_engine.connect() as pg_conn:
            for row in rows:
                cpf, image_data, content_type, created_at = row
                pg_conn.execute(
                    text("""
                        INSERT INTO images (cpf, image_data, content_type, created_at)
                        VALUES (:cpf, :image_data, :content_type, :created_at)
                        ON CONFLICT (cpf) DO UPDATE SET
                        image_data = EXCLUDED.image_data,
                        content_type = EXCLUDED.content_type,
                        created_at = EXCLUDED.created_at
                    """),
                    {
                        'cpf': cpf,
                        'image_data': image_data,
                        'content_type': content_type,
                        'created_at': created_at
                    }
                )
            pg_conn.commit()
            
        print(f"Migrated {len(rows)} records from SQLite to PostgreSQL")
        
    finally:
        sqlite_cursor.close()
        sqlite_conn.close()

if __name__ == '__main__':
    migrate() 