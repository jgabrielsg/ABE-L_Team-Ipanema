# Manual Canônico de Dados e Conhecimento Demográfico — WPP 2024

> **Status:** Documento Vivo (Single Source of Truth)  
> **Versão:** 1.0 (Inicial — Fundamentos Estruturais, Regras Algorítmicas e Literatura Teórica)  
> **Equipe:** Team Ipanema (ABE-L) — ASA International Data Quest 2026  
> **Finalidade:** Centralizar todas as regras canônicas de processamento, definições de métricas, equações matemáticas e descobertas empíricas acumuladas pela equipe ao longo da competição.

---

## 1. Filosofia e Uso Deste Documento

Este manual é o repositório normativo do projeto. Qualquer membro da equipe, script de processamento ou agente autônomo deve seguir estritamente as regras de negócio e de filtragem aqui consolidadas.

* **Integridade:** Nenhum cálculo descritivo ou inferencial pode ser executado sem aplicar os filtros anti-dupla contagem.
* **Reprodutibilidade:** Toda equação implementada no pipeline de código deve corresponder exatamente à formulação matemática registrada nesta especificação.
* **Evolução Contínua:** Novas descobertas analíticas, calibrações de modelos ou anomalias empíricas encontradas na base devem ser registradas na **Seção 8 (Log Canônico de Descobertas)**.

---

## 2. Anatomia e Arquitetura dos Arquivos da ONU (WPP 2024)

Os dados provêm da 28ª revisão das Projeções Populacionais Mundiais das Nações Unidas (UN DESA Population Division).

### 2.1. Arquivos Oficiais Fornecidos

| Nome do Arquivo | Extensão / Formato | Linhas | Período | Conteúdo Principal |
| :--- | :--- | :---: | :---: | :--- |
| `WPP2024_Demographic_Indicators_Medium_csv.gz` | GZIP / CSV | 84.360 | 1950–2101 | **Série canônica contínua:** Registros censitários harmonizados observados (1950–2023) integrados à variante determinística média projetada pela ONU (2024–2101). |
| `WPP2024_Demographic_Indicators_OtherVariants_csv.gz` | GZIP / CSV | 662.919 | 2024–2101 | **Cenários contrafactuais e estocásticos:** Contém 18 cenários alternativos determinísticos (Alta/Baixa fecundidade, mortalidade constante, migração zero, etc.) e quantis probabilísticos (80% e 95% Prediction Intervals). |
| `WPP2024_Demographic_Indicators_notes.csv` | CSV | 59 | Metadados | Dicionário canônico de variáveis, nomes oficiais e unidades de medida. |

### 2.2. Particularidades Técnicas de Carregamento
* **Encoding:** Usar obrigatoriamente `encoding='utf-8-sig'` (ou `UTF-8-BOM`) para evitar caracteres corrompidos na primeira coluna (`SortOrder`).
* **Atenção à extração manual:** Ao descompactar via 7-Zip ou ferramentas de sistema no Windows, a UN armazena o arquivo com o sufixo `_csv` em vez de `.csv`. É necessário renomear para `.csv` caso seja aberto em planilhas.
* **Escala de População:** Variáveis de volume de pessoas (`TPopulation...`, `Births...`, `Deaths...`, `NetMigrations`) estão expressas em **milhares de indivíduos** (`thousands`). Para escala unitária, deve-se multiplicar por $1.000$.

---

## 3. Regras Canônicas de Integridade e Filtragem

> [!CAUTION]
> A coluna `Location` não lista apenas países soberanos. Ela contém simultaneamente:
> 1. Nações independentes e territórios (ex: *Brazil*, *Japan*, *Kenya*).
> 2. Agregados geográficos e continentais (ex: *South America*, *Sub-Saharan Africa*, *World*).
> 3. Agrupamentos socioeconômicos e institucionais (ex: *OECD*, *Least Developed Countries*, *Upper-middle-income countries*).
> 
> Qualquer agregação sem filtro (ex: `df.groupby('Time')['TPopulation1July'].sum()`) somará a mesma pessoa até quatro vezes.

