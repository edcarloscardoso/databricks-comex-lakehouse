# Rascunho — Post #1 no LinkedIn (Episódio 1)

## Sugestão de Carrossel / Imagens para Anexar (3 a 4 prints)
1. **Print 1 (Capa ou Arquitetura):** Diagrama da Arquitetura Medallion (`MDIC -> Volume -> Bronze -> Silver -> Gold -> BI`).
2. **Print 2 (VS Code / Código como Infraestrutura):** Arquivo `databricks.yml` e `resources/setup_unity_catalog_job.yml` lado a lado no VS Code.
3. **Print 3 (Terminal):** Saída do `databricks bundle validate -t dev` + `databricks bundle deploy -t dev` + `databricks bundle run setup_unity_catalog_job -t dev` com sucesso.
4. **Print 4 (Databricks UI - Catalog Explorer):** Árvore do Unity Catalog mostrando `workspace -> comex_dev_raw (Volume mdic_landing) / comex_dev_bronze / comex_dev_silver / comex_dev_gold`.

---

## Texto Pronto para Publicar (Ajuste com seu tom pessoal)

Comecei hoje uma nova jornada prática rumo à certificação **Databricks Certified Data Engineer Associate** — e decidi construir tudo em público (**Build in Public**) usando dados reais do governo brasileiro.

A base escolhida foi a **Base Bruta de Comércio Exterior do MDIC (Comex Stat)** — milhões de registros reais de Exportações, Importações, NCMs, Países, Portos e Modais de Transporte.

Mas, antes de escrever uma única linha de PySpark, fiz questão de começar pelo que diferencia um estudo de laboratório de um projeto de Engenharia de Dados de mercado: **a fundação e a Infraestrutura como Código (IaC)**.

### O que construí no Episódio 1 (Setup do Zero):

1. **Zero tokens soltos no código:** conectei meu ambiente local (Linux + VS Code) ao **Databricks Free Edition** usando o Databricks CLI com autenticação moderna **OAuth U2M** (`databricks auth login --profile comex-free`).
2. **Databricks Asset Bundles (DABs):** em vez de criar notebooks e jobs clicando na interface web, versionei toda a estrutura do projeto em Git (`databricks.yml` + `resources/*.yml`), já separando targets de `dev` e `prod`.
3. **Compute Serverless + Job como Código:** criei um **Lakeflow Job** 100% Serverless que executa um notebook idempotente para provisionar a estrutura no **Unity Catalog**.
4. **Governança desde o Dia 1 (Unity Catalog):**
   - Namespace de 3 níveis (`catalog.schema.object`)
   - Schemas Medallion: `raw`, `bronze`, `silver` e `gold`
   - Um **Managed Volume** (`/Volumes/workspace/comex_dev_raw/mdic_landing`) para substituir o antigo DBFS na aterrissagem dos arquivos CSV brutos.
5. **Segurança no código SQL:** usei `IDENTIFIER(:param)` com validação estrita de identificadores no Spark SQL para evitar concatenação insegura de strings em DDL.

Tudo validado e provisionado com 3 comandos:
- `databricks bundle validate -t dev`
- `databricks bundle deploy -t dev`
- `databricks bundle run setup_unity_catalog_job -t dev`

### Próximo Episódio (Ep. 2):
Vamos baixar os CSVs oficiais de Exportação, Importação e Tabelas Auxiliares do MDIC para o nosso Volume e compararmos na prática **Auto Loader (`cloudFiles`) vs `COPY INTO`** na camada **Bronze**!

Se você também está estudando para certificações de dados ou trabalhando com Databricks, me conta aqui nos comentários: você já usa **Databricks Asset Bundles (DABs)** nos seus projetos ou ainda faz deploy manual?

#EngenhariaDeDados #Databricks #DataEngineering #UnityCatalog #Lakehouse #PySpark #DeltaLake #BuildInPublic #ComexStat
