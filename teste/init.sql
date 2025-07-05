-- Script de inicialização do banco de dados
-- Este arquivo é executado automaticamente quando o container PostgreSQL é criado

-- Criar tabelas se não existirem
CREATE TABLE IF NOT EXISTS cadastro (
    cpf TEXT PRIMARY KEY,
    caminho_imagem TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS parametros (
    nome TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eventos (
    id SERIAL PRIMARY KEY,
    cpf TEXT NOT NULL,
    visualization TEXT NOT NULL,
    hora_acesso TIME NOT NULL,
    delay INTERVAL NOT NULL,
    hora_exibicao TIME NOT NULL,
    hora_fim TIME NOT NULL
);

-- Inserir parâmetros padrão
INSERT INTO parametros (nome, valor) VALUES 
    ('tempo_inicial_segundos', '30'),
    ('incremento_segundos', '10'),
    ('duracao_exibicao_seg', '10')
ON CONFLICT (nome) DO NOTHING;

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_eventos_cpf ON eventos(cpf);
CREATE INDEX IF NOT EXISTS idx_eventos_visualization ON eventos(visualization);
CREATE INDEX IF NOT EXISTS idx_eventos_hora_exibicao ON eventos(hora_exibicao);
CREATE INDEX IF NOT EXISTS idx_eventos_hora_fim ON eventos(hora_fim);

-- Comentários sobre as tabelas
COMMENT ON TABLE cadastro IS 'Armazena CPFs e suas imagens em Base64';
COMMENT ON TABLE parametros IS 'Configurações do sistema (tempos, delays, etc.)';
COMMENT ON TABLE eventos IS 'Agendamentos de exibição para cada visualização';

-- Log de inicialização
SELECT 'Banco de dados inicializado com sucesso!' as status; 