# MIA Assistente de Design de Interiores com IA

## Relatório Técnico

**Autores:**
- Diego Jefferson Mendes Silva (pg59999@alunos.uminho.pt)
- Vicente de Carvalho Castro (pg60395@alunos.uminho.pt)

**Instituição:** Universidade do Minho - Escola de Engenharia  
**Disciplina:** Introdução a Inteligência Artificial (IIA)  

---

## 1. Resumo Executivo

Este projeto consiste no desenvolvimento de um assistente inteligente de design de interiores baseado em modelos de linguagem (LLM) e visão computacional. A aplicação permite aos utilizadores interagir através de texto e imagem, recebendo conselhos profissionais e personalizados para melhorar espaços interiores e aumentar o valor de propriedades imobiliárias.

O sistema foi desenvolvido utilizando tecnologias modernas como **Ollama**, **LangGraph**, **Hyperdiv** e containers Docker, garantindo portabilidade, escalabilidade e facilidade de implementação.

---

## 2. Arquitetura do Sistema

### 2.1. Visão Geral

A aplicação segue uma arquitetura em camadas com os seguintes componentes principais:

```
┌─────────────────────────────────────────┐
│    Interface Web (Hyperdiv Frontend)    │
├─────────────────────────────────────────┤
│      Camada de Aplicação (main.py)      │
├─────────────────────────────────────────┤
│  Serviço de Chatbot (chatbot.py)        │
│  - LangGraph Workflow                   │
│  - Nós de Processamento                 │
├─────────────────────────────────────────┤
│      Modelos de IA (Ollama)             │
│  - LLaMA 3 (Texto)                      │
│  - LLaVA (Visão)                        │
└─────────────────────────────────────────┘
```

### 2.2. Componentes Tecnológicos

#### 2.2.1. Frontend
- **Hyperdiv (v0.1.9)**: Framework Python para criação de interfaces web reativas
- **Plugin personalizado**: Componente JavaScript para upload de imagens (`file_picker.js`)

#### 2.2.2. Backend
- **Python 3.13**: Linguagem principal do projeto
- **Poetry**: Gestão de dependências e ambientes virtuais
- **LangGraph (v1.0.5)**: Orquestração de fluxos conversacionais com grafos
- **LangChain-Ollama (v1.0.1)**: Integração com modelos Ollama

#### 2.2.3. Modelos de IA
- **LLaMA 3**: Modelo de linguagem para processamento de texto
- **LLaVA**: Modelo multimodal para análise de imagens

#### 2.2.4. Infraestrutura
- **Docker & Docker Compose**: Containerização e orquestração
- **Ollama**: Servidor local de modelos LLM

---

## 3. Estrutura do Projeto

```
IIA/
├── docker-compose.yaml      # Orquestração de containers
├── Dockerfile               # Imagem da aplicação
├── Makefile                 # Automação de comandos
├── pyproject.toml           # Configuração Poetry
├── README.md                # Documentação
└── src/
    ├── main.py              # Aplicação principal Hyperdiv
    ├── assets/
    │   └── file_picker.js   # Plugin de upload de imagens
    └── services/
        └── chatbot.py       # Serviço de chatbot com LangGraph
```

---

## 4. Descrição Detalhada dos Componentes

### 4.1. Aplicação Principal (`main.py`)

O ficheiro `main.py` contém a interface web construída com Hyperdiv. As principais funcionalidades incluem:

#### **Plugin de Upload de Imagem**
```python
class file_picker(hd.Plugin):
    _assets_root = os.path.join(os.path.dirname(__file__), "assets")
    _assets = ["file_picker.js"]
    image_metadata = hd.Prop(hd.Any, None)
    disabled = hd.Prop(hd.Bool, False)
```

Define um plugin personalizado que permite aos utilizadores carregar imagens para análise. O plugin utiliza JavaScript para criar um botão de upload que converte imagens para Base64.

#### **Gestão de Estado**
O sistema mantém um estado reativo que inclui:
- Histórico de mensagens
- Resposta atual do assistente
- Metadados de imagens carregadas
- Identificador único de mensagens

#### **Interface de Chat**
Interface responsiva com:
- Caixa de texto para entrada de perguntas
- Botão de upload de imagens
- Área de visualização do histórico de conversação
- Indicadores de estado (loading, modelo utilizado)

### 4.2. Serviço de Chatbot (`chatbot.py`)

Implementa a lógica de processamento utilizando **LangGraph** para orquestrar diferentes modelos de IA:

#### **Grafo de Estados**
```python
workflow = StateGraph(dict)
workflow.add_node("vision_llm", self.vision_node)
workflow.add_node("text_llm", self.text_node)
workflow.add_node("improve_space_node", self.improve_space_node)
```

O grafo define três nós principais:

1. **`vision_llm`**: Processa imagens com o modelo LLaVA
   - Recebe imagem em Base64
   - Gera descrição detalhada do espaço
   - Identifica elementos de design