### 3.1. Predicado Booleano Estrito para Países/Territórios Soberanos
Para reter exclusivamente estados-nação individuais, todo script deve aplicar a seguinte filtragem lógica:

$$\text{Filtro Nacional} = (\text{ISO3\_code} \ne \text{null}) \land (\text{len}(\text{ISO3\_code}) == 3) \land (\text{LocTypeName} == \text{'Country/Area'})$$

Em Python / Pandas:
```python
is_country = (
    df['ISO3_code'].notna() & 
    (df['ISO3_code'].str.strip().str.len() == 3) & 
    (df['LocTypeName'] == 'Country/Area')
)
df_countries = df[is_country].copy()
```

### 3.2. Tratamento de Entidades Agregadas (Sem ISO3)
* Registros onde `ISO3_code` é nulo representam entidades sintéticas agregadas da ONU, Banco Mundial ou macro-regiões geográficas.
* **Regra:** Esses registros devem ser isolados em um dataframe específico (`df_macro_aggregates`) para comparações de contexto global ou continental, nunca mesclados com a base de países.

### 3.3. Fronteira Temporal Epistêmica
* Anos $\le 2023$: Dados empíricos históricos harmonizados (estimativas baseadas em censos, pesquisas amostrais e registros vitais).
* Anos $\ge 2024$: Projeções e modelos matemáticos probabilísticos/determinísticos.
* **Regra Gráfica:** Todas as visualizações temporais devem exibir uma linha divisória vertical ou demarcação visual explícita no ano **2024**, separando história de projeção.

---

## 4. Identidades Demográficas e Equações Fundamentais

### 4.1. Equação de Equilíbrio Demográfico em Tempo Discreto
O sistema interno de variáveis do WPP obedece à equação de conservação contábil demográfica:

$$P_{t+1} = P_t + B_t - D_t + M_t$$

Onde:
* $P_t$: População total em 1 de julho (`TPopulation1July`) no ano $t$.
* $B_t$: Nascimentos brutos anuais (`Births`).
* $D_t$: Óbitos brutos anuais (`Deaths`).
* $M_t$: Saldo migratório líquido anual (`NetMigrations`).

### 4.2. Taxas Brutas Padronizadas por Mil Habitantes
* **Taxa de Crescimento Vegetativo / Mudança Natural:**
  $$\text{NatChangeRT}_t = \text{CBR}_t - \text{CDR}_t$$
  Onde $\text{CBR}_t$ é a Taxa Bruta de Natalidade (*Crude Birth Rate*) e $\text{CDR}_t$ é a Taxa Bruta de Mortalidade (*Crude Death Rate*).
* **Taxa de Crescimento Populacional Total (Aproximação Percentual):**
  $$\text{PopGrowthRate}_t \approx \frac{\text{NatChangeRT}_t + \text{CNMR}_t}{10}$$
  Onde $\text{CNMR}_t$ é a Taxa Líquida de Migração (*Crude Net Migration Rate*) por mil habitantes.

### 4.3. Classificação e Agrupamento Canônico das Variáveis

```
WPP 2024
 ├── 1. Dinâmica Populacional: TPopulation1July, MedianAgePop, PopDensity, PopGrowthRate, DoublingTime
 ├── 2. Fecundidade / Reprodução: Births, Births1519, CBR, TFR (Filhos/Mulher), NRR, MAC, SRB
 ├── 3. Sobrevida e Mortalidade:
 │    ├── Precoce: InfantDeaths, IMR, Under5Deaths, Q5, Q0040, Q0060
 │    ├── Adulta e Senescência: Deaths, CDR, Q1550, Q1560, LEx, LE15, LE65, LE80
 └── 4. Redistribuição Espacial: NetMigrations, CNMR
```

---

## 5. Fundamentação Teórica da Modelagem e Literatura dos Papers

