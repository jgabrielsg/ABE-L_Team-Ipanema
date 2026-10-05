# Roteiro Cronometrado — Vídeo Técnico de 5 Minutos (300 segundos)

> **Competição:** ASA International Data Quest 2026  
> **Equipe:** Team Ipanema (ABE-L)  
> **Duração Total:** Exatamente 5 minutos (300 s)  
> **Apresentadores Sugeridos:** 1 ou 2 membros em revezamento  
> **Material de Apoio:** 4 Slides de Conteúdo oficiais

---

### [00:00 – 00:50] Bloco 1: Abertura, Contexto do WPP 2024 e o Perigo da Dupla Contagem (Slide 1)
* **Visual:** Slide 1 na tela (Dispersão global $CBR \times \text{PopGrowthRate}$ e mapa temático).
* **Fala (50s):**
  > *"Olá a todos e aos avaliadores da American Statistical Association. Somos a Equipe Ipanema e apresentamos nossa pesquisa para o ASA Data Quest 2026 sobre a 28ª revisão das Projeções Populacionais da ONU.*  
  > *Logo no primeiro contato com o dataset WPP 2024, identificamos um risco crítico de integridade: a base sobrepõe 237 países soberanos a mais de 300 agregados regionais e de renda. Qualquer análise ingênua que some a população mundial em 2024 resulta em surreais 366 bilhões de habitantes — uma inflação de quase 45 vezes o tamanho real da humanidade.  
  > Ao estabelecermos nosso filtro canônico rigoroso por ISO3 e LocTypeName, restauramos a integridade com 8,16 bilhões reais. Observamos que o mundo caminha para um ápice em meados da década de 2080, com 700 milhões de pessoas a menos em 2100 frente às projeções de 10 anos atrás. Mais de 26% das nações já registram crescimento negativo hoje."*

---

### [00:50 – 02:00] Bloco 2: O Caso Brasileiro: Espaço de Fases, Bônus e Decomposição de Kitagawa (Slide 2)
* **Visual:** Slide 2 na tela (Espaço de fases vitais $CBR \times CDR$ com a reta $y=x$ e gráfico de barras divergentes de Kitagawa).
* **Fala (70s):**
  > *"Ao aprofundarmos no Brasil, encontramos um caso paradigmático de transição demográfica hipercomprimida. Em apenas 7 décadas, a fecundidade brasileira desabou de 6,1 para 1,61 filhos por mulher.  
  > Nosso diagrama de fases vitais demonstra que a população brasileira atinge seu ápice de 219,3 milhões em 2042 e cruza a linha de decréscimo natural em 2043, quando a taxa bruta de mortalidade supera a de natalidade.  
  > Mas aqui surge um paradoxo estatístico clássico: por que a mortalidade bruta brasileira sobe continuamente a partir de 2020 se a esperança de vida atinge 86,8 anos em 2100?  
  > Para responder com rigor matemático, implementamos a decomposição formal de Evelyn Kitagawa. O resultado é inequívoco: o aumento do CDR é explicado em sua quase totalidade pelo 'efeito-composição' — o rápido envelhecimento da estrutura etária, com a idade mediana saltando para 50,7 anos — e não pela piora sanitária. O Brasil envelheceu antes de atingir a renda média per capita das nações desenvolvidas, esgotando seu bônus demográfico prematuramente."*

---

### [02:00 – 03:20] Bloco 3: O Debate Metodológico ONU vs. IHME e a Comunicação Estocástica (Slide 3)
* **Visual:** Slide 3 na tela (Fan Chart contínuo com envelopes de incerteza de 80% e 95% PI e linha vertical em 2024).
* **Fala (80s):**
  > *"No cenário global, investigamos a profunda controvérsia entre as projeções bayesianas da ONU e os modelos de coorte do IHME publicados no The Lancet.  
  > Enquanto a ONU prevê um pico de 10,3 bilhões nos anos 2080 admitindo uma recuperação parcial da fecundidade pós-2050, o IHME introduz preditores exógenos de escolaridade feminina e modela a ultrabaixa fecundidade como um processo autorreforçante, antecipando o pico global para 2064 com 9,7 bilhões.  
  > Como cientistas de dados, aplicamos o arquivo OtherVariants para romper com a ilusão do determinismo da variante 'Medium'. Construímos Fan Charts estocásticos evidenciando os envelopes de predição a 80% e 95%.  
  > A mensagem científica é clara: a partir de 2050, a dispersão estatística acumulada ultrapassa centenas de milhões de habitantes. Projetar políticas públicas ignorando esses intervalos é uma falha metodológica severa."*

---

### [03:20 – 04:30] Bloco 4: Diretrizes Éticas da ASA, Direitos Reprodutivos e CRVS (Slide 4)
* **Visual:** Slide 4 na tela (Painel de ética, comparação Censo IBGE 2022 e eixos de políticas públicas).
* **Fala (70s):**
  > *"Em estrita observância às Diretrizes Éticas para a Prática Estatística da ASA (Princípios A e B), rejeitamos enfaticamente a instrumentalização ideológica dos dados demográficos. A retração da fecundidade não deve ser rotulada como 'colapso' ou 'suicídio civilizacional' para justificar medidas coercitivas contra a autonomia corporal e reprodutiva das mulheres, nem discursos xenofóbicos contra migrantes.  
  > O declínio reprodutivo é fruto da conquista de direitos civis, urbanização e escolarização feminina.  
  > Além disso, destacamos o problema do sub-registro nos sistemas de registros civis (CRVS) no Sul Global. Ao cruzarmos os dados da ONU com os resultados empíricos do Censo IBGE 2022, que contou 203 milhões de brasileiros — bem abaixo das projeções prévias —, comprovamos que modelos bayesianos sintéticos devem ser permanentemente calibrados por censos de campo de alta qualidade."*

---

### [04:30 – 05:00] Bloco 5: Recomendações e Encerramento (Slide 4 / Conclusão)
* **Visual:** Slide 4 (Recomendações estratégicas) seguido da lâmina de encerramento e créditos.
* **Fala (30s):**
  > *"Concluímos que a resposta ao novo regime demográfico não reside em pânicos natalistas, mas na governança pública baseada em evidências: reestruturação atuarial da previdência, adaptação do SUS para cuidados de média e alta complexidade geriátrica e valorização da produtividade por trabalhador.  
  > Agradecemos à ASA e ao SaLLy/UFBA pela oportunidade de articular rigor estatístico, ética e visualização de dados."*
