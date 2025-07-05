-- Script para otimizar a tabela de eventos com índices
-- Execute este script no banco de dados PostgreSQL

-- 1. Índice composto para consultas por visualização e hora de exibição
-- Este é o índice mais importante para o funcionamento otimizado
CREATE INDEX IF NOT EXISTS idx_eventos_viz_hora 
ON eventos (visualization, hora_exibicao);

-- 2. Índice para consultas de eventos ativos (por hora_fim)
CREATE INDEX IF NOT EXISTS idx_eventos_fim 
ON eventos (hora_fim);

-- 3. Índice para consultas por CPF
CREATE INDEX IF NOT EXISTS idx_eventos_cpf 
ON eventos (cpf);

-- 4. Índice para consultas de eventos ativos por visualização
CREATE INDEX IF NOT EXISTS idx_eventos_viz_ativo 
ON eventos (visualization, hora_exibicao, hora_fim);

-- 5. Índice para buscar último evento de uma visualização
CREATE INDEX IF NOT EXISTS idx_eventos_viz_ultimo 
ON eventos (visualization, hora_fim DESC);

-- Verificar se os índices foram criados
SELECT 
    indexname, 
    tablename, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'eventos' 
ORDER BY indexname;

-- Análise da tabela para otimização
ANALYZE eventos;

-- Estatísticas dos índices
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes 
WHERE tablename = 'eventos'
ORDER BY idx_scan DESC; 