#!/usr/bin/env python3
"""
Script de migração para adicionar novos campos à tabela schedule_entries
"""

import os
from sqlalchemy import create_engine, text
import pytz

# Configuração de timezone para Brasília
TIMEZONE = pytz.timezone('America/Sao_Paulo')

# PostgreSQL database configuration
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'postgres')
DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'gestao_img')

# Configure PostgreSQL database
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
engine = create_engine(DATABASE_URL)

def migrate_schedule_entries():
    """Migra a tabela schedule_entries para incluir os novos campos"""
    
    with engine.connect() as conn:
        try:
            # Verifica se os campos já existem
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'schedule_entries' 
                AND column_name IN ('visualization_name', 'display_time', 'display_datetime')
            """))
            
            existing_columns = {row[0]: row[1] for row in result}
            
            if 'visualization_name' not in existing_columns:
                print("Adicionando campo visualization_name...")
                conn.execute(text("ALTER TABLE schedule_entries ADD COLUMN visualization_name VARCHAR"))
                conn.commit()
                print("Campo visualization_name adicionado!")
            
            if 'display_time' not in existing_columns:
                print("Adicionando campo display_time...")
                conn.execute(text("ALTER TABLE schedule_entries ADD COLUMN display_time TIME"))
                conn.commit()
                print("Campo display_time adicionado!")
            
            if 'display_datetime' not in existing_columns:
                print("Adicionando campo display_datetime...")
                conn.execute(text("ALTER TABLE schedule_entries ADD COLUMN display_datetime TIMESTAMP WITH TIME ZONE"))
                conn.commit()
                print("Campo display_datetime adicionado!")
            elif existing_columns['display_datetime'] == 'timestamp without time zone':
                print("Convertendo display_datetime para timezone-aware...")
                conn.execute(text("ALTER TABLE schedule_entries ALTER COLUMN display_datetime TYPE TIMESTAMP WITH TIME ZONE"))
                conn.commit()
                print("Campo display_datetime convertido!")
            
            print("Migração concluída com sucesso!")
            
        except Exception as e:
            print(f"Erro durante a migração: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    print("Iniciando migração da tabela schedule_entries...")
    migrate_schedule_entries()
    print("Migração finalizada!") 