### 5.1. Modelos Bayesianos Hierárquicos (BHM) da ONU
As projeções probabilísticas do WPP 2024 foram desenvolvidas pela Divisão de População da ONU em parceria com o Center for Statistics and the Social Sciences da Universidade de Washington:
1. **`bayesTFR` (Fecundidade):** Modela o declínio da taxa de fecundidade total (`TFR`) via MCMC autorregressivo em 3 fases: pré-transição de alta fecundidade, transição descendente regida por função logística dupla, e fase pós-transição estabilizada em torno de níveis de baixa fecundidade:
   $$f(w; \theta_c) = \frac{-d_c}{1 + \exp\left(-\frac{w - \Delta_{c1}}{\sigma_{c1}}\right)} + \frac{d_c}{1 + \exp\left(-\frac{w - \Delta_{c2}}{\sigma_{c2}}\right)}$$
2. **`bayesLife` (Mortalidade):** Projeta a esperança de vida ao nascer (`LEx`) feminina por trajetórias de convergência e estima o diferencial de sobrevida masculino (`LExMale` vs. `LExFemale`) via processos estocásticos correlacionados.
3. **`bayesPop` (População Integrada):** Aplica o Método dos Componentes por Coorte (*Cohort-Component Method*) sobre cada iteração da distribuição posterior gerada pelos modelos anteriores.
4. **Novidade do WPP 2024:** Pela primeira vez na história do WPP, o saldo migratório líquido (`NetMigrations`) recebeu modelagem probabilística estocástica completa, superando o determinismo constante das revisões anteriores.

### 5.2. O Debate Paradigmático: ONU (WPP 2024) vs. IHME / GBD (The Lancet)
No centro da discussão demográfica internacional, há uma divergência estrutural entre a ONU e o Institute for Health Metrics and Evaluation (IHME):

| Parâmetro Metodológico | ONU (WPP 2024) | IHME / GBD (The Lancet 2020, 2024) |
| :--- | :--- | :--- |
| **Pico Populacional** | **~10,3 bilhões** em meados de **2084**; leve declínio para ~10,2 bi em 2100. | **~9,7 bilhões** em **2064**; contração acelerada para **~8,8 bi** em 2100. |
| **Espaço de Modelagem** | Espaço de **Período** (Taxa `TFR`). Admite recuperação parcial probabilística pós-transição. | Espaço de **Coorte** (`CCF50` — Fecundidade Cumulativa aos 50 anos). |
| **Inclusão de Preditores** | Extrapolação hierárquica autorregressiva sem covariáveis macroeconômicas diretas. | Inclusão de preditores causais explícitos: escolaridade feminina e cobertura contraceptiva. |
| **Regime de Ultrabaixa Fecundidade** | Supõe que regimes abaixo de 1,5 filhos/mulher passam por lenta reversão em direção a 1,7–1,8. | Considera regimes ultrabaixos como autorreforçantes; projeta taxa global de 1,59 em 2100 com 97% dos países abaixo da reposição. |

### 5.3. O Paradoxo da Mortalidade Bruta e a Decomposição de Kitagawa (1955)
* **O Paradoxo:** Países desenvolvidos com alta esperança de vida (`LEx` > 80 anos) exibem taxas brutas de mortalidade (`CDR`) mais elevadas que países em desenvolvimento jovens. Isso não reflete piora nas condições de saúde, mas sim uma estrutura demográfica com concentração maciça de idosos.
* **Decomposição Matemática de Kitagawa (1955):** Divide a variação da taxa bruta entre dois períodos ou populações ($A$ e $B$) em duas parcelas aditivas exatas sem resíduo:
  $$\Delta R = R^A - R^B = \underbrace{\sum_{k} \bar{w}_k (r_k^A - r_k^B)}_{\text{Efeito-Taxa (Saúde Real)}} + \underbrace{\sum_{k} \bar{r}_k (w_k^A - w_k^B)}_{\text{Efeito-Composição (Envelhecimento)}}$$
  Onde $r_k$ são taxas de mortalidade da faixa etária $k$, $w_k$ é o peso proporcional da faixa na população, $\bar{w}_k = \frac{w_k^A + w_k^B}{2}$ e $\bar{r}_k = \frac{r_k^A + r_k^B}{2}$.
