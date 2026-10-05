# ASA International Data Quest 2026 — Planejamento e Objetivos do Projeto

> **Equipe:** Team Ipanema (ABE-L)  
> **Competição:** ASA International Data Quest 2026  
> **Organizadores:** American Statistical Association (ASA) & Statistical Learning Laboratory (SaLLy/UFBA)  
> **Base de Dados:** UN World Population Prospects (WPP 2024) — UN DESA Population Division  
> **Status Geral do Projeto:** Planejamento Concluído | Modelagem e Pipeline em Implementação

---

## 1. Visão Geral e Propósito do Projeto

Este projeto tem como objetivo construir uma análise demográfica rigorosa, reproduzível e eticamente orientada sobre a 28ª revisão das Projeções Populacionais Mundiais das Nações Unidas (**WPP 2024**). 

A abordagem do **Team Ipanema** foi estruturada estrategicamente para disputar as **três categorias oficiais de premiação** do concurso, integrando métodos avançados de demografia formal, rigor ético segundo as diretrizes da ASA e engenharia de visualização de dados de alto impacto cognitivo:

| Categoria Oficial da ASA | Questão Central Investigada pela Equipe | Instrumentos Analíticos Centrais |
| :--- | :--- | :--- |
| **Best Statistical Insight** | Como a velocidade da transição demográfica em economias emergentes (foco Brasil) acelera o esgotamento do bônus demográfico, e de que forma a controvérsia metodológica ONU vs. IHME altera as previsões de pico populacional? | Decomposição formal de Kitagawa (1955), contrastes contrafactuais de fecundidade, espaço de fases $(TFR \times LEx)$ e $(CBR \times CDR)$. |
| **Best Consideration of Ethics** | De que maneira a comunicação determinista da projeção central mascara incertezas profundas, alimenta retóricas anti-direitos reprodutivos e invisibiliza limitações de dados censitários (CRVS) no Sul Global? | Auditoria de calibração dos envelopes estocásticos (80% e 95% PI), contraste WPP vs. Censo IBGE 2022, alinhamento aos Princípios A e B da ASA. |
| **Best Data Visualization** | Como sintetizar fenômenos multidimensionais e incerteza estocástica em gráficos intuitivos, de alta densidade informativa e sem sobrecarga cognitiva? | Fan Charts contínuos com envelope de incerteza posterior, diagrama de espaço de fases com linha de equilíbrio vital ($y=x$), gráficos de divergência de Kitagawa. |

---

## 2. Hipóteses Estatísticas e Objetivos Científicos

O projeto investiga quatro hipóteses centrais, articulando matemática atuarial, demografia estocástica e ciência de dados:

1. **Hipótese da Inflexão Populacional Acelerada:**
   * *Formula:* A transição para saldo biológico negativo ($\text{NatChangeRT} < 0$) em economias emergentes consolidadas é insensível ao saldo migratório histórico, ocorrendo impreterivelmente na década de 2040 no Brasil.
   * *Métricas:* `CBR`, `CDR`, `NatChangeRT`, `PopGrowthRate`, `CNMR`.
2. **Hipótese do Paradoxo da Mortalidade e Efeito-Composição:**
   * *Formula:* Mais de 80% do incremento na taxa bruta de mortalidade (`CDR`) em países pós-transição resulta exclusivamente da alteração da estrutura etária (envelhecimento das coortes), e não da piora nas condições sanitárias ou de sobrevida.
   * *Métricas e Métodos:* Decomposição aditiva de Kitagawa aplicada sobre faixas etárias, `CDR`, `MedianAgePop`, `LEx`, `LE65`.
3. **Hipótese da Divergência Metodológica Global (ONU vs. IHME):**
   * *Formula:* A modelagem hierárquica bayesiana em espaço de período (ONU) retarda o pico da população mundial (~10,3 bi em 2084) quando comparada à modelagem em espaço de coorte com preditores exógenos educacionais do IHME (~9,7 bi em 2064).
   * *Métricas:* `TFR`, cenários contrafactuais (`Medium`, `Low`, `Constant Fertility`).
