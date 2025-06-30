-- Script para limpar registros duplicados da tabela schedule_entries
-- Remove registros com ID no formato antigo (cpf_entrytime_waittime_delay)
-- Mantém apenas registros com ID no formato correto (cpf_visualizationX_YYYYMMDD_HHMMSS)

-- Primeiro, vamos ver quantos registros existem
SELECT 'Total de registros antes da limpeza:' as info, COUNT(*) as total FROM schedule_entries;

-- Mostra os registros que serão removidos (formato antigo)
SELECT 'Registros que serão removidos (formato antigo):' as info;
SELECT id, cpf, visualization_name, display_datetime 
FROM schedule_entries 
WHERE id NOT LIKE '%_visualization%_%' 
   OR id LIKE '%_%_%_%_%' 
   OR id LIKE '%_%_%_%_%_%';

-- Remove registros com formato antigo de ID
DELETE FROM schedule_entries 
WHERE id NOT LIKE '%_visualization%_%' 
   OR id LIKE '%_%_%_%_%' 
   OR id LIKE '%_%_%_%_%_%';

-- Mostra quantos registros restaram
SELECT 'Total de registros após a limpeza:' as info, COUNT(*) as total FROM schedule_entries;

-- Mostra os registros restantes
SELECT 'Registros restantes:' as info;
SELECT id, cpf, visualization_name, display_datetime 
FROM schedule_entries 
ORDER BY display_datetime; 