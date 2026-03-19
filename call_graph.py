"""
call_graph.py — Extração de Call Graph via análise estática (AST).

Funcionalidades:
  - Suporte a funções e métodos de classe
  - Resolução de imports entre módulos do projeto
  - Filtragem de chamadas (mantém apenas funções do projeto)
"""

import ast
import os
from collections import defaultdict


# ═══════════════════════════════════════════════════════════════════════════
# Visitor — percorre a AST de um único módulo
# ═══════════════════════════════════════════════════════════════════════════

class CallGraphVisitor(ast.NodeVisitor):
    """Visita a AST e registra caller → callee para funções e métodos."""

    def __init__(self, module_name, import_map, module_set):
        self.module_name = module_name
        self.import_map = import_map          # alias → módulo real
        self.module_set = module_set          # nomes de módulos do projeto
        self.current_function = None
        self.current_class = None
        self.calls = defaultdict(set)

    # ── Classes ────────────────────────────────────────────────────────────
    def visit_ClassDef(self, node):
        previous_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = previous_class

    # ── Funções / Métodos ──────────────────────────────────────────────────
    def visit_FunctionDef(self, node):
        previous = self.current_function
        if self.current_class:
            self.current_function = f"{self.module_name}.{self.current_class}.{node.name}"
        else:
            self.current_function = f"{self.module_name}.{node.name}"
        self.generic_visit(node)
        self.current_function = previous

    visit_AsyncFunctionDef = visit_FunctionDef

    # ── Chamadas ───────────────────────────────────────────────────────────
    def visit_Call(self, node):
        if self.current_function is None:
            self.generic_visit(node)
            return

        callee = self._resolve_call(node)
        if callee:
            self.calls[self.current_function].add(callee)
        self.generic_visit(node)

    # ── Resolução de nome ──────────────────────────────────────────────────
    def _resolve_call(self, node):
        # ① chamada simples: foo()
        if isinstance(node.func, ast.Name):
            name = node.func.id
            # se veio de um 'from modulo import func'
            if name in self.import_map:
                return self.import_map[name]
            # função local do próprio módulo
            return f"{self.module_name}.{name}"

        # ② chamada com atributo: modulo.func() / self.method() / obj.method()
        if isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            value = node.func.value

            # self.method() → método da classe atual
            if isinstance(value, ast.Name) and value.id == "self":
                if self.current_class:
                    return f"{self.module_name}.{self.current_class}.{attr}"

            # modulo.func()  — resolve via import map
            if isinstance(value, ast.Name):
                alias = value.id
                real_module = self.import_map.get(alias, alias)
                # se é um módulo conhecido do projeto
                if real_module in self.module_set:
                    return f"{real_module}.{attr}"
                return f"{real_module}.{attr}"

            # ③ cadeia: modulo.Classe.metodo() — encadeia
            if isinstance(value, ast.Attribute) and isinstance(value.value, ast.Name):
                outer = value.value.id
                mid = value.attr
                real_module = self.import_map.get(outer, outer)
                return f"{real_module}.{mid}.{attr}"

        return None


# ═══════════════════════════════════════════════════════════════════════════
# Extração de imports
# ═══════════════════════════════════════════════════════════════════════════

def _extract_imports(tree, module_set):
    """
    Extrai o mapa de imports de uma AST.

    Diferencia:
      - `import auth`          → {"auth": "auth"}
      - `from database import connect_db` → {"connect_db": "database.connect_db"}
    """
    import_map = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias_node in node.names:
                key = alias_node.asname or alias_node.name
                import_map[key] = alias_node.name

        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias_node in node.names:
                key = alias_node.asname or alias_node.name
                # para 'from modulo import func', resolver como modulo.func
                if mod in module_set:
                    import_map[key] = f"{mod}.{alias_node.name}"
                else:
                    import_map[key] = f"{mod}.{alias_node.name}" if mod else alias_node.name
    return import_map


# ═══════════════════════════════════════════════════════════════════════════
# Builder — analisa o projeto inteiro
# ═══════════════════════════════════════════════════════════════════════════

class CallGraphBuilder:
    """Constrói o Call Graph de um projeto Python."""

    IGNORE_FILES = {"__init__.py", "setup.py"}

    def __init__(self):
        self.graph = defaultdict(set)
        self.all_functions = set()
        self.module_set = set()

    def analyze_project(self, root_path, ignore_files=None):
        """
        Analisa todos os .py de root_path e devolve o call graph.

        Parâmetros
        ----------
        root_path : str
            Caminho raiz do projeto a analisar.
        ignore_files : set[str] | None
            Nomes de arquivo .py para ignorar (ex: {"mapeamento.py"}).

        Retorna
        -------
        dict[str, set[str]]
        """
        skip = self.IGNORE_FILES | (ignore_files or set())

        # Primeiro passo: descobrir todos os módulos do projeto
        py_files = []
        for root, _dirs, files in os.walk(root_path):
            for fname in files:
                if fname.endswith(".py") and fname not in skip:
                    filepath = os.path.join(root, fname)
                    module_name = os.path.splitext(fname)[0]
                    self.module_set.add(module_name)
                    py_files.append((filepath, module_name))

        # Segundo passo: analisar cada arquivo
        for filepath, module_name in py_files:
            with open(filepath, "r", encoding="utf-8") as fh:
                source = fh.read()

            try:
                tree = ast.parse(source, filename=filepath)
            except SyntaxError as exc:
                print(f"[AVISO] Erro de sintaxe em {filepath}: {exc}")
                continue

            # Registrar todas as funções/métodos definidos
            self._register_definitions(tree, module_name)

            # Extrair imports e visitar chamadas
            import_map = _extract_imports(tree, self.module_set)
            visitor = CallGraphVisitor(module_name, import_map, self.module_set)
            visitor.visit(tree)

            for caller, callees in visitor.calls.items():
                self.graph[caller].update(callees)

        # Terceiro passo: filtrar para manter apenas callees reais
        filtered = defaultdict(set)
        for caller, callees in self.graph.items():
            for callee in callees:
                if callee in self.all_functions:
                    filtered[caller].add(callee)

        self.graph = dict(filtered)
        return self.graph

    def _register_definitions(self, tree, module_name):
        """Registra todas as funções e métodos definidos no módulo."""
        current_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                current_class = node.name
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        full = f"{module_name}.{current_class}.{item.name}"
                        self.all_functions.add(full)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Só registrar se for top-level (não já registrado como método)
                full = f"{module_name}.{node.name}"
                self.all_functions.add(full)


# ═══════════════════════════════════════════════════════════════════════════
# Utilitário de impressão
# ═══════════════════════════════════════════════════════════════════════════

def print_call_graph(graph):
    """Imprime o call graph de forma legível."""
    print("=" * 64)
    print("  GRAFO DE CHAMADAS (Call Graph)")
    print("=" * 64)
    if not graph:
        print("  (vazio)")
    for caller in sorted(graph):
        for callee in sorted(graph[caller]):
            print(f"  {caller}  -->  {callee}")
    print("=" * 64)
