# Sistema Multi-Agentes para Análise de Pesquisadores CNPq

**Disciplina:** Agentic AI  
**Professor:** Dr. Eduardo Almeida  
**Aluna:** Elen Greice  
**Ano:** 2026

---

## Sumário

1. [Visão Geral do Sistema](#1-visão-geral-do-sistema)
2. [Requisitos do Sistema](#2-requisitos-do-sistema)
3. [Design do Sistema](#3-design-do-sistema)
4. [Implementação](#4-implementação)
5. [Architecture Decision Records (ADRs)](#5-architecture-decision-records-adrs)
6. [Testes e Inconsistências](#6-testes-e-inconsistências)
7. [Implantação](#7-implantação)
8. [Model Context Protocol (MCP)](#8-model-context-protocol-mcp)
9. [Qualidade e Resiliência](#9-qualidade-e-resiliência)
10. [Conclusão](#10-conclusão)

---

## 1. Visão Geral do Sistema

O sistema desenvolvido é uma plataforma multi-agentes que coleta, processa e disponibiliza dados sobre pesquisadores bolsistas do CNPq. O sistema realiza scraping automatizado do site do CNPq e do Currículo Lattes, organiza os dados em um dataset estruturado, e os disponibiliza através de um dashboard interativo com suporte a consultas em linguagem natural via LangChain Pandas Agent com GPT-4o.

### 1.1 Objetivos do Sistema

- Coletar automaticamente dados de pesquisadores do site do CNPq
- Enriquecer os dados com informações do Currículo Lattes
- Gerar um dataset estruturado com informações completas dos bolsistas
- Disponibilizar um dashboard interativo para visualização dos dados
- Permitir exportação dos dados em formato CSV e PDF
- Oferecer interface de consulta em linguagem natural com precisão total
- Registrar log de todas as operações realizadas
- Validar a integridade dos dados automaticamente
- Detectar e tratar novos e removidos pesquisadores automaticamente
- Facilitar a atualização do dataset com novos pesquisadores via script

### 1.2 Tecnologias Utilizadas

| Tecnologia | Finalidade | Justificativa |
|---|---|---|
| Python 3.x | Linguagem principal | Ecossistema rico com bibliotecas maduras para scraping e IA |
| Streamlit | Dashboard web | Cria interfaces web sem necessidade de HTML/JS |
| BeautifulSoup4 | Web scraping CNPq | Parser HTML robusto para sites estáticos |
| Selenium | Web scraping Lattes | Automação de navegador para sites com JavaScript e CAPTCHA |
| Pandas | Manipulação de dados | Padrão para análise de dados em Python |
| Plotly | Gráficos interativos | Visualizações ricas e interativas |
| LangChain + GPT-4o | Linguagem natural | Agente que executa código pandas para respostas precisas |
| FPDF2 | Geração de PDF | Simples e eficiente para relatórios |
| gender-guesser | Inferência de sexo | Detecta sexo pelo primeiro nome automaticamente |
| GitHub + Streamlit Cloud | Implantação | Hospedagem gratuita e deploy automatizado |

---

## 2. Requisitos do Sistema

### 2.1 Requisitos Funcionais

| ID | Requisito | Descrição |
|---|---|---|
| RF01 | Coletar Dados | O sistema deve coletar dados automaticamente do site do CNPq |
| RF02 | Enriquecer Dataset | O sistema deve buscar dados complementares no Currículo Lattes |
| RF03 | Inferir Sexo | O sistema deve inferir o sexo do pesquisador pelo primeiro nome |
| RF04 | Mapear UF | O sistema deve identificar o estado (UF) pela sigla da instituição |
| RF05 | Gerar Dataset | Os dados devem ser organizados em formato CSV estruturado e ordenado alfabeticamente |
| RF06 | Visualizar Dashboard | O sistema deve exibir gráficos e tabelas com os dados coletados |
| RF07 | Filtrar Dados | O dashboard deve permitir filtragem por nível, instituição, UF, sexo e situação |
| RF08 | Exportar CSV | O sistema deve permitir download dos dados filtrados em CSV |
| RF09 | Exportar PDF | O sistema deve permitir download dos dados filtrados em PDF |
| RF10 | Consultar Linguagem Natural | O sistema deve responder qualquer pergunta em português sobre os dados com precisão total |
| RF11 | Registrar Log | O sistema deve registrar todas as ações realizadas com data e hora |
| RF12 | Validar Integridade | O sistema deve validar automaticamente a integridade do dataset |
| RF13 | Detectar Mudanças | O sistema deve detectar novos e removidos pesquisadores no CNPq |
| RF14 | Gerenciar Ativos | O sistema deve marcar pesquisadores removidos como inativos sem excluí-los |
| RF15 | Facilitar Atualização | O sistema deve gerar arquivo e script para atualização de novos pesquisadores |

### 2.2 Requisitos Não Funcionais

| ID | Categoria | Descrição |
|---|---|---|
| RNF01 | Desempenho | Cache de 1 hora para evitar requisições repetidas ao CNPq |
| RNF02 | Disponibilidade | Sistema disponível online via Streamlit Cloud |
| RNF03 | Segurança | Chaves de API armazenadas em variáveis de ambiente seguras |
| RNF04 | Usabilidade | Interface intuitiva sem necessidade de treinamento |
| RNF05 | Manutenção | Código organizado em módulos por responsabilidade |
| RNF06 | Resiliência | Reinício automático do driver Selenium em caso de falha de sessão |
| RNF07 | Confiabilidade | Validações automáticas de integridade do dataset a cada carregamento |
| RNF08 | Precisão | Respostas de linguagem natural via execução real de código pandas |
| RNF09 | Disponibilidade | Fallback automático CNPq → GitHub → arquivo local |
| RNF10 | Rastreabilidade | Pesquisadores removidos mantidos no dataset com campo ativo=N |
| RNF11 | Organização | Dataset sempre ordenado alfabeticamente por nome |

---

## 3. Design do Sistema

### 3.1 Por que Arquitetura Multi-Agentes?

A escolha pela arquitetura multi-agentes se justifica pela necessidade de separar responsabilidades complexas e distintas: coleta de dados, enriquecimento, visualização, consulta em linguagem natural, logging, validação, gerenciamento de ciclo de vida e facilitação de atualizações. Um sistema monolítico dificultaria a manutenção e o rastreamento de erros.

### 3.2 Agentes do Sistema

| Agente | Responsabilidade | Ferramentas (Tools) |
|---|---|---|
| Orchestrator Agent | Coordena todos os agentes e define o fluxo de execução | Gerenciamento de estado, logging |
| Scraping Agent | Coleta dados do site do CNPq automaticamente | requests, BeautifulSoup4, pandas |
| Enrichment Agent | Busca dados complementares no Currículo Lattes | Selenium, ChromeDriver |
| Data Agent | Processa, limpa e organiza os dados coletados | pandas, gender-guesser, regex |
| Data Loader Agent | Carrega dados com fallback e detecta mudanças | requests, pandas, BeautifulSoup4 |
| Dashboard Agent | Exibe visualizações e permite exportação | Streamlit, Plotly, FPDF2 |
| Query Agent | Responde perguntas em linguagem natural via Text-to-Pandas | LangChain, GPT-4o, pandas |
| Logger Agent | Registra todas as operações do sistema | logging, arquivo .log |
| Validation Agent | Valida integridade do dataset automaticamente | pandas, assertions |
| Update Agent | Facilita atualização de novos pesquisadores | pandas, subprocess, git |

### 3.3 Fluxo do Sistema (Flow)

Fluxo de coleta de dados (executado localmente):
```
Scraping Agent acessa site CNPq
       ↓
Extrai pesquisadores e ordena alfabeticamente
       ↓
Validation Agent valida os dados coletados
       ↓
Data Agent infere sexo, UF e área de atuação
       ↓
Enrichment Agent acessa Currículo Lattes via Selenium
       ↓
Data Agent extrai ano de conclusão do doutorado via regex
       ↓
Dataset final ordenado e salvo em CSV → GitHub
```

Fluxo do dashboard (executado online):
```
Data Loader Agent verifica CNPq
       ↓
Detecta novos/removidos → atualiza campo ativo
       ↓
Se houver novos → exibe aviso + botão "Gerar arquivo de atualizacao"
       ↓
Usuário clica → gera novos_pesquisadores.csv + exibe script
       ↓
Usuário baixa CSV, salva em atualizacoes/ e roda script localmente
       ↓
Script atualiza dataset, ordena e faz push para GitHub
       ↓
Validation Agent valida integridade
       ↓
Dashboard Agent exibe apenas pesquisadores com ativo=S
```

### 3.4 Fluxo de Atualização de Novos Pesquisadores

```
Dashboard detecta novo pesquisador no CNPq
       ↓
Exibe aviso com nome dos novos pesquisadores
       ↓
Usuário clica em "Gerar arquivo de atualizacao"
       ↓
Sistema gera novos_pesquisadores.csv na pasta atualizacoes/
       ↓
Exibe instrução: python atualizacoes/atualizar_dataset.py
       ↓
Usuário baixa o CSV e salva em atualizacoes/ localmente
       ↓
Usuário roda o script no terminal
       ↓
Script carrega novos_pesquisadores.csv
Script enriquece com Google Scholar e URL Lattes
Script adiciona ao dataset e ordena alfabeticamente
Script faz push automático para GitHub
       ↓
Dashboard atualizado automaticamente
```

### 3.5 Handoffs

| De | Para | Condição |
|---|---|---|
| Orchestrator | Data Loader Agent | Ao iniciar o dashboard |
| Data Loader Agent | Validation Agent | Após carregar os dados |
| Data Loader Agent | Dashboard Agent | Após validar os dados |
| Dashboard Agent | Update Agent | Quando usuário clica em Gerar arquivo |
| Dashboard Agent | Logger Agent | A cada ação do usuário |
| Dashboard Agent | Query Agent | Quando usuário digita uma pergunta |
| Query Agent | LangChain | Para gerar código pandas |
| LangChain | GPT-4o | Para raciocinar sobre a pergunta |
| GPT-4o | LangChain | Código pandas gerado |
| LangChain | Dashboard Agent | Resultado calculado |

### 3.6 Guardrails

- **Validação de linhas:** apenas linhas com 6 ou mais colunas são processadas
- **Filtro de cabeçalhos:** linhas com texto NOME são ignoradas
- **Deduplicação:** pesquisadores duplicados são removidos pelo nome
- **Timeout:** requisições ao CNPq têm limite de 15 segundos
- **Cache:** dados armazenados por 1 hora para evitar sobrecarga
- **Reinício automático:** driver Selenium reinicia em caso de sessão perdida
- **Campo ativo:** pesquisadores removidos marcados como ativo=N, nunca excluídos
- **Fallback triplo:** CNPq → GitHub → arquivo local
- **Ordenação alfabética:** dataset sempre ordenado por nome
- **Colunas reduzidas:** Query Agent recebe apenas colunas essenciais
- **handle_parsing_errors:** LangChain trata erros de parsing automaticamente
- **max_iterations:** limite de 5 iterações por consulta
- **Confirmação do usuário:** atualização só ocorre após confirmação explícita

---

## 4. Implementação

### 4.1 Estrutura de Arquivos

```
projeto-cnpq/
├── agents/
│   └── logger_agent.py              # Logger Agent
├── tools/
│   ├── cnpq_scraper.py              # Scraping Agent
│   ├── lattes_scraper.py            # Enrichment Agent
│   ├── data_loader.py               # Data Loader Agent
│   ├── extrair_ano.py               # Data Agent
│   ├── corrigir_area.py             # Data Agent
│   ├── corrigir_area2.py            # Data Agent
│   └── corrigir_sexo.py             # Data Agent
├── atualizacoes/
│   ├── atualizar_dataset.py         # Update Agent - script de atualizacao
│   └── novos_pesquisadores.csv      # Gerado pelo dashboard quando há novos
├── data/
│   └── dataset.csv                  # Dataset final com 480 pesquisadores
├── dashboard/
│   └── app.py                       # Dashboard + Query + Logger + Validation
├── logs/
│   └── operacoes.log                # Log de todas as operações
├── docs/
│   ├── documentacao_projeto_cnpq.md
│   └── documentacao_projeto_cnpq_v5.docx
├── .env                             # Variáveis de ambiente (não versionado)
├── .gitignore
└── requirements.txt
```

### 4.2 Dataset Final (480 pesquisadores, 16 colunas)

| Campo | Descrição | Fonte |
|---|---|---|
| nome | Nome completo do pesquisador | CNPq |
| sexo | Masculino/Feminino | gender-guesser + dicionário manual |
| instituicao | Instituição de vínculo | CNPq |
| uf | Estado (UF) | Mapeamento por sigla da instituição |
| nivel_bolsa | Nível da bolsa CNPq (PQ-1A, PQ-1B, etc.) | CNPq |
| area_atuacao | Área de atuação detalhada | Lattes |
| ano_conclusao_doutorado | Ano de conclusão do doutorado | Extraído via regex |
| url_lattes | Link do Currículo Lattes | Lattes |
| google_scholar | Link de busca no Google Scholar | Gerado automaticamente |
| vigencia_inicio | Início da vigência da bolsa | CNPq |
| vigencia_termino | Término da vigência da bolsa | CNPq |
| situacao | Situação atual da bolsa | CNPq |
| formacao_academica | Formação acadêmica completa | Lattes |
| pos_doutorado | Pós-doutorado(s) realizados | Lattes |
| url | Link de busca no CNPq | Gerado automaticamente |
| ativo | S=ativo no CNPq / N=removido | Gerenciado automaticamente |

### 4.3 Google Scholar

O Google Scholar não possui API pública oficial. A automação via biblioteca `scholarly` foi testada mas o Google bloqueou todas as requisições. A solução adotada foi gerar uma URL de busca automaticamente:

```
https://scholar.google.com/scholar?q=Nome+do+Pesquisador
```

Ao clicar, o usuário é direcionado para a busca do Google Scholar com o nome do pesquisador já preenchido.

### 4.4 Update Agent (atualizacoes/atualizar_dataset.py)

Script Python multiplataforma (Windows, Mac e Linux) que:

1. Carrega o dataset atual
2. Carrega o arquivo `novos_pesquisadores.csv` gerado pelo dashboard
3. Solicita confirmação do usuário
4. Enriquece os dados (Google Scholar, URL Lattes)
5. Adiciona ao dataset e ordena alfabeticamente
6. Salva o dataset atualizado
7. Faz push automático para o GitHub

### 4.5 Evolução do Query Agent (5 versões)

| Versão | Abordagem | Problema | Solução |
|---|---|---|---|
| v1 | Groq + prompt simples | Alucinações, erros de cálculo | Dados pré-calculados |
| v2 | Groq + dados pré-calculados | Falha em cruzamentos de 3+ campos | LangChain Pandas Agent |
| v3 | Groq + LangChain | Erro 413 (limite 6.000 tokens) | Migração para GPT-4o |
| v4 | GPT-4o + dataset completo | Erro 429 (44.585 tokens) | Redução de colunas |
| v5 (final) | GPT-4o + colunas essenciais | Nenhum | Funcionando perfeitamente |

### 4.6 Log de Operações

| Operação | Quando ocorre |
|---|---|
| DASHBOARD INICIADO | Ao carregar o dashboard |
| VALIDACAO DO DATASET | Após carregar os dados |
| FILTRO APLICADO | Quando usuário seleciona filtros |
| EXPORTACAO CSV | Quando usuário baixa CSV |
| EXPORTACAO PDF | Quando usuário baixa PDF |
| CONSULTA LINGUAGEM NATURAL | Quando usuário faz uma pergunta |
| RESPOSTA GERADA | Após resposta bem-sucedida |
| ERRO NA CONSULTA | Em caso de falha na API |
| ATUALIZACAO DE DADOS | Quando usuário clica em Atualizar |
| ARQUIVO DE ATUALIZACAO GERADO | Quando usuário gera arquivo de novos pesquisadores |

---

## 5. Architecture Decision Records (ADRs)

### ADR-001: Adoção de Arquitetura Multi-Agentes

| Campo | Descrição |
|---|---|
| **Contexto** | O sistema precisa realizar tarefas complexas: scraping, enriquecimento, visualização, linguagem natural, logging, validação, gerenciamento de ciclo de vida e facilitar atualizações |
| **Decisão** | Adotar arquitetura multi-agentes com responsabilidades bem definidas |
| **Justificativa** | Permite separar responsabilidades, facilitar teste individual e substituição de partes sem afetar o todo |
| **Alternativas** | Sistema monolítico (difícil de manter), microserviços (desnecessário) |
| **Consequências** | Maior organização, facilidade de manutenção e extensibilidade |

### ADR-002: Escolha da Linguagem de Programação

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de scraping, processamento, interface web e integração com APIs de IA |
| **Decisão** | Python 3.x |
| **Justificativa** | Ecossistema rico com bibliotecas maduras para todas as necessidades |
| **Alternativas** | Node.js (menor suporte a data science), Java (mais verboso) |
| **Consequências** | Desenvolvimento rápido e código legível |

### ADR-003: Ferramenta de Scraping do CNPq

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de coletar dados da tabela do CNPq |
| **Decisão** | requests + BeautifulSoup4 |
| **Justificativa** | Site do CNPq retorna HTML estático, não requerendo JavaScript |
| **Alternativas** | Selenium (mais pesado), Scrapy (mais complexo) |
| **Consequências** | Scraping rápido e eficiente |

### ADR-004: Ferramenta de Scraping do Lattes

| Campo | Descrição |
|---|---|
| **Contexto** | O Lattes requer interação com formulários, cliques e CAPTCHA |
| **Decisão** | Selenium com ChromeDriver |
| **Tentativas anteriores** | requests direto (bloqueado pelo CAPTCHA), XML do Lattes (timeout) |
| **Mudança de abordagem** | Primeira versão identificou âncoras HTML incorretamente. DevTools corrigiu. |
| **Consequências** | Processo mais lento com CAPTCHA manual, mas funcional com reinício automático |

### ADR-005: Framework de Dashboard

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de interface web interativa sem expertise em frontend |
| **Decisão** | Streamlit |
| **Justificativa** | Dashboards interativos apenas com Python. Deploy gratuito. |
| **Alternativas** | Dash (mais complexo), Flask (requer frontend) |
| **Consequências** | Desenvolvimento rápido com menos flexibilidade de customização |

### ADR-006: Estratégia de Hospedagem

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de disponibilizar o dashboard online |
| **Decisão** | GitHub + Streamlit Community Cloud |
| **Primeira tentativa** | Execução local — bloqueada por firewall na porta 8501 |
| **Mudança de abordagem** | Deploy no Streamlit Community Cloud |
| **Consequências** | Sistema acessível de qualquer dispositivo |

### ADR-007: Fonte dos Dados no Dashboard

| Campo | Descrição |
|---|---|
| **Contexto** | Streamlit Cloud não acessa o CNPq diretamente (timeout) |
| **Decisão** | Fallback triplo: CNPq → GitHub → arquivo local |
| **Primeira tentativa** | Scraping em tempo real — bloqueado por timeout |
| **Mudança de abordagem** | Dataset no GitHub com verificação do CNPq para detectar mudanças |
| **Consequências** | Sistema resiliente com dados sempre disponíveis |

### ADR-008: Estratégia de Inferência de Sexo

| Campo | Descrição |
|---|---|
| **Contexto** | Dataset não contém o campo sexo |
| **Decisão** | gender-guesser + dicionário manual de nomes brasileiros |
| **Primeira tentativa** | Apenas gender-guesser — 96 indefinidos |
| **Mudança de abordagem** | Dicionário manual corrigiu 95. Erickson corrigido manualmente. |
| **Consequências** | 100% dos pesquisadores com sexo definido |

### ADR-009: Gerenciamento do Ciclo de Vida dos Pesquisadores

| Campo | Descrição |
|---|---|
| **Contexto** | Pesquisadores podem ser adicionados ou removidos do CNPq ao longo do tempo |
| **Decisão** | Campo ativo (S/N) — pesquisadores removidos nunca são excluídos |
| **Justificativa** | Preserva histórico. Pesquisador removido pode retornar. Dashboard exibe apenas ativo=S. |
| **Alternativas** | Exclusão física (perde histórico), tabela separada (desnecessário) |
| **Consequências** | Dados históricos preservados, dashboard sempre atualizado |

### ADR-010: Separação do Data Loader em Módulo Independente

| Campo | Descrição |
|---|---|
| **Contexto** | Função carregar_dados() dentro do app.py misturava responsabilidades |
| **Decisão** | Criar tools/data_loader.py com a lógica isolada |
| **Justificativa** | Princípio de Single Responsibility. Código mais limpo e testável. |
| **Implementação** | Cache do Streamlit mantido no app.py via wrapper |
| **Consequências** | Código organizado e fácil de manter |

### ADR-011: Evolução da Estratégia do Query Agent

| Campo | Descrição |
|---|---|
| **Contexto** | Necessidade de linguagem natural precisa para qualquer pergunta sobre os dados |
| **Decisão Final** | LangChain Pandas Agent com GPT-4o (Text-to-Pandas) |
| **Tentativa 1** | Groq + prompt simples — alucinações e erros de cálculo |
| **Tentativa 2** | Dados pré-calculados — falhou em cruzamentos de 3+ campos |
| **Tentativa 3** | Groq + LangChain — erro 413 (limite de 6.000 tokens) |
| **Tentativa 4** | GPT-4o + dataset completo — erro 429 (44.585 tokens) |
| **Solução Final** | GPT-4o com apenas colunas essenciais do DataFrame |
| **Justificativa** | Text-to-Pandas garante precisão total — modelo gera código pandas executado nos dados reais |
| **Consequências** | Qualquer pergunta respondida com precisão, incluindo cruzamentos de múltiplos campos |

### ADR-012: Estratégia para Google Scholar

| Campo | Descrição |
|---|---|
| **Contexto** | O professor solicitou o Google Scholar como campo do dataset |
| **Decisão** | URL de busca gerada automaticamente com o nome do pesquisador |
| **Tentativa 1** | Biblioteca scholarly — Google bloqueou todas as requisições automaticamente |
| **Tentativa 2** | ScraperAPI (pago) — avaliado como lento e com risco de dados incorretos |
| **Solução adotada** | URL de busca: https://scholar.google.com/scholar?q=Nome+do+Pesquisador |
| **Justificativa** | Google Scholar não possui API pública. Qualquer automação pode violar os termos de uso. A URL de busca é funcional e honesta. |
| **Consequências** | Campo preenchido para todos os 480 pesquisadores com link funcional |

### ADR-013: Estratégia de Atualização de Novos Pesquisadores

| Campo | Descrição |
|---|---|
| **Contexto** | Quando novos pesquisadores são detectados no CNPq, precisam ser adicionados ao dataset com dados completos |
| **Decisão** | Dashboard gera arquivo CSV + script Python multiplataforma para atualização local |
| **Tentativa 1** | Formulário manual no dashboard — dados não persistiam entre sessões |
| **Tentativa 2** | Streamlit Storage — complexidade desnecessária para o escopo |
| **Solução adotada** | Dashboard gera novos_pesquisadores.csv + script atualizar_dataset.py para rodar localmente |
| **Justificativa** | Selenium não pode rodar no Streamlit Cloud. Script local é mais confiável, transparente e auditável. |
| **Consequências** | Processo documentado e reproduzível, com confirmação explícita do usuário |

---

## 6. Testes e Inconsistências

### 6.1 Testes Realizados

| Teste | Resultado Esperado | Resultado Obtido |
|---|---|---|
| Scraping do CNPq | 480 pesquisadores ordenados | Funcionando |
| Geração do CSV | 16 colunas ordenado alfabeticamente | Funcionando |
| Inferência de sexo | 100% classificados | 100% após correção manual |
| Mapeamento de UF | Sem NaN | 480 com UF |
| Scraping do Lattes | Dados de formação e área | 480 enriquecidos |
| Google Scholar | Link de busca para todos | Funcionando |
| Campo ativo | S para todos | 480 com ativo=S |
| Fallback CNPq indisponível | Usa GitHub com aviso | Funcionando |
| Detecção de novos pesquisadores | Exibe aviso + botão | Funcionando |
| Geração de arquivo de atualização | CSV gerado + script exibido | Funcionando |
| Script de atualização local | Atualiza dataset + push GitHub | Funcionando |
| Ordenação alfabética | Dataset ordenado após atualização | Funcionando |
| Filtros do dashboard | 5 critérios | Funcionando |
| Exportação CSV e PDF | Download | Funcionando |
| LN - pergunta simples | Resposta precisa | Funcionando |
| LN - cruzamento 3 campos | Resultado correto | Funcionando com GPT-4o |
| LN - fora do escopo | Recusar resposta | Funcionando |
| Log de operações | Registrar ações | Funcionando |
| Validações de integridade | Alertar problemas | Funcionando |
| Deploy Streamlit Cloud | Dashboard online | Funcionando |

### 6.2 Inconsistências Identificadas e Corrigidas

| Inconsistência | Quantidade | Solução |
|---|---|---|
| Pesquisadores com sexo Indefinido | 96 | Dicionário manual de nomes brasileiros |
| Sexo indefinido restante (Erickson) | 1 | Correção manual |
| Área de atuação incorreta | 10 | Reprocessamento com Selenium |
| Pesquisador com URL inválida (Lucchesi) | 1 | Correção manual |
| Instituições sem mapeamento de UF | 13 | Adicionadas ao dicionário |
| Modelo errando cálculos numéricos | Vários | Migração para Text-to-Pandas |
| Erro 413 Groq (6.000 tokens) | 1 | Migração para GPT-4o |
| Erro 429 GPT-4o (44.585 tokens) | 1 | Redução para colunas essenciais |
| Google Scholar bloqueado | 1 | URL de busca automática |
| Dataset desorganizado após atualização | 1 | Ordenação alfabética automática |
| Script não encontrava novos_pesquisadores.csv | 1 | Download do arquivo pelo dashboard |

---

## 7. Implantação

### 7.1 Processo de Deploy

1. Desenvolvimento e testes locais com Python
2. Versionamento no GitHub (repositório: elengreice/projeto-cnpq)
3. Configuração das variáveis de ambiente no Streamlit Cloud (GROQ_API_KEY, OPENAI_API_KEY)
4. Deploy automático via Streamlit Community Cloud
5. Validação do sistema em produção

### 7.2 Processo de Atualização de Novos Pesquisadores

1. Dashboard detecta novo pesquisador e exibe aviso
2. Usuário clica em "Gerar arquivo de atualizacao"
3. Sistema gera `atualizacoes/novos_pesquisadores.csv`
4. Usuário baixa o arquivo e salva em `atualizacoes/` localmente
5. Usuário roda: `python atualizacoes/atualizar_dataset.py`
6. Script atualiza dataset, ordena e faz push para GitHub
7. Dashboard recarrega com dados atualizados

### 7.3 Variáveis de Ambiente

| Variável | Uso |
|---|---|
| GROQ_API_KEY | API Groq (mantida como backup) |
| OPENAI_API_KEY | API OpenAI GPT-4o para o Query Agent |

---

## 8. Model Context Protocol (MCP)

O MCP define como o modelo de linguagem interage com o contexto dos dados.

### 8.1 Arquitetura Text-to-Pandas

1. Usuário faz uma pergunta em linguagem natural
2. LangChain envia o schema do DataFrame + pergunta para o GPT-4o
3. GPT-4o raciocina e gera código pandas para responder
4. LangChain executa o código no DataFrame real
5. GPT-4o formata o resultado em português
6. Dashboard exibe a resposta ao usuário

### 8.2 Vantagem sobre Abordagem Anterior

| Abordagem anterior | Abordagem atual (Text-to-Pandas) |
|---|---|
| Dados pré-calculados enviados ao modelo | Código pandas gerado e executado |
| Limitado a cruzamentos previstos | Qualquer cruzamento possível |
| Risco de alucinação | Resultado calculado nos dados reais |
| Falha em perguntas complexas | Funciona para qualquer pergunta |

---

## 9. Qualidade e Resiliência

### 9.1 Resiliência do Sistema

| Componente | Mecanismo de Resiliência |
|---|---|
| Carregamento de dados | Fallback triplo: CNPq → GitHub → local |
| Enrichment Agent | Reinício automático, 3 tentativas por pesquisador |
| Dataset | Campo ativo preserva histórico de removidos |
| Query Agent | Text-to-Pandas elimina alucinações |
| Dashboard | Validações automáticas alertam sobre problemas |
| Atualização | Confirmação explícita antes de qualquer mudança |

### 9.2 Exemplo Real do Log

```
2026-05-30 19:06:47 | INFO | DASHBOARD INICIADO | CNPq disponivel. Total: 480
2026-05-30 19:06:47 | INFO | VALIDACAO DO DATASET | Dataset valido com 480 pesquisadores
2026-05-30 19:06:55 | INFO | FILTRO APLICADO | UF: ['BA']
2026-05-30 19:07:10 | INFO | CONSULTA LINGUAGEM NATURAL | Pergunta: Quantos pesquisadores femininos tem na Bahia com nivel PQ-2?
2026-05-30 19:07:12 | INFO | RESPOSTA GERADA | Pergunta respondida com sucesso
2026-05-30 19:08:00 | INFO | ARQUIVO DE ATUALIZACAO GERADO | Novos pesquisadores: ['João Silva']
```

---

## 10. Conclusão

O sistema multi-agentes desenvolvido atende a todos os requisitos propostos. A evolução mais significativa foi o Query Agent, que passou por 5 versões até chegar à solução final com LangChain Pandas Agent + GPT-4o.

### 10.1 Principais Desafios e Soluções

| Desafio | Solução Adotada |
|---|---|
| Firewall bloqueando Streamlit local | Deploy no Streamlit Community Cloud |
| CNPq bloqueando acesso do Streamlit Cloud | Fallback triplo com dataset no GitHub |
| CAPTCHA no Currículo Lattes | Selenium com resolução manual |
| Sessão do Selenium sendo perdida | Reinício automático com retomada de progresso |
| Cartão brasileiro rejeitado na OpenAI | Uso temporário da chave de colega |
| 96 pesquisadores com sexo indefinido | Dicionário manual de nomes brasileiros |
| Alucinações no Query Agent | Migração para Text-to-Pandas com GPT-4o |
| Erro 413 Groq | Migração para GPT-4o |
| Erro 429 GPT-4o | Redução para colunas essenciais |
| Google Scholar bloqueado | URL de busca automática |
| Pesquisadores novos/removidos | Campo ativo com detecção automática |
| Persistência de dados de novos pesquisadores | Script local + download do CSV |
| Dataset desorganizado | Ordenação alfabética automática |

### 10.2 Limitações Conhecidas

- **Google Scholar:** link de busca em vez de perfil direto
- **Enrichment de novos:** dados do Lattes requerem execução local do script
- **Selenium:** não pode rodar no Streamlit Cloud
- **Atualização:** requer execução manual do script localmente

### 10.3 Melhorias Futuras

- Automação completa da atualização via agendamento
- Integração com API oficial do Lattes quando disponível
- Busca automatizada do Google Scholar via ScraperAPI
- Interface no dashboard para preencher dados do Lattes de novos pesquisadores com persistência via banco de dados externo (Supabase ou Firebase)
- Notificações automáticas quando o dataset ficar desatualizado