4. **Hipótese da Dispersão Estocástica e Transparência Ética:**
   * *Formula:* A amplitude do intervalo de predição a 95% (`Upper 95 PI` − `Lower 95 PI`) supera o tamanho de populações inteiras de grandes nações após 2050, tornando eticamente reprovável a apresentação da variante `Medium` como cenário determinístico para formulação de políticas públicas.
   * *Métricas:* Quantis de distribuição do arquivo `OtherVariants`.

---

## 3. Informações Gerais sobre os Dados

A base de dados oficial é composta por três arquivos principais fornecidos pela organização do evento:

| Arquivo Fonte | Dimensão | Período Coberto | Papel no Projeto | Cuidados Críticos |
| :--- | :--- | :--- | :--- | :--- |
| `WPP2024_Demographic_Indicators_Medium_csv.gz` | 84.360 linhas | 1950–2101 | **Série canônica principal:** Histórico harmonizado (1950–2023) + Projeção média da ONU (2024–2101). | Filtrar obrigatoriamente por `ISO3_code` não nulo e `LocTypeName == 'Country/Area'`. |
| `WPP2024_Demographic_Indicators_OtherVariants_csv.gz` | 662.919 linhas | 2024–2101 | **Análise de incerteza e cenários contrafactuais:** 18 variantes e quantis probabilísticos (80% e 95% PI). | Arquivo volumoso (~232 MB descompactado); filtrar estritamente as colunas e países alvo. |
| `WPP2024_Demographic_Indicators_notes.csv` | 59 registros | Metadados | Dicionário de variáveis, siglas oficiais e unidades de medida. | Fonte de verdade de unidades (população em milhares, taxas por 1.000, etc.). |

> **Atenção Estrutural:** O arquivo não possui apenas países; ele agrega blocos regionais, estratos do Banco Mundial e agrupamentos ad hoc. O manuseio sem filtro gera **dupla contagem** catastrófica nas análises globais.

---

## 4. Matriz de Entregáveis do Edital

O edital do ASA International Data Quest 2026 estabelece requisitos rigorosos de formato e limites de conteúdo:

### 4.1. Vídeo Técnico (Máximo de 5 minutos / 300 segundos)
* **Objetivo:** Exposição oral e visual fluida do raciocínio analítico, demonstrando o insight estatístico, a fundamentação ética e os gráficos interativos/estáticos gerados.
* **Cronograma sugerido por bloco de fala:**
  * `00:00 – 00:50` (50s): Introdução, contexto da WPP 2024, prevenção de dupla contagem e inflexão global.
  * `00:50 – 02:00` (70s): O caso brasileiro: espaço de fases vital, bônus demográfico e decomposição de Kitagawa do paradoxo da mortalidade.
  * `02:00 – 03:20` (80s): Debate metodológico ONU vs. IHME e comunicação estocástica via Fan Charts (80% e 95% PI).
  * `03:20 – 04:30` (70s): Ética estatística da ASA: combate ao alarmismo natalista, invisibilidade censitária (CRVS) e cotejamento com o Censo 2022.
  * `04:30 – 05:00` (30s): Conclusão, recomendações de políticas públicas e encerramento.

### 4.2. Apresentação em Slides (Exatamente 4 Slides de Conteúdo)
* **Estrutura estrita:** Capa + 4 Slides de Conteúdo + Referências (Total: 6 lâminas).

```
[Slide 0: Capa] -> [Slide 1: Inflexão Global] -> [Slide 2: Brasil & Kitagawa] 
                -> [Slide 3: Debate ONU x IHME & Fan Chart] 
                -> [Slide 4: Ética ASA & Políticas Públicas] -> [Slide 5: Referências]
```

* **Slide 1 — A Inflexão Demográfica Global e a Prevenção de Dupla Contagem:**
  * O ápice em meados de 2080 (~10,3 bi) e a revisão para baixo de 700 milhões de pessoas frente a 2014.
  * A armadilha de `Location` e o predicado booleano estrito de isolamento soberano.
  * *Gráfico:* Dispersão global $CBR \times \text{PopGrowthRate}$ com marcação dos polos regionais.
* **Slide 2 — O Caso Brasileiro: Espaço de Fases, Bônus Demográfico e Decomposição de Taxas:**
  * Trajetória de 1950 a 2100: de 53,4M a 219,3M (ápice em 2042) e queda para 163,4M em 2100.
  * *Gráfico 1:* Diagrama de fases vitais $CBR \times CDR$ com a bissetriz $y=x$ marcando a virada biológica em 2042.
  * *Gráfico 2:* Decomposição de Kitagawa isolando o efeito-composição (envelhecimento) no aumento do CDR.