* **Algoritmo de Substituição Passo a Passo (Andreev, Shkolnikov & Begun, 2002):** Decompõe ganhos em `LEx` por faixas etárias específicas (`IMR`, `Q5`, `LE65`, `LE80`) sem gerar resíduos matemáticos inexplicados.

---

## 6. Fatos Canônicos da Dinâmica Demográfica Brasileira

O Brasil é um modelo clássico de transição acelerada em economia de renda média, tendo realizado em poucas décadas transformações que levaram mais de um século na Europa:

### 6.1. Marco Temporal da Série WPP 2024 para o Brasil (ISO3: `BRA`)

| Indicador | 1950 (Marco Histórico) | 2024 (Presente) | 2042 (Ápice Projetado) | 2100 (Final da Série) |
| :--- | :---: | :---: | :---: | :---: |
| **População Residente (`TPopulation1July`)** | 53,4 milhões | 212,0 milhões | **219,3 milhões** | 163,4 milhões |
| **Fecundidade Total (`TFR`)** | 6,10 filhos/mulher | 1,61 filhos/mulher | 1,56 filhos/mulher | 1,58 filhos/mulher |
| **Idade Mediana (`MedianAgePop`)** | 17,5 anos | 34,4 anos | ~41,0 anos | **50,7 anos** |
| **Esperança de Vida ao Nascer (`LEx`)** | 50,0 anos | 76,0 anos | 79,0 anos | 86,8 anos |
| **Crescimento Populacional (`PopGrowthRate`)** | +3,07% ao ano | +0,40% ao ano | **0,00% (Inflexão)** | **-0,80% ao ano** |
| **Saldo Migratório Líquido (`NetMigrations`)** | Residual | -226 mil / ano | Negativo persistente | Estabilização negativa |

### 6.2. Os Três Efeitos Estruturais Encadeados
1. **1ª Ordem (Base da Pirâmide):** Queda vertical da fecundidade ($6,1 \to 1,61$), aniquilando a expansão da base e levando à anulação do crescimento vegetativo em 2042 ($\text{Births} = \text{Deaths}$).
2. **2ª Ordem (Esgotamento do Bônus):** Elevação drástica da idade mediana para 50,7 anos. O país esgota o bônus demográfico (razão de dependência favorável) antes de alcançar renda per capita de nação desenvolvida ("envelhece antes de enriquecer").
3. **3ª Ordem (Tensões Fiscais e Epidemiológicas):** Compressão da razão de trabalhadores ativos por aposentado no regime de repartição da previdência, conjugada à transição epidemiológica do SUS para o manejo de doenças crônicas nas faixas longevas (`LE65` e `LE80`).

### 6.3. Confronto Empírico com o Censo Demográfico IBGE 2022
* O Censo 2022 do IBGE apurou **203,1 milhões de habitantes**, número inferior às projeções anteriores tanto do IBGE quanto da ONU.
* **Implicação Canônica:** Esse resultado empírico comprova que a desaceleração reprodutiva foi ainda mais aguda do que o projetado, indicando que o pico populacional brasileiro poderá ocorrer até antes de 2042.

---

## 7. Diretrizes Éticas e Boas Práticas da ASA

Segundo as *Ethical Guidelines for Statistical Practice* da ASA:
1. **Princípios A e B (Comunicação da Incerteza):** É dever ético explicitar a dispersão estocástica. Apresentar apenas a variante `Medium` induz o público e tomadores de decisão a uma falsa sensação de certeza determinística. Deve-se sempre incorporar os intervalos de predição a 80% e 95% do arquivo `OtherVariants`.
2. **Combate ao Pânico Moral e Instrumentalização Ideológica:** A queda da fecundidade é consequência direta do aumento da escolaridade feminina, inserção no mercado de trabalho e autonomia sobre direitos sexuais e reprodutivos. Rejeitar terminologias alarmistas ("colapso demográfico", "suicídio geracional" ou teorias conspiratórias de "substituição de povos") frequentemente usadas para tentar revogar direitos reprodutivos das mulheres ou criminalizar migrantes.
3. **Invisibilidade Censitária e Limitações de CRVS:** Em países do Sul Global e em populações periféricas e originárias, registros civis de nascimento e óbito (*Civil Registration and Vital Statistics - CRVS*) possuem sub-registros históricos. Modelos bayesianos realizam imputações sintéticas que não devem ser tratadas de forma cega como verdades absolutas sem a devida advertência metodológica.

