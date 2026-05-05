#!/usr/bin/env python3
"""
ECC Dashboard (Español) - Everything Claude Code GUI
Aplicación de escritorio multiplataforma con interfaz en español para gestionar componentes ECC.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import json
import subprocess
from typing import Dict, List, Optional

from scripts.lib.ecc_dashboard_runtime import build_terminal_launch, maximize_window

# ============================================================================
# CARGADORES DE DATOS - Carga datos del proyecto ECC
# ============================================================================

def get_project_path() -> str:
    """Obtiene la ruta del proyecto ECC; asume que el script se ejecuta desde el directorio del proyecto."""
    return os.path.dirname(os.path.abspath(__file__))


def load_agents(project_path: str) -> List[Dict]:
    """Carga los agentes desde AGENTS.md"""
    agents_file = os.path.join(project_path, "AGENTS.md")
    agents = []

    if os.path.exists(agents_file):
        with open(agents_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Analiza la tabla de agentes en AGENTS.md
        lines = content.split('\n')
        in_table = False
        for line in lines:
            if '| Agent | Purpose | When to Use |' in line:
                in_table = True
                continue
            if in_table and line.startswith('|'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4 and parts[1] and parts[1] != 'Agent':
                    agents.append({
                        'name': parts[1],
                        'purpose': parts[2],
                        'when_to_use': parts[3]
                    })

    # Agentes predeterminados si el archivo no existe
    if not agents:
        agents = [
            {'name': 'planner', 'purpose': 'Planificación de implementación', 'when_to_use': 'Funciones complejas, refactorización'},
            {'name': 'architect', 'purpose': 'Diseño del sistema y escalabilidad', 'when_to_use': 'Decisiones de arquitectura'},
            {'name': 'tdd-guide', 'purpose': 'Desarrollo guiado por pruebas', 'when_to_use': 'Nuevas funciones, corrección de errores'},
            {'name': 'code-reviewer', 'purpose': 'Calidad y mantenibilidad del código', 'when_to_use': 'Tras escribir o modificar código'},
            {'name': 'security-reviewer', 'purpose': 'Detección de vulnerabilidades', 'when_to_use': 'Antes de commits, código sensible'},
            {'name': 'build-error-resolver', 'purpose': 'Corregir errores de compilación/tipos', 'when_to_use': 'Cuando falla la compilación'},
            {'name': 'e2e-runner', 'purpose': 'Pruebas end-to-end con Playwright', 'when_to_use': 'Flujos de usuario críticos'},
            {'name': 'refactor-cleaner', 'purpose': 'Limpieza de código muerto', 'when_to_use': 'Mantenimiento de código'},
            {'name': 'doc-updater', 'purpose': 'Documentación y mapas de código', 'when_to_use': 'Actualizar documentación'},
            {'name': 'go-reviewer', 'purpose': 'Revisión de código Go', 'when_to_use': 'Proyectos Go'},
            {'name': 'python-reviewer', 'purpose': 'Revisión de código Python', 'when_to_use': 'Proyectos Python'},
            {'name': 'typescript-reviewer', 'purpose': 'Revisión de código TypeScript/JavaScript', 'when_to_use': 'Proyectos TypeScript'},
            {'name': 'rust-reviewer', 'purpose': 'Revisión de código Rust', 'when_to_use': 'Proyectos Rust'},
            {'name': 'java-reviewer', 'purpose': 'Revisión de código Java y Spring Boot', 'when_to_use': 'Proyectos Java'},
            {'name': 'kotlin-reviewer', 'purpose': 'Revisión de código Kotlin', 'when_to_use': 'Proyectos Kotlin'},
            {'name': 'cpp-reviewer', 'purpose': 'Revisión de código C/C++', 'when_to_use': 'Proyectos C/C++'},
            {'name': 'database-reviewer', 'purpose': 'Especialista en PostgreSQL/Supabase', 'when_to_use': 'Trabajo con bases de datos'},
            {'name': 'loop-operator', 'purpose': 'Ejecución autónoma en bucle', 'when_to_use': 'Ejecutar bucles de forma segura'},
            {'name': 'harness-optimizer', 'purpose': 'Ajuste de configuración del harness', 'when_to_use': 'Fiabilidad, coste, rendimiento'},
        ]

    return agents


def load_skills(project_path: str) -> List[Dict]:
    """Carga las habilidades desde el directorio skills"""
    skills_dir = os.path.join(project_path, "skills")
    skills = []

    if os.path.exists(skills_dir):
        for item in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, item)
            if os.path.isdir(skill_path):
                skill_file = os.path.join(skill_path, "SKILL.md")
                description = item.replace('-', ' ').title()

                if os.path.exists(skill_file):
                    try:
                        with open(skill_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.split('\n')
                            for line in lines:
                                if line.strip() and not line.startswith('#'):
                                    description = line.strip()[:100]
                                    break
                                if line.startswith('# '):
                                    description = line[2:].strip()[:100]
                                    break
                    except:
                        pass

                # Determinar categoría
                category = "General"
                item_lower = item.lower()
                if 'python' in item_lower or 'django' in item_lower:
                    category = "Python"
                elif 'golang' in item_lower or 'go-' in item_lower:
                    category = "Go"
                elif 'frontend' in item_lower or 'react' in item_lower:
                    category = "Frontend"
                elif 'backend' in item_lower or 'api' in item_lower:
                    category = "Backend"
                elif 'security' in item_lower:
                    category = "Security"
                elif 'testing' in item_lower or 'tdd' in item_lower:
                    category = "Testing"
                elif 'docker' in item_lower or 'deployment' in item_lower:
                    category = "DevOps"
                elif 'swift' in item_lower or 'ios' in item_lower:
                    category = "iOS"
                elif 'java' in item_lower or 'spring' in item_lower:
                    category = "Java"
                elif 'rust' in item_lower:
                    category = "Rust"

                skills.append({
                    'name': item,
                    'description': description,
                    'category': category,
                    'path': skill_path
                })

    # Valores predeterminados si el directorio no existe
    if not skills:
        skills = [
            {'name': 'tdd-workflow', 'description': 'Flujo de trabajo de desarrollo guiado por pruebas', 'category': 'Testing'},
            {'name': 'coding-standards', 'description': 'Convenciones base de codificación', 'category': 'General'},
            {'name': 'security-review', 'description': 'Lista de verificación y patrones de seguridad', 'category': 'Security'},
            {'name': 'frontend-patterns', 'description': 'Patrones React y Next.js', 'category': 'Frontend'},
            {'name': 'backend-patterns', 'description': 'Patrones de API y base de datos', 'category': 'Backend'},
            {'name': 'api-design', 'description': 'Patrones de diseño de API REST', 'category': 'Backend'},
            {'name': 'docker-patterns', 'description': 'Patrones Docker y contenedores', 'category': 'DevOps'},
            {'name': 'e2e-testing', 'description': 'Patrones de pruebas E2E con Playwright', 'category': 'Testing'},
            {'name': 'verification-loop', 'description': 'Verificación: compilar, probar, lint', 'category': 'General'},
            {'name': 'python-patterns', 'description': 'Expresiones idiomáticas y buenas prácticas en Python', 'category': 'Python'},
            {'name': 'golang-patterns', 'description': 'Expresiones idiomáticas y buenas prácticas en Go', 'category': 'Go'},
            {'name': 'django-patterns', 'description': 'Patrones y buenas prácticas en Django', 'category': 'Python'},
            {'name': 'springboot-patterns', 'description': 'Patrones Java Spring Boot', 'category': 'Java'},
            {'name': 'laravel-patterns', 'description': 'Patrones de arquitectura Laravel', 'category': 'PHP'},
        ]

    return skills


def load_commands(project_path: str) -> List[Dict]:
    """Carga los comandos desde el directorio commands"""
    commands_dir = os.path.join(project_path, "commands")
    commands = []

    if os.path.exists(commands_dir):
        for item in os.listdir(commands_dir):
            if item.endswith('.md'):
                cmd_name = item[:-3]
                description = ""

                try:
                    with open(os.path.join(commands_dir, item), 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        for line in lines:
                            if line.startswith('# '):
                                description = line[2:].strip()
                                break
                except:
                    pass

                commands.append({
                    'name': cmd_name,
                    'description': description or cmd_name.replace('-', ' ').title()
                })

    # Comandos predeterminados
    if not commands:
        commands = [
            {'name': 'plan', 'description': 'Crear plan de implementación'},
            {'name': 'tdd', 'description': 'Flujo de trabajo de desarrollo guiado por pruebas'},
            {'name': 'code-review', 'description': 'Revisar código por calidad y seguridad'},
            {'name': 'build-fix', 'description': 'Corregir errores de compilación y TypeScript'},
            {'name': 'e2e', 'description': 'Generar y ejecutar pruebas E2E'},
            {'name': 'refactor-clean', 'description': 'Eliminar código muerto'},
            {'name': 'verify', 'description': 'Ejecutar bucle de verificación'},
            {'name': 'eval', 'description': 'Ejecutar evaluación contra criterios'},
            {'name': 'security', 'description': 'Ejecutar revisión de seguridad completa'},
            {'name': 'test-coverage', 'description': 'Analizar cobertura de pruebas'},
            {'name': 'update-docs', 'description': 'Actualizar documentación'},
            {'name': 'setup-pm', 'description': 'Configurar gestor de paquetes'},
            {'name': 'go-review', 'description': 'Revisión de código Go'},
            {'name': 'go-test', 'description': 'Flujo de trabajo TDD en Go'},
            {'name': 'python-review', 'description': 'Revisión de código Python'},
        ]

    return commands


def load_rules(project_path: str) -> List[Dict]:
    """Carga las reglas desde el directorio rules"""
    rules_dir = os.path.join(project_path, "rules")
    rules = []

    if os.path.exists(rules_dir):
        for item in os.listdir(rules_dir):
            item_path = os.path.join(rules_dir, item)
            if os.path.isdir(item_path):
                # Reglas comunes
                if item == "common":
                    for file in os.listdir(item_path):
                        if file.endswith('.md'):
                            rules.append({
                                'name': file[:-3],
                                'language': 'Común',
                                'path': os.path.join(item_path, file)
                            })
                else:
                    # Reglas específicas del lenguaje
                    for file in os.listdir(item_path):
                        if file.endswith('.md'):
                            rules.append({
                                'name': file[:-3],
                                'language': item.title(),
                                'path': os.path.join(item_path, file)
                            })

    # Reglas predeterminadas
    if not rules:
        rules = [
            {'name': 'coding-style', 'language': 'Común', 'path': ''},
            {'name': 'git-workflow', 'language': 'Común', 'path': ''},
            {'name': 'testing', 'language': 'Común', 'path': ''},
            {'name': 'performance', 'language': 'Común', 'path': ''},
            {'name': 'patterns', 'language': 'Común', 'path': ''},
            {'name': 'security', 'language': 'Común', 'path': ''},
            {'name': 'typescript', 'language': 'TypeScript', 'path': ''},
            {'name': 'python', 'language': 'Python', 'path': ''},
            {'name': 'golang', 'language': 'Go', 'path': ''},
            {'name': 'swift', 'language': 'Swift', 'path': ''},
            {'name': 'php', 'language': 'PHP', 'path': ''},
        ]

    return rules


# ============================================================================
# APLICACIÓN PRINCIPAL
# ============================================================================

class ECCDashboardES(tk.Tk):
    """Panel Principal ECC - Interfaz en Español"""

    def __init__(self):
        super().__init__()

        self.project_path = get_project_path()
        self.title("Panel ECC - Everything Claude Code")

        maximize_window(self)

        try:
            self.icon_image = tk.PhotoImage(file='assets/images/ecc-logo.png')
            self.iconphoto(True, self.icon_image)
        except:
            pass

        self.minsize(800, 600)

        # Cargar datos
        self.agents = load_agents(self.project_path)
        self.skills = load_skills(self.project_path)
        self.commands = load_commands(self.project_path)
        self.rules = load_rules(self.project_path)

        # Configuración
        self.settings = {
            'project_path': self.project_path,
            'theme': 'light'
        }

        # Configurar UI
        self.setup_styles()
        self.create_widgets()

        # Centrar ventana
        self.center_window()

    def setup_styles(self):
        """Configura los estilos ttk para una apariencia moderna"""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 10))
        style.map('TNotebook.Tab', background=[('selected', '#ffffff')])

        style.configure('Treeview', font=('Arial', 10), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))

        style.configure('TButton', font=('Arial', 10), padding=5)

    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Contenedor principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Encabezado
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        try:
            self.logo_image = tk.PhotoImage(file='assets/images/ecc-logo.png')
            self.logo_image = self.logo_image.subsample(2, 2)
            ttk.Label(header_frame, image=self.logo_image).pack(side=tk.LEFT, padx=(0, 10))
        except:
            pass

        self.title_label = ttk.Label(header_frame, text="Panel ECC", font=('Open Sans', 18, 'bold'))
        self.title_label.pack(side=tk.LEFT)
        self.version_label = ttk.Label(header_frame, text="v1.10.0", font=('Open Sans', 10), foreground='gray')
        self.version_label.pack(side=tk.LEFT, padx=(10, 0))

        # Cuaderno de pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Crear pestañas
        self.create_agents_tab()
        self.create_skills_tab()
        self.create_commands_tab()
        self.create_rules_tab()
        self.create_settings_tab()

        # Barra de estado
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(
            status_frame,
            text=f"Listo | Agentes: {len(self.agents)} | Habilidades: {len(self.skills)} | Comandos: {len(self.commands)}",
            font=('Arial', 9), foreground='gray'
        )
        self.status_label.pack(side=tk.LEFT)

    # =========================================================================
    # PESTAÑA DE AGENTES
    # =========================================================================

    def create_agents_tab(self):
        """Crea la pestaña Agentes"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"Agentes ({len(self.agents)})")

        # Barra de búsqueda
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        self.agent_search = ttk.Entry(search_frame, width=30)
        self.agent_search.pack(side=tk.LEFT, padx=5)
        self.agent_search.bind('<KeyRelease>', self.filter_agents)

        ttk.Label(search_frame, text="Total:").pack(side=tk.LEFT, padx=(20, 0))
        self.agent_count_label = ttk.Label(search_frame, text=str(len(self.agents)))
        self.agent_count_label.pack(side=tk.LEFT)

        # Panel dividido: lista + detalles
        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Lista de agentes
        list_frame = ttk.Frame(paned)
        paned.add(list_frame, weight=2)

        columns = ('name', 'purpose')
        self.agent_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        self.agent_tree.heading('#0', text='#')
        self.agent_tree.heading('name', text='Nombre del agente')
        self.agent_tree.heading('purpose', text='Propósito')
        self.agent_tree.column('#0', width=40)
        self.agent_tree.column('name', width=180)
        self.agent_tree.column('purpose', width=250)

        self.agent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Barra de desplazamiento
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.agent_tree.yview)
        self.agent_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Panel de detalles
        details_frame = ttk.Frame(paned)
        paned.add(details_frame, weight=1)

        ttk.Label(details_frame, text="Detalles", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=5)

        self.agent_details = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, height=15)
        self.agent_details.pack(fill=tk.BOTH, expand=True)

        # Vincular selección
        self.agent_tree.bind('<<TreeviewSelect>>', self.on_agent_select)

        # Poblar lista
        self.populate_agents(self.agents)

    def populate_agents(self, agents: List[Dict]):
        """Pobla la lista de agentes"""
        for item in self.agent_tree.get_children():
            self.agent_tree.delete(item)

        for i, agent in enumerate(agents, 1):
            self.agent_tree.insert('', tk.END, text=str(i), values=(agent['name'], agent['purpose']))

    def filter_agents(self, event=None):
        """Filtra agentes según la búsqueda"""
        query = self.agent_search.get().lower()

        if not query:
            filtered = self.agents
        else:
            filtered = [a for a in self.agents
                        if query in a['name'].lower() or query in a['purpose'].lower()]

        self.populate_agents(filtered)
        self.agent_count_label.config(text=str(len(filtered)))

    def on_agent_select(self, event):
        """Maneja la selección de un agente"""
        selection = self.agent_tree.selection()
        if not selection:
            return

        item = self.agent_tree.item(selection[0])
        agent_name = item['values'][0]

        agent = next((a for a in self.agents if a['name'] == agent_name), None)
        if agent:
            details = f"""Agente: {agent['name']}

Propósito: {agent['purpose']}

Cuándo usar: {agent['when_to_use']}

---
Uso en Claude Code:
Use el comando /{agent['name']} o invóquelo mediante delegación de agentes."""
            self.agent_details.delete('1.0', tk.END)
            self.agent_details.insert('1.0', details)

    # =========================================================================
    # PESTAÑA DE HABILIDADES
    # =========================================================================

    def create_skills_tab(self):
        """Crea la pestaña Habilidades"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"Habilidades ({len(self.skills)})")

        # Búsqueda y filtros
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(filter_frame, text="Buscar:").pack(side=tk.LEFT)
        self.skill_search = ttk.Entry(filter_frame, width=25)
        self.skill_search.pack(side=tk.LEFT, padx=5)
        self.skill_search.bind('<KeyRelease>', self.filter_skills)

        ttk.Label(filter_frame, text="Categoría:").pack(side=tk.LEFT, padx=(20, 0))
        self.skill_category = ttk.Combobox(filter_frame, values=['Todas'] + self.get_categories(), width=15)
        self.skill_category.set('Todas')
        self.skill_category.pack(side=tk.LEFT, padx=5)
        self.skill_category.bind('<<ComboboxSelected>>', self.filter_skills)

        ttk.Label(filter_frame, text="Total:").pack(side=tk.LEFT, padx=(20, 0))
        self.skill_count_label = ttk.Label(filter_frame, text=str(len(self.skills)))
        self.skill_count_label.pack(side=tk.LEFT)

        # Panel dividido
        paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Lista de habilidades
        list_frame = ttk.Frame(paned)
        paned.add(list_frame, weight=1)

        columns = ('name', 'category', 'description')
        self.skill_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        self.skill_tree.heading('#0', text='#')
        self.skill_tree.heading('name', text='Nombre de habilidad')
        self.skill_tree.heading('category', text='Categoría')
        self.skill_tree.heading('description', text='Descripción')

        self.skill_tree.column('#0', width=40)
        self.skill_tree.column('name', width=180)
        self.skill_tree.column('category', width=100)
        self.skill_tree.column('description', width=300)

        self.skill_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.skill_tree.yview)
        self.skill_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Detalles
        details_frame = ttk.Frame(paned)
        paned.add(details_frame, weight=1)

        ttk.Label(details_frame, text="Descripción", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=5)

        self.skill_details = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, height=15)
        self.skill_details.pack(fill=tk.BOTH, expand=True)

        self.skill_tree.bind('<<TreeviewSelect>>', self.on_skill_select)

        self.populate_skills(self.skills)

    def get_categories(self) -> List[str]:
        """Obtiene categorías únicas de las habilidades"""
        categories = set(s['category'] for s in self.skills)
        return sorted(categories)

    def populate_skills(self, skills: List[Dict]):
        """Pobla la lista de habilidades"""
        for item in self.skill_tree.get_children():
            self.skill_tree.delete(item)

        for i, skill in enumerate(skills, 1):
            self.skill_tree.insert('', tk.END, text=str(i),
                                   values=(skill['name'], skill['category'], skill['description']))

    def filter_skills(self, event=None):
        """Filtra habilidades según búsqueda y categoría"""
        search = self.skill_search.get().lower()
        category = self.skill_category.get()

        filtered = self.skills

        if category != 'Todas':
            filtered = [s for s in filtered if s['category'] == category]

        if search:
            filtered = [s for s in filtered
                        if search in s['name'].lower() or search in s['description'].lower()]

        self.populate_skills(filtered)
        self.skill_count_label.config(text=str(len(filtered)))

    def on_skill_select(self, event):
        """Maneja la selección de una habilidad"""
        selection = self.skill_tree.selection()
        if not selection:
            return

        item = self.skill_tree.item(selection[0])
        skill_name = item['values'][0]

        skill = next((s for s in self.skills if s['name'] == skill_name), None)
        if skill:
            details = f"""Habilidad: {skill['name']}

