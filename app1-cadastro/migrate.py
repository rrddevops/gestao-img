import os
from sqlalchemy import create_engine, text
from datetime import datetime

# Configure SQLite database
DB_PATH = os.path.join('data', 'images.db')
os.makedirs('data', exist_ok=True)
engine = create_engine(f'sqlite:///{DB_PATH}')

def migrate():
    # Adiciona a coluna created_at se ela não existir
    with engine.connect() as conn:
        # Verifica se a coluna já existe
        result = conn.execute(text("SELECT name FROM pragma_table_info('images') WHERE name='created_at'"))
        column_exists = result.fetchone() is not None

        if not column_exists:
            print("Adicionando coluna created_at...")
            try:
                # Primeiro, tenta remover a tabela temporária se ela existir
                conn.execute(text("DROP TABLE IF EXISTS images_new"))
                
                # Cria uma tabela temporária com a nova estrutura
                conn.execute(text("""
                    CREATE TABLE images_new (
                        cpf TEXT PRIMARY KEY,
                        image_data BLOB NOT NULL,
                        content_type TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Verifica se a tabela original existe
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='images'"))
                if result.fetchone() is not None:
                    # Copia os dados existentes para a nova tabela
                    conn.execute(text("""
                        INSERT INTO images_new (cpf, image_data, content_type, created_at)
                        SELECT cpf, image_data, content_type, CURRENT_TIMESTAMP
                        FROM images
                    """))
                    
                    # Remove a tabela antiga
                    conn.execute(text("DROP TABLE images"))
                
                # Renomeia a nova tabela
                conn.execute(text("ALTER TABLE images_new RENAME TO images"))
                
                conn.commit()
                print("Coluna created_at adicionada com sucesso!")
            except Exception as e:
                print(f"Erro durante a migração: {str(e)}")
                conn.rollback()
                raise
        else:
            print("Coluna created_at já existe!")

if __name__ == '__main__':
    migrate() 