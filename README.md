# ReqGraph

**ReqGraph** é uma ferramenta standalone de rastreabilidade automática de requisitos. Ela analisa o código fonte de qualquer projeto Python (via AST - *Abstract Syntax Tree*), extrai o grafo de chamadas de funções e métodos e, a partir de um mapeamento fornecido, deriva um Grafo de Requisitos e gera visualizações automáticas.

---

## 🚀 Instalação

Como o `reqgraph` é um projeto estruturado como pacote Python, recomenda-se instalá-lo no seu ambiente virtual local.

### Opção 1: Via pip install (Recomendada)
Estando no diretório principal do pacote (onde está o `setup.py`), execute:
```bash
pip install -e .
```
*(Isso instala as dependências e torna o comando `reqgraph` globalmente acessível no seu ambiente).*

### Opção 2: Via requirements.txt
Se preferir apenas instalar as dependências manualmente:
```bash
pip install -r requirements.txt
```

---

## 🤖 Automação 100% via LLM (Novo Projeto)

Não é mais necessário escrever o mapeamento função → requisito manualmente! 

Para rodar essa biblioteca **em qualquer repositório de projeto diferente**, disponibilizamos um prompt pronto para que uma Inteligência Artificial crie isso para você. 

Siga este guia simples:
1. Abra o arquivo [llm_prompt_mapping.md](llm_prompt_mapping.md) incluso nesta biblioteca.
2. Copie o texto do prompt e cole em seu LLM favorito (ChatGPT, Gemini, Claude).
3. Anexe os arquivos do projeto que deseja rastrear.
4. Salve a resposta do LLM como o arquivo `mapeamento.py` dentro do seu repositório alvo.
5. Em seguida, basta usar o próprio CLI da biblioteca `reqgraph` para extrair os grafos visuais. 

---

## 🛠️ Como Executar

**Aviso Importante sobre importação:**
Se você optou pela **Opção 2** (apenas requirements.txt), você **não deve executar** o arquivo interno `__main__.py` diretamente. Você precisa ir para o diretório raiz pai da pasta `reqgraph` e rodá-lo como um módulo do Python (`-m`):

```bash
# Estando na pasta pai (ex: MODELO_FRAM)
python -m reqgraph o_meu_projeto_de_teste/ --mapping o_meu_projeto_de_teste/mapeamento.py
```

Se você o instalou via **Opção 1** (`pip install -e .`), basta usar a interface de linha de comando gerada de qualquer diretório:
```bash
reqgraph C:\Caminho\Ate\Qualquer\Projeto --mapping C:\Caminho\Ate\Qualquer\Projeto\mapeamento.py
```

---

## 📋 Requisitos do Projeto Alvo ("Teste")

Para que o **reqgraph** funcione corretamente no projeto que você deseja analisar, este projeto-alvo **deve atender obrigatoriamente** as seguintes regras básicas:

1. **Arquivo de Mapeamento**: Deve existir um arquivo Python (geralmente chamado de `mapeamento.py`) contendo um dicionário global exato chamado `func_to_req`.
   
   Exemplo exigido de conteúdo do `mapeamento.py`:
   ```python
   func_to_req = {
       "login": "REQ_AUTENTICACAO",
       "query_user": "REQ_BANCO_DE_DADOS",
       "checkout": "REQ_PAGAMENTOS"
   }
   ```
   > Observação: Apenas forneça o nome final (curto) da função. Em `auth.login`, mapeie apenas `"login": "REQ_X"`. Em métodos de classe `app.AuthService.login`, mapeie também apenas `"login": "REQ_X"`.

2. **Sintaxe Python Correta**: Como a biblioteca utiliza extração por AST, os arquivos `.py` do seu projeto teste não podem ter erros de sintaxe graves.

3. **Invocação Legítima de Métodos e Funções**: 
   - A ferramenta lida com invocações diretas `nome_funcao()`
   - Atributos com o módulo `nome_modulo.nome_funcao()`
   - Chamadas a si mesmo dentro de classes via `self.nome_metodo()`
   *(Importações ambíguas ou construções excessivamente dinâmicas como getattr() e exec() escapam da coleta em AST).*

---

## 📊 O que é exportado?

Após a execução bem-sucedida, o `reqgraph` criará dentro do projeto alvo que foi avaliado os seguintes arquivos:

- `call_graph.png`: Visualização do grafo de chamadas de funções usando networkx.
- `req_graph.png`: Visualização do grafo construído de requisitos pendentes.
- `req_graph.json`: Versão serializada em JSON para integrações com outros softwares.
- `req_graph.dot`: Representação textual padrão graphviz de todas as ramificações de requisitos.
