# Prompts Automáticos para Geração de Mapeamento via LLM

Para utilizar a ferramenta `reqgraph` de forma global e com **100% de automação** em novos projetos, nós introduzimos um documento de prompt base. 

Você pode copiar o prompt abaixo e colá-lo em qualquer LLM (como ChatGPT, Claude, Gemini, etc.), fornecendo os arquivos ou a estrutura do seu código fonte. A IA vai devolver o arquivo `mapeamento.py` perfeito exigido pelo seu projeto.

---

### Copie o texto abaixo:

```text
Atue como um Engenheiro de Requisitos Sênior. Estou anexando o código-fonte de um projeto Python.

A minha ferramenta de rastreabilidade baseada em AST precisa de um dicionário chamado `func_to_req` que mapeia o nome de cada função/método do projeto para o requisito estrutural correspondente.

Regras Obrigatórias:
1. Retorne APENAS código Python válido. Não adicione textos explicativos, markdown ou falas.
2. Crie uma única variável global chamada `func_to_req` que é um dicionário.
3. As chaves devem ser as strings do nome **curto e final** da função (ex: para uma função `user.verify_password`, a chave será apenas `"verify_password"`).
4. Os valores devem ser strings do requisito em UPPERCASE, prefixadas de `REQ_` (Ex: `"REQ_AUTENTICACAO"`, `"REQ_DATABASE"`, `"REQ_CORE_LOGIC"`).
5. Agrupe de forma inteligente funções do mesmo domínio/entidade de negócio sob o mesmo `REQ_`.

Código-fonte que deve ser analisado:
[COLE AS PASTAS OU ARQUIVOS AQUI]
```