* **Slide 3 — O Debate Metodológico Global e a Comunicação Estocástica da Incerteza:**
  * Comparação crítica: ONU (TFR de período, BHM) vs. IHME/The Lancet (CCF50 de coorte, preditores exógenos de educação feminina).
  * *Gráfico:* Fan Chart com envelopes de densidade posterior (80% e 95% PI) e linha divisória temporal no marco de 2024.
* **Slide 4 — Governança Ética, Direitos Reprodutivos e Formulação de Políticas Públicas:**
  * Princípios A e B da ASA: desmistificação de teorias conspiratórias ("substituição de povos") e pânico neomalthusiano.
  * Sub-registro censitário e discrepâncias empíricas (Censo IBGE 2022 com 203M vs projeções anteriores).
  * Recomendações práticas para sustentabilidade previdenciária e adaptação do SUS à terceira idade.

---

## 5. Status dos Entregáveis e Quadro de Acompanhamento (Kanban)

| Entregável / Tarefa | Responsável / Sub-etapa | Status Atual | Próxima Ação Imediata |
| :--- | :--- | :---: | :--- |
| **1. Documentação e Regras Canônicas** | Criação do `OBJETIVOS_DO_PROJETO.md` e `CANONICAL_DATA_RULES.md` | **CONCLUÍDO** | Manter o log canônico atualizado a cada nova rodada analítica. |
| **2. Pipeline de Limpeza e Filtragem** | Script Python para carregar `Medium` e `OtherVariants` com filtros anti-dupla contagem | **EM ANDAMENTO** | Implementar `src/data_loader.py` com testes automáticos de integridade. |
| **3. Modelagem Estatística: Decomposição** | Implementação do algoritmo de Kitagawa (1955) e cálculo dos efeitos taxa e composição para o Brasil | **A FAZER** | Criar script de cálculo matemático `src/kitagawa_decomposition.py`. |
| **4. Extração e Análise da Incerteza (OtherVariants)** | Processamento das séries estocásticas de 80% e 95% PI para o mundo e Brasil | **A FAZER** | Isolar cenários `Medium`, `Low`, `High`, `Upper 95`, `Lower 95`. |
| **5. Geração das Visualizações Gráficas** | Código das 4 figuras de alta resolução em estilo publicação (Matplotlib / Seaborn) | **A FAZER** | Produzir: (1) Espaço de Fases Vital, (2) Fan Chart, (3) Kitagawa, (4) Inflexão Global. |
| **6. Redação e Design dos 4 Slides de Conteúdo** | Criação do deck de slides respeitando rigorosamente a limitação de 4 lâminas | **A FAZER** | Diagramar slides com textos concisos e os gráficos incorporados em alta qualidade. |
| **7. Roteiro e Gravação do Vídeo de 5 Minutos** | Escrita do script segundo a segundo, gravação de áudio/vídeo e edição | **A FAZER** | Ensaiar tempo de fala com base no roteiro cronometrado e gravar apresentação. |
| **8. Revisão Ética e Auditoria Final da ASA** | Checklist contra as *Ethical Guidelines for Statistical Practice* da ASA | **A FAZER** | Validar menção a incertezas, transparência de premissas e sub-registro censitário. |

---

## 6. Checklist de Validação Final da Submissão

- [ ] Apenas dados filtrados por `ISO3_code.notna()` e `LocTypeName == 'Country/Area'` foram usados para agregados nacionais?
- [ ] A linha de corte temporal entre observação empírica ($\le 2023$) e projeção ($\ge 2024$) está destacada visualmente?
- [ ] Os intervalos probabilísticos de 80% e 95% foram apresentados para contestar o determinismo da variante média?
- [ ] O paradoxo da mortalidade bruta do Brasil foi formalmente explicado pela decomposição de Kitagawa?
- [ ] O slide deck possui no máximo 4 slides de conteúdo (sem contar capa e referências)?
- [ ] O vídeo respeita rigorosamente o limite de 5 minutos (300 segundos)?
- [ ] As diretrizes éticas da ASA foram explicitadas e integradas à narrativa de políticas públicas?