---

## 8. Log Canônico de Descobertas e Validações Empíricas (Living Knowledge Log)

Esta seção deve ser incrementada cronologicamente conforme a equipe explore a base e execute modelos:

| Data (YYYY-MM-DD) | Autor / Agente | Hipótese / Questão Testada | Variáveis Mobilizadas | Descoberta Empírica / Conclusão | Impacto no Projeto / Slides |
| :---: | :---: | :--- | :--- | :--- | :--- |
| **2026-10-05** | Equipe Ipanema | Verificação da taxonomia e sobreposição de `Location` | `Location`, `ISO3_code`, `LocTypeName` | Confirmado: base possui 237 nações soberanas e 316 agrupamentos sintéticos. A soma ingênua em 2024 resulta em 366,22 bilhões (inflação de 44,87x) contra 8,16 bilhões reais com o filtro canônico. | Slide 1 (Destaque metodológico de rigor estatístico e integridade). |
| **2026-10-05** | Equipe Ipanema | Diagnóstico de Inflexão Vital do Brasil | `CBR`, `CDR`, `PopGrowthRate` | Confirmado ápice de 219,3 milhões em 2042 e travessia da linha biológica ($CDR \ge CBR$) no ano de 2043. Taxa de crescimento anual atinge -0,74% em 2100. | Slide 2 (Diagrama $CBR \times CDR$ e análise de transição). |
| **2026-10-05** | Equipe Ipanema | Análise das variantes presentes em `OtherVariants` | `Variant`, `Time` | O arquivo contém 18 variantes nominais determinísticas e 5 séries de quantis estocásticos (`Lower 80`, `Upper 80`, `Lower 95`, `Upper 95`, `Median PI`). | Definido uso do envelope 80% e 95% no Fan Chart do Slide 3. |
| **2026-10-06** | Equipe Ipanema | Diagnóstico de K Ideal e Regimes Demográficos (Módulo 06) | `TFR`, `LEx`, `CBR`, `CDR`, `MedianAgePop`, `NatChangeRT` | Painel de 35.787 pares país-ano testado de K=2 a K=8. O valor K=5 reconstrói perfeitamente as 5 fases da Transição Demográfica (WCSS 31.469, CH 52.091). A matriz empírica P_ij é estritamente tridiagonal superior (unidirecional). | Metodologia central de modelagem estocástica (Best Statistical Insight). |
| **2026-10-06** | Equipe Ipanema | Identificação do Estágio 5 como Estado Quase-Absorvente | Matriz Markov $P_{55}$, $E[T_i]$ | O Estágio 5 (Super-Envelhecimento) exibe retenção de $99,74\%$ ao ano ($E[T_5] \approx 384$ anos). A probabilidade de retorno a estágios anteriores é de apenas $0,26\%$, confirmando a tese de "armadilha de baixa fertilidade" (Lancet/IHME). | Slide 3 e 4 (Alinhamento teórico com a literatura). |
| **2026-10-06** | Equipe Ipanema | Reconstrução Estocástica da Jornada do Brasil | `stage` anual | O Brasil transita para o Estágio 3 (Bônus Demográfico) em 1982, para o Estágio 4 (Pós-Transição) em 2008, e ingressa no Estágio 5 (Super-Envelhecimento) em 2046. A permanência média no Bônus foi de apenas 26 anos. | Slide 2 (Narrativa de compressão temporal da transição). |
