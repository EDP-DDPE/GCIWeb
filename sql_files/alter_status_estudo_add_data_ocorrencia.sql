-- Adiciona a data de ocorrência do status (informada pelo usuário),
-- separada da data de cadastro do registro (coluna `data`).
-- Executar uma vez no banco (SQL Server).

IF NOT EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('gciweb.status_estudo')
      AND name = 'data_ocorrencia'
)
BEGIN
    ALTER TABLE gciweb.status_estudo ADD data_ocorrencia DATE NULL;
END
GO