2. **`text_llm`**: Processa consultas apenas de texto
   - Fornece conselhos diretos
   - Utiliza o modelo LLaMA 3

3. **`improve_space_node`**: Combina análise visual e textual
   - Integra descrição da imagem
   - Gera recomendações estruturadas
   - Prioriza alterações de alto impacto

#### **Roteamento Condicional**
```python
def router(self, state):
    if state.get('image_bytes'):
        return "vision"
    return "text"
```

O sistema decide automaticamente o fluxo baseado na presença de imagem:
- **Com imagem**: `vision_llm` → `improve_space_node`
- **Sem imagem**: `text_llm` → END

### 4.3. Plugin JavaScript (`file_picker.js`)

Componente frontend que:
- Cria um botão de upload estilizado
- Aceita apenas ficheiros de imagem
- Converte imagens para Base64
- Atualiza propriedades reativas do Hyperdiv
- Permite reset para novo upload

### 4.4. Infraestrutura Docker

#### **Dockerfile**
- Base: Python 3.13 Slim
- Instala Poetry para gestão de dependências
- Configura variáveis de ambiente do Hyperdiv
- Expõe porta 8888

#### **docker-compose.yaml**
Define dois serviços:

1. **Ollama**:
   - Baixa modelos LLaMA 3 e LLaVA automaticamente
   - Expõe API na porta 11434
   - Volume persistente para modelos

2. **App**:
   - Construída a partir do Dockerfile
   - Depende do serviço Ollama
   - Mapeamento de porta 8080:8888

---

## 5. Fluxo de Processamento

### 5.1. Consulta com Imagem

```
1. Utilizador carrega imagem + texto
2. Interface converte imagem para Base64
3. Estado atualizado com image_bytes
4. Router direciona para "vision"
5. vision_llm analisa imagem (LLaVA)
6. improve_space_node combina análise + contexto
7. Resposta estruturada em PT-PT
8. Interface exibe resposta com streaming
```

### 5.2. Consulta Apenas Texto

```
1. Utilizador insere pergunta
2. Estado atualizado sem image_bytes
3. Router direciona para "text"
4. text_llm processa com LLaMA 3
5. Resposta traduzida para PT-PT
6. Interface exibe resposta com streaming
```

---

## 6. Como Utilizar a Aplicação

### 6.1. Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **Make** instalado (disponível por defeito no macOS e Linux)
- Mínimo de 8GB de RAM (recomendado 16GB para modelos LLM)
- Espaço em disco: ~10GB para modelos

### 6.2. Comandos do Makefile

O projeto inclui um Makefile com comandos automatizados:

#### **Iniciar a aplicação**
```bash
make up
```
Este comando:
- Inicia os containers em modo detached (`-d`)
- Aguarda 5 segundos pela inicialização
- Abre automaticamente o navegador em `http://localhost:8080`

#### **Parar a aplicação**
```bash
make down
```
Este comando:
- Para todos os containers
- Remove os containers e redes criadas
- Mantém os volumes (modelos permanecem guardados)

#### **Reconstruir e reiniciar**
```bash
make build
```
Este comando é útil quando:
- Modifica código Python ou JavaScript
- Altera dependências no `pyproject.toml`
- Atualiza Dockerfile
- Executa `docker compose up -d --build`
- Abre o navegador automaticamente

### 6.3. Primeiro Uso

1. **Iniciar o sistema**:
   ```bash
   make up
   ```

2. **Aguardar download dos modelos**:
   - Na primeira execução, o Ollama fará download do LLaMA 3 (~4.7GB) e LLaVA (~4.7GB)
   - Este processo pode demorar 10-30 minutos dependendo da ligação à internet
   - Monitore o progresso com:
     ```bash
     docker logs -f ollama
     ```

3. **Aceder à aplicação**:
   - O navegador abrirá automaticamente em `http://localhost:8080`
   - Se não abrir, aceda manualmente ao endereço

4. **Utilizar o chat**:
   - Digite perguntas sobre design de interiores
   - Use o botão `+` para adicionar imagens
   - Clique em "Enviar" ou pressione Enter
   - Aguarde a resposta (com indicador de loading)

### 6.4. Exemplos de Uso

#### **Consulta de Texto**:
```
"Como posso tornar a minha sala mais luminosa?"
"Quais as cores recomendadas para aumentar o valor de venda?"
"Dá-me ideias para decoração minimalista"
```

#### **Consulta com Imagem**:
1. Carregar foto da divisão
2. Escrever: "Como posso melhorar este espaço para venda?"
3. O sistema analisará a imagem e fornecerá sugestões específicas

### 6.5. Resolução de Problemas

#### **Containers não iniciam**:
```bash
docker compose logs
```

#### **Modelos não descarregam**:
```bash
docker exec -it ollama ollama list
docker exec -it ollama ollama pull llama3
docker exec -it ollama ollama pull llava
```

#### **Porta já em uso**:
Editar `docker-compose.yaml` e alterar:
```yaml
ports:
  - "8081:8888"  # Usar porta 8081 em vez de 8080
```

