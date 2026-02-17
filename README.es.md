<p align="center">
  <img src="tuxido.png" alt="Tuxido Logo" width="150">
</p>

<h1 align="center">Tuxido</h1>

<p align="center">
  <strong>Viste tus aplicaciones de terminal.</strong><br>
  <em>Validador de Framework AI-Nativo para Aplicaciones TUI de Textual</em>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12%20|%203.13-blue?logo=python&logoColor=white">
  <img alt="CI" src="https://img.shields.io/badge/CI-passing-brightgreen?logo=github&logoColor=white">
  <img alt="Plataformas" src="https://img.shields.io/badge/OS-Linux%20|%20macOS%20|%20Windows-241F31?logo=gnometerminal&logoColor=white">
  <a href="LICENSE">
    <img alt="Licencia" src="https://img.shields.io/badge/Licencia-MIT-green?logo=open-source-initiative&logoColor=white">
  </a>
  <br>
  <a href="README.md">
    <img alt="English" src="https://img.shields.io/badge/Lang-English-blue">
  </a>
</p>

---

## Acerca de

Tuxido ayuda a los desarrolladores a construir aplicaciones TUI de Textual confiables detectando errores antes de la ejecución y generando código desde mockups ASCII. Proporciona cuatro niveles de validación, capacidades de auto-corrección e integración perfecta con asistentes de IA a través de MCP.

---

## ¿Qué es Tuxido?

Tuxido es un validador y generador de código para aplicaciones TUI de **Textual**. Detecta errores antes de la ejecución y genera código funcional desde mockups ASCII.

### ¿Por qué usarlo?

| Problema | Solución de Tuxido |
|----------|---------------------|
| Errores de sintaxis en runtime | Validación L1 los detecta al instante |
| Imports inseguros (`os`, `subprocess`) | Análisis estático L2 los detecta |
| Problemas de estructura de widgets | Validación DOM L3 |
| Crashes en runtime | Testing en sandbox L4 |
| Escribir código repetitivo | Generar desde ASCII art |
| Corregir errores manualmente | Auto-corrección iterativa |

### Ejemplo: Validar

```python
# app.py - Tiene un import prohibido
import os  # ← Problema!
from textual.app import App
from textual.widgets import Static

class MyApp(App):
    def compose(self):
        yield Static("Hola")
```

```bash
$ tuxido check app.py

✗ app.py
  Status: fail

  E201 FORBIDDEN_IMPORT (L2)
    import os
    │
  ⚠ Import prohibido: 'os'
    Fix: Remueve el import os o usa alternativas de Textual
    LLM Action: Usa pathlib.Path para operaciones de archivo
```

### Ejemplo: Generar desde ASCII

```
╭────────────────────────────╮
│ Usuario: [_______________] │
│ Clave:   [_______________] │
│                            │
│    [Ingresar]  [Cancelar]  │
╰────────────────────────────╯
```

```bash
$ tuxido generate mockup.txt --output login.py
```

Genera:

```python
from textual.app import App, ComposeResult
from textual.widgets import Input, Button
from textual.containers import Vertical, Horizontal

class LoginApp(App):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="Usuario", id="username")
            yield Input(placeholder="Clave", password=True, id="password")
            with Horizontal():
                yield Button("Ingresar", variant="primary")
                yield Button("Cancelar")
```

### Ejemplo: Auto-Corregir

```bash
$ tuxido heal app.py --max-iterations=5

Analizando app.py...
Encontrados 3 problemas

Iteración 1:
  ✓ fix_unused_import: Removido 'os'
  ✓ fix_widget_id: Agregado id="username" al Input
  ✓ fix_missing_import: Agregado 'from textual.containers import Vertical'

Iteración 2:
  ✓ Validación exitosa

Aplicados 3 fixes en 2 iteraciones
```

---

## Instalar

### Ejecutar sin instalar (uvx)

```bash
uvx tuxido check app.py
uvx tuxido generate layout.txt --output app.py
```

### Instalar con uv

