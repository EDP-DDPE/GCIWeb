from app.models import db
import pandas as pd


def get_schema_from_sqlserver():
    """
    Retorna um schema compacto contendo:
    - tabelas
    - colunas
    - tipos
    - PK
    - FK
    Em formato de texto pronto para colocar no prompt do LLM.
    """

    engine = db.engine

    # 1) TABELAS E COLUNAS
    query_columns = """
        SELECT 
            TABLE_SCHEMA,
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'gciweb'
        ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION;
    """

    df_cols = pd.read_sql(query_columns, engine)

    # 2) CHAVES PRIMÁRIAS
    query_pk = """
        SELECT
            KU.TABLE_SCHEMA,
            KU.TABLE_NAME,
            KU.COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS TC
        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS KU
            ON TC.CONSTRAINT_TYPE = 'PRIMARY KEY'
            AND TC.CONSTRAINT_NAME = KU.CONSTRAINT_NAME
        ORDER BY KU.TABLE_SCHEMA, KU.TABLE_NAME, KU.ORDINAL_POSITION;
    """

    df_pk = pd.read_sql(query_pk, engine)

    # 3) CHAVES ESTRANGEIRAS
    query_fk = """
        SELECT
            FK.TABLE_SCHEMA AS FK_SCHEMA,
            FK.TABLE_NAME AS FK_TABLE,
            CU.COLUMN_NAME AS FK_COLUMN,
            PK.TABLE_SCHEMA AS PK_SCHEMA,
            PK.TABLE_NAME AS PK_TABLE,
            PT.COLUMN_NAME AS PK_COLUMN
        FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS C
        INNER JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS FK
            ON C.CONSTRAINT_NAME = FK.CONSTRAINT_NAME
        INNER JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS PK
            ON C.UNIQUE_CONSTRAINT_NAME = PK.CONSTRAINT_NAME
        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE CU
            ON C.CONSTRAINT_NAME = CU.CONSTRAINT_NAME
        INNER JOIN (
            SELECT
                i1.TABLE_NAME,
                i2.COLUMN_NAME,
                i1.CONSTRAINT_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS i1
            INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE i2
                ON i1.CONSTRAINT_NAME = i2.CONSTRAINT_NAME
            WHERE i1.CONSTRAINT_TYPE = 'PRIMARY KEY'
        ) PT
            ON PT.CONSTRAINT_NAME = PK.CONSTRAINT_NAME
        ORDER BY FK.TABLE_SCHEMA, FK.TABLE_NAME;
    """

    df_fk = pd.read_sql(query_fk, engine)

    # ---------------------------------------------------------
    # MONTAR O TEXTO FINAL COMPACTO
    # ---------------------------------------------------------
    schema_text = []

    for (schema, table), group in df_cols.groupby(["TABLE_SCHEMA", "TABLE_NAME"]):
        schema_text.append(f"Tabela {schema}.{table}")

        # listar colunas
        for _, row in group.iterrows():
            col = row["COLUMN_NAME"]
            dtype = row["DATA_TYPE"]
            length = row["CHARACTER_MAXIMUM_LENGTH"]

            # tratar varchar(n)
            if length and dtype in ("varchar", "nvarchar"):
                dtype = f"{dtype}({length})"

            pk_flag = ""
            if ((df_pk["TABLE_NAME"] == table) &
                (df_pk["COLUMN_NAME"] == col)).any():
                pk_flag = " PK"

            # verificar FK
            fk_info = df_fk[
                (df_fk["FK_TABLE"] == table) &
                (df_fk["FK_COLUMN"] == col)
            ]

            if not fk_info.empty:
                fk = fk_info.iloc[0]
                fk_flag = f" FK → {fk['PK_SCHEMA']}.{fk['PK_TABLE']}.{fk['PK_COLUMN']}"
            else:
                fk_flag = ""

            schema_text.append(f"  - {col} ({dtype}){pk_flag}{fk_flag}")

        schema_text.append("")  # linha de espaço

    return "\n".join(schema_text)