Categoría: {skill['category']}

Descripción: {skill['description']}

Ruta: {skill['path']}

---
Uso: Esta habilidad se activa automáticamente al trabajar con tecnologías relacionadas."""
            self.skill_details.delete('1.0', tk.END)
            self.skill_details.insert('1.0', details)

    # =========================================================================
    # PESTAÑA DE COMANDOS
    # =========================================================================

    def create_commands_tab(self):
        """Crea la pestaña Comandos"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"Comandos ({len(self.commands)})")

        # Información
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(info_frame, text="Comandos de barra diagonal para Claude Code:",
                  font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(info_frame, text="Usa estos comandos en Claude Code escribiendo /nombre_comando",
                  foreground='gray').pack(anchor=tk.W)

        # Lista de comandos
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        columns = ('name', 'description')
        self.command_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        self.command_tree.heading('#0', text='#')
        self.command_tree.heading('name', text='Comando')
        self.command_tree.heading('description', text='Descripción')

        self.command_tree.column('#0', width=40)
        self.command_tree.column('name', width=150)
        self.command_tree.column('description', width=400)

        self.command_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.command_tree.yview)
        self.command_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Poblar lista
        for i, cmd in enumerate(self.commands, 1):
            self.command_tree.insert('', tk.END, text=str(i),
                                     values=('/' + cmd['name'], cmd['description']))

    # =========================================================================
    # PESTAÑA DE REGLAS
    # =========================================================================

    def create_rules_tab(self):
        """Crea la pestaña Reglas"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=f"Reglas ({len(self.rules)})")

        # Información
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(info_frame, text="Reglas de codificación por lenguaje:",
                  font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(info_frame, text="Estas reglas se aplican automáticamente en Claude Code",
                  foreground='gray').pack(anchor=tk.W)

        # Filtro
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="Lenguaje:").pack(side=tk.LEFT)
        self.rules_language = ttk.Combobox(filter_frame,
                                           values=['Todos'] + self.get_rule_languages(),
                                           width=15)
        self.rules_language.set('Todos')
        self.rules_language.pack(side=tk.LEFT, padx=5)
        self.rules_language.bind('<<ComboboxSelected>>', self.filter_rules)

        # Lista de reglas
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        columns = ('name', 'language')
        self.rules_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        self.rules_tree.heading('#0', text='#')
        self.rules_tree.heading('name', text='Nombre de regla')
        self.rules_tree.heading('language', text='Lenguaje')

        self.rules_tree.column('#0', width=40)
        self.rules_tree.column('name', width=250)
        self.rules_tree.column('language', width=100)

        self.rules_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.rules_tree.yview)
        self.rules_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.populate_rules(self.rules)

    def get_rule_languages(self) -> List[str]:
        """Obtiene lenguajes únicos de las reglas"""
        languages = set(r['language'] for r in self.rules)
        return sorted(languages)

    def populate_rules(self, rules: List[Dict]):
        """Pobla la lista de reglas"""
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)

        for i, rule in enumerate(rules, 1):
            self.rules_tree.insert('', tk.END, text=str(i),
                                   values=(rule['name'], rule['language']))

    def filter_rules(self, event=None):
        """Filtra reglas por lenguaje"""
        language = self.rules_language.get()

        if language == 'Todos':
            filtered = self.rules
        else:
            filtered = [r for r in self.rules if r['language'] == language]

        self.populate_rules(filtered)

    # =========================================================================
    # PESTAÑA DE CONFIGURACIÓN
    # =========================================================================

    def create_settings_tab(self):
        """Crea la pestaña Configuración"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Configuración")

        # Ruta del proyecto
        path_frame = ttk.LabelFrame(frame, text="Ruta del proyecto", padding=10)
        path_frame.pack(fill=tk.X, padx=10, pady=10)

        self.path_entry = ttk.Entry(path_frame, width=60)
        self.path_entry.insert(0, self.project_path)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(path_frame, text="Explorar...", command=self.browse_path).pack(side=tk.LEFT, padx=5)

        # Tema
        theme_frame = ttk.LabelFrame(frame, text="Apariencia", padding=10)
        theme_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(theme_frame, text="Tema:").pack(anchor=tk.W)
        self.theme_var = tk.StringVar(value='light')
        light_rb = ttk.Radiobutton(theme_frame, text="Claro", variable=self.theme_var,
                                   value='light', command=self.apply_theme)
        light_rb.pack(anchor=tk.W)
        dark_rb = ttk.Radiobutton(theme_frame, text="Oscuro", variable=self.theme_var,
                                  value='dark', command=self.apply_theme)
        dark_rb.pack(anchor=tk.W)

        # Fuente
        font_frame = ttk.LabelFrame(frame, text="Fuente", padding=10)
        font_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(font_frame, text="Familia tipográfica:").pack(anchor=tk.W)
        self.font_var = tk.StringVar(value='Open Sans')

        fonts = ['Open Sans', 'Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana', 'Georgia', 'Tahoma', 'Trebuchet MS']
        self.font_combo = ttk.Combobox(font_frame, textvariable=self.font_var, values=fonts, state='readonly')
        self.font_combo.pack(anchor=tk.W, fill=tk.X, pady=(5, 0))
        self.font_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_theme())

        ttk.Label(font_frame, text="Tamaño de fuente:").pack(anchor=tk.W, pady=(10, 0))
        self.size_var = tk.StringVar(value='10')
        sizes = ['8', '9', '10', '11', '12', '14', '16', '18', '20']
        self.size_combo = ttk.Combobox(font_frame, textvariable=self.size_var, values=sizes, state='readonly', width=10)
        self.size_combo.pack(anchor=tk.W, pady=(5, 0))
        self.size_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_theme())

        # Acciones rápidas
        actions_frame = ttk.LabelFrame(frame, text="Acciones rápidas", padding=10)
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Button(actions_frame, text="Abrir proyecto en terminal",
                   command=self.open_terminal).pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="Abrir README",
                   command=self.open_readme).pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="Abrir AGENTS.md",
                   command=self.open_agents).pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="Actualizar datos",
                   command=self.refresh_data).pack(fill=tk.X, pady=2)

        # Acerca de
        about_frame = ttk.LabelFrame(frame, text="Acerca de", padding=10)
        about_frame.pack(fill=tk.X, padx=10, pady=10)

        about_text = """Panel ECC v1.0.0
Everything Claude Code GUI (Interfaz en Español)

Aplicación de escritorio multiplataforma para
gestionar y explorar componentes ECC.

Versión: 1.10.0
Proyecto: github.com/affaan-m/everything-claude-code"""

        ttk.Label(about_frame, text=about_text, justify=tk.LEFT).pack(anchor=tk.W)

    def browse_path(self):
        """Explorar ruta del proyecto"""
        from tkinter import filedialog
        path = filedialog.askdirectory(initialdir=self.project_path)
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def open_terminal(self):
        """Abre la terminal en la ruta del proyecto"""
        path = self.path_entry.get()
        argv, kwargs = build_terminal_launch(path)
        subprocess.Popen(argv, **kwargs)

    def open_readme(self):
        """Abre el README en el visor predeterminado"""
        import subprocess
        path = os.path.join(self.path_entry.get(), 'README.md')
        if os.path.exists(path):
            subprocess.Popen(['xdg-open' if os.name != 'nt' else 'start', path])
        else:
            messagebox.showerror("Error", "README.md no encontrado")

    def open_agents(self):
        """Abre AGENTS.md"""
        import subprocess
        path = os.path.join(self.path_entry.get(), 'AGENTS.md')
        if os.path.exists(path):
            subprocess.Popen(['xdg-open' if os.name != 'nt' else 'start', path])
        else:
            messagebox.showerror("Error", "AGENTS.md no encontrado")

    def refresh_data(self):
        """Actualiza todos los datos"""
        self.project_path = self.path_entry.get()
        self.agents = load_agents(self.project_path)
        self.skills = load_skills(self.project_path)
        self.commands = load_commands(self.project_path)
        self.rules = load_rules(self.project_path)

        # Actualizar pestañas
        self.notebook.tab(0, text=f"Agentes ({len(self.agents)})")
        self.notebook.tab(1, text=f"Habilidades ({len(self.skills)})")
        self.notebook.tab(2, text=f"Comandos ({len(self.commands)})")
        self.notebook.tab(3, text=f"Reglas ({len(self.rules)})")

        # Re-poblar
        self.populate_agents(self.agents)
        self.populate_skills(self.skills)

        # Actualizar estado
        self.status_label.config(
            text=f"Listo | Agentes: {len(self.agents)} | Habilidades: {len(self.skills)} | Comandos: {len(self.commands)}"
        )

        messagebox.showinfo("Éxito", "¡Datos actualizados correctamente!")

    def apply_theme(self):
        theme = self.theme_var.get()
        font_family = self.font_var.get()
        font_size = int(self.size_var.get())
        font_tuple = (font_family, font_size)

        if theme == 'dark':
            bg_color = '#2b2b2b'
            fg_color = '#ffffff'
            entry_bg = '#3c3c3c'
            frame_bg = '#2b2b2b'
            select_bg = '#0f5a9e'
        else:
            bg_color = '#f0f0f0'
            fg_color = '#000000'
            entry_bg = '#ffffff'
            frame_bg = '#f0f0f0'
            select_bg = '#e0e0e0'

        self.configure(background=bg_color)

        style = ttk.Style()
        style.configure('.', background=bg_color, foreground=fg_color, font=font_tuple)
        style.configure('TFrame', background=bg_color, font=font_tuple)
        style.configure('TLabel', background=bg_color, foreground=fg_color, font=font_tuple)
        style.configure('TNotebook', background=bg_color, font=font_tuple)
        style.configure('TNotebook.Tab', background=frame_bg, foreground=fg_color, font=font_tuple)
        style.map('TNotebook.Tab', background=[('selected', select_bg)])
        style.configure('Treeview', background=entry_bg, foreground=fg_color, fieldbackground=entry_bg, font=font_tuple)
        style.configure('Treeview.Heading', background=frame_bg, foreground=fg_color, font=font_tuple)
        style.configure('TEntry', fieldbackground=entry_bg, foreground=fg_color, font=font_tuple)
        style.configure('TButton', background=frame_bg, foreground=fg_color, font=font_tuple)

        self.title_label.configure(font=(font_family, 18, 'bold'))
        self.version_label.configure(font=(font_family, 10))

        def update_widget_colors(widget):
            try:
                widget.configure(background=bg_color)
            except:
                pass
            for child in widget.winfo_children():
                try:
                    child.configure(background=bg_color)
                except:
                    pass
                try:
                    update_widget_colors(child)
                except:
                    pass

        try:
            update_widget_colors(self)
        except:
            pass

        self.update()


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

def main():
    """Punto de entrada principal"""
    app = ECCDashboardES()
    app.mainloop()


if __name__ == "__main__":
    main()