```bash
uv tool install tuxido

# Con soporte MCP
uv tool install "tuxido[mcp]"
```

### Instalar con pip

```bash
pip install tuxido

# Con soporte MCP
pip install tuxido[mcp]
```

---

## Uso en Terminal

### Validar

```bash
tuxido check app.py              # Rápido (L1+L2)
tuxido check app.py --depth=full # Completo (L1-L4)
tuxido check app.py --json       # Salida JSON
```

### Generar desde ASCII

```bash
tuxido generate layout.txt --output app.py
```

```
╭─────────────╮     →     class GeneratedApp(App):
│ [Buscar...] │             def compose(self):
│ [Enviar]    │                 yield Input(placeholder="Buscar...")
╰─────────────╯                 yield Button("Enviar")
```

### Auto-Corregir

```bash
tuxido heal app.py --max-iterations=5
```

### Otros Comandos

```bash
tuxido version          # Info de versión
tuxido info --verbose   # Widgets y APIs de Textual
tuxido fix app.py       # Corregir errores
```

---

## Servidor MCP

### Instalar MCP

**OpenCode** (`~/.config/opencode/opencode.json`):
```json
{
  "mcp": {
    "tuxido": {
      "enabled": true,
      "command": ["tuxido", "mcp", "--fastmcp"]
    }
  }
}
```

**Claude Code** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "tuxido": {
      "command": "tuxido",
      "args": ["mcp", "--fastmcp"]
    }
  }
}
```

**Cursor** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "tuxido": {
      "command": "tuxido",
      "args": ["mcp"]
    }
  }
}
```

### Herramientas MCP

| Herramienta | Descripción |
|-------------|-------------|
| `validate_tui` | Validar código TUI (L1-L4) |
| `get_framework_info` | Obtener widgets y APIs deprecadas |

### Ejemplo de Uso

```python
# En tu asistente AI
result = validate_tui(code="...", depth="fast")
# Retorna: status, errors, summary, metadata
```

---

## Skill de OpenCode

Tuxido incluye un skill con referencia de widgets Textual, patrones de código e integración Rich.

### Instalar Skill

```bash
# El skill se auto-instala con el paquete
# O manualmente:
python scripts/install_skill.py
```

**Ubicaciones del skill** (auto-descubierto):
- `~/.claude/skills/tuxido/SKILL.md`
- `~/.config/opencode/skills/tuxido/SKILL.md`

### Características del Skill

- **Referencia de 20+ Widgets** - Core, Data, Input, Layout con ejemplos
- **Integración Rich** - Texto estilizado, tablas, resaltado de sintaxis
- **Patrones de Código** - Form, Master-Detail, DataTable, Reactive
- **Guía CSS** - Layouts, docking, estilos reactivos
- **Context7 IDs** - Acceso dinámico a docs de Textual y Rich

### Usar el Skill

El skill se carga automáticamente al mencionar temas TUI/Textual:
```
"Crear un formulario de login con Textual"
"Generar un DataTable con ordenamiento"
"Agregar formato Rich a mi TUI"
```

---

## Niveles de Validación

| Nivel | Nombre | Verifica | Velocidad |
|-------|--------|----------|-----------|
| L1 | Sintaxis | Parsing AST | Instantáneo |
| L2 | Estático | Imports, async | Rápido |
| L3 | DOM | Árbol de widgets | Medio |
| L4 | Sandbox | Runtime | Lento |

## Códigos de Error

| Código | Solución |
|--------|----------|
| E101 | Corregir sintaxis Python |
| E201 | Eliminar `os`, `sys`, `subprocess` |
| E202 | Usar decorador `@work` |
| W201 | Agregar `from textual.app import App` |
| W202 | Eliminar import no usado |
| D301 | Agregar `id="nombre-widget"` |

---

## Referencia Rápida

```python
# Imports comunes
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, DataTable
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
```

---

## Enlaces

- **Docs**: https://textual.textualize.io
- **Context7**: `/websites/textual_textualize_io`
- **Issues**: https://github.com/hbuddenberg/tuxido/issues

---

## Licencia

MIT