#### **Limpar tudo e recomeçar**:
```bash
make down
docker volume rm iia_ollama  # Remove modelos (requer novo download)
make up
```

---

## 7. Configuração e Personalização

### 7.1. Variáveis de Ambiente

No `Dockerfile`:
```dockerfile
ENV HD_HOST="0.0.0.0"       # Interface de rede
ENV HD_PORT="8888"          # Porta interna
ENV HD_PRODUCTION="true"    # Modo de produção
```

No `docker-compose.yaml`:
```yaml
environment:
  - OLLAMA_BASE_URL=http://ollama:11434  # URL do Ollama
```

### 7.2. Ajuste de Modelos

Para utilizar modelos diferentes, editar `chatbot.py`:
```python
self.model_texto = ChatOllama(
    model="llama3",  # Alterar para outro modelo
    base_url=ollama_url,
    streaming=True
)
```

Modelos disponíveis: https://ollama.ai/library

### 7.3. Personalização da Interface

A interface pode ser customizada editando `main.py`:
- Cores e estilos através dos parâmetros do Hyperdiv
- Mensagem inicial em `initial_message`
- System prompts nos nós do `chatbot.py`

---

## 8. Dependências do Projeto

Definidas em `pyproject.toml`:

| Dependência | Versão | Função |
|------------|--------|--------|
| python | >=3.11,<4.0 | Linguagem base |
| ollama | >=0.6.1,<0.7.0 | Cliente Ollama |
| hyperdiv | >=0.1.9,<0.2.0 | Framework web |
| requests | >=2.32.5,<3.0.0 | HTTP client |
| langgraph | >=1.0.5,<2.0.0 | Orquestração de grafos |
| langchain-ollama | >=1.0.1,<2.0.0 | Integração LangChain |

### 8.1. Gestão com Poetry

Poetry é utilizado para gestão de dependências:

```bash
# Adicionar nova dependência
poetry add <package>

# Atualizar dependências
poetry update

# Instalar dependências
poetry install
```

---

## 9. Considerações de Performance

### 9.1. Requisitos de Hardware

- **CPU**: Mínimo 4 cores (recomendado 8+ cores)
- **RAM**: Mínimo 8GB (recomendado 16GB)
- **Disco**: 15GB livres (10GB para modelos + 5GB para sistema)
- **GPU**: Opcional, melhora significativamente a velocidade (NVIDIA com CUDA)

### 9.2. Otimizações

- **Streaming**: Respostas são transmitidas em tempo real
- **Cache de modelos**: Modelos permanecem em memória entre requests
- **Containers**: Isolamento e gestão eficiente de recursos

### 9.3. Tempos de Resposta Esperados

- **Consulta de texto**: 2-10 segundos
- **Consulta com imagem**: 10-30 segundos
- **Primeira inicialização**: 10-30 minutos (download de modelos)

---

## 10. Segurança e Boas Práticas

### 10.1. Considerações de Segurança

- Aplicação projetada para uso local/desenvolvimento
- Não recomendado para exposição direta à internet sem autenticação
- Imagens são processadas localmente (privacidade garantida)

### 10.2. Produção

Para ambiente de produção, considerar:
- Implementar autenticação (OAuth, JWT)
- Configurar HTTPS/TLS
- Implementar rate limiting
- Adicionar logs e monitorização
- Utilizar reverse proxy (Nginx, Traefik)

---

## 11. Desenvolvimento Futuro

### Funcionalidades Potenciais
- [ ] Histórico de conversações persistente
- [ ] Export de sugestões em PDF
- [ ] Biblioteca de referências de design
- [ ] Integração com catálogos de móveis
- [ ] Estimativa de custos de implementação
- [ ] Suporte multi-idioma
- [ ] Análise comparativa de "antes/depois"

### Melhorias Técnicas
- [ ] Testes unitários e de integração
- [ ] CI/CD pipeline
- [ ] Documentação API
- [ ] Monitorização com Prometheus/Grafana
- [ ] Suporte a GPU para acelerar inferência

---

## 12. Licença e Contribuições

Este projeto foi desenvolvido no âmbito académico da Universidade do Minho para a disciplina de Introdução a Inteligência Artificial (IIA).

### Autores
- **Diego Jefferson Mendes Silva**
- **Vicente de Carvalho Castro**

---

## 13. Referências

- [Ollama Documentation](https://ollama.ai/docs)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Hyperdiv Documentation](https://hyperdiv.io/docs)
- [LLaMA 3 Model Card](https://ollama.ai/library/llama3)
- [LLaVA Model Card](https://ollama.ai/library/llava)
- [Docker Documentation](https://docs.docker.com/)

---

## 14. Contacto e Suporte

Para questões ou sugestões sobre este projeto:
- Diego Jefferson: pg59999@alunos.uminho.pt
- Vicente de Carvalho: pg60395@alunos.uminho.pt

**Universidade do Minho - Escola de Engenharia**  