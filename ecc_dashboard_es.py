#!/usr/bin/env python3
"""
Panel de Control ECC - Everything Claude Code (Versión en Español)
Aplicación de escritorio multiplataforma con Tkinter para gestionar componentes ECC
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import json
import subprocess
from typing import Dict, List, Optional

from scripts.lib.ecc_dashboard_runtime import build_terminal_launch, maximize_window

# ============================================================================
# TRADUCCIONES — Textos de la interfaz en castellano
# ============================================================================

TRADUCCIONES = {
    # Agentes
    'planner':              ('Planificación de implementación',      'Funcionalidades complejas, refactorización'),
    'architect':            ('Diseño de sistemas y escalabilidad',   'Decisiones de arquitectura'),
    'tdd-guide':            ('Desarrollo guiado por pruebas',        'Nuevas funcionalidades, corrección de bugs'),
    'code-reviewer':        ('Calidad y mantenibilidad del código',  'Tras escribir o modificar código'),
    'security-reviewer':    ('Detección de vulnerabilidades',        'Antes de commits, código sensible'),
    'build-error-resolver': ('Corrección de errores de compilación', 'Cuando falla el build'),
    'e2e-runner':           ('Pruebas E2E con Playwright',           'Flujos críticos de usuario'),
    'refactor-cleaner':     ('Limpieza de código muerto',            'Mantenimiento del código'),
    'doc-updater':          ('Documentación y codemaps',             'Actualización de docs'),
    'go-reviewer':          ('Revisión de código Go',                'Proyectos Go'),
    'python-reviewer':      ('Revisión de código Python',            'Proyectos Python'),
    'typescript-reviewer':  ('Revisión de código TypeScript/JS',     'Proyectos TypeScript'),
    'rust-reviewer':        ('Revisión de código Rust',              'Proyectos Rust'),
    'java-reviewer':        ('Revisión de Java y Spring Boot',       'Proyectos Java'),
    'kotlin-reviewer':      ('Revisión de código Kotlin',            'Proyectos Kotlin'),
    'cpp-reviewer':         ('Revisión de código C/C++',             'Proyectos C/C++'),
    'database-reviewer':    ('Especialista PostgreSQL/Supabase',     'Trabajo con bases de datos'),
    'loop-operator':        ('Ejecución de bucles autónomos',        'Ejecutar bucles de forma segura'),
    'harness-optimizer':    ('Ajuste de configuración del harness',  'Fiabilidad, coste, rendimiento'),
}

CATEGORIAS_ES = {
    'General':   'General',
    'Python':    'Python',
    'Go':        'Go',
    'Frontend':  'Frontend',
    'Backend':   'Backend',
    'Security':  'Seguridad',
    'Testing':   'Pruebas',
    'DevOps':    'DevOps',
    'iOS':       'iOS',
    'Java':      'Java',
    'Rust':      'Rust',
}


# ============================================================================
# CARGADORES DE DATOS
# ============================================================================

def obtener_ruta_proyecto() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def cargar_agentes(ruta_proyecto: str) -> List[Dict]:
    archivo_agentes = os.path.join(ruta_proyecto, "AGENTS.md")
    agentes = []

    if os.path.exists(archivo_agentes):
        with open(archivo_agentes, 'r', encoding='utf-8') as f:
            contenido = f.read()

        lineas = contenido.split('\n')
        en_tabla = False
        for linea in lineas:
            if '| Agent | Purpose | When to Use |' in linea:
                en_tabla = True
                continue
            if en_tabla and linea.startswith('|'):
                partes = [p.strip() for p in linea.split('|')]
                if len(partes) >= 4 and partes[1] and partes[1] != 'Agent':
                    nombre = partes[1]
                    proposito_en = partes[2]
                    cuando_en = partes[3]
                    proposito_es, cuando_es = TRADUCCIONES.get(
                        nombre, (proposito_en, cuando_en)
                    )
                    agentes.append({
                        'nombre': nombre,
                        'proposito': proposito_es,
                        'cuando_usar': cuando_es,
                    })

    if not agentes:
        for nombre, (proposito, cuando) in TRADUCCIONES.items():
            agentes.append({'nombre': nombre, 'proposito': proposito, 'cuando_usar': cuando})

    return agentes


def cargar_skills(ruta_proyecto: str) -> List[Dict]:
    directorio_skills = os.path.join(ruta_proyecto, "skills")
    skills = []

    if os.path.exists(directorio_skills):
        for elemento in os.listdir(directorio_skills):
            ruta_skill = os.path.join(directorio_skills, elemento)
            if os.path.isdir(ruta_skill):
                archivo_skill = os.path.join(ruta_skill, "SKILL.md")
                descripcion = elemento.replace('-', ' ').title()

                if os.path.exists(archivo_skill):
                    try:
                        with open(archivo_skill, 'r', encoding='utf-8') as f:
                            contenido = f.read()
                            lineas = contenido.split('\n')
                            for linea in lineas:
                                if linea.strip() and not linea.startswith('#'):
                                    descripcion = linea.strip()[:100]
                                    break
                                if linea.startswith('# '):
                                    descripcion = linea[2:].strip()[:100]
                                    break
                    except Exception:
                        pass

                # Determinar categoría
                categoria = "General"
                elem_lower = elemento.lower()
                if 'python' in elem_lower or 'django' in elem_lower:
                    categoria = "Python"
                elif 'golang' in elem_lower or 'go-' in elem_lower:
                    categoria = "Go"
                elif 'frontend' in elem_lower or 'react' in elem_lower:
                    categoria = "Frontend"
                elif 'backend' in elem_lower or 'api' in elem_lower:
                    categoria = "Backend"
                elif 'security' in elem_lower:
                    categoria = "Seguridad"
                elif 'testing' in elem_lower or 'tdd' in elem_lower:
                    categoria = "Pruebas"
                elif 'docker' in elem_lower or 'deployment' in elem_lower:
                    categoria = "DevOps"
                elif 'swift' in elem_lower or 'ios' in elem_lower:
                    categoria = "iOS"
                elif 'java' in elem_lower or 'spring' in elem_lower:
                    categoria = "Java"
                elif 'rust' in elem_lower:
                    categoria = "Rust"

                skills.append({
                    'nombre': elemento,
                    'descripcion': descripcion,
                    'categoria': categoria,
                    'ruta': ruta_skill,
                })

    if not skills:
        skills = [
            {'nombre': 'tdd-workflow',       'descripcion': 'Flujo de desarrollo guiado por pruebas', 'categoria': 'Pruebas',   'ruta': ''},
            {'nombre': 'coding-standards',   'descripcion': 'Convenciones de codificación base',      'categoria': 'General',   'ruta': ''},
            {'nombre': 'security-review',    'descripcion': 'Lista de verificación de seguridad',     'categoria': 'Seguridad', 'ruta': ''},
            {'nombre': 'frontend-patterns',  'descripcion': 'Patrones React y Next.js',               'categoria': 'Frontend',  'ruta': ''},
            {'nombre': 'backend-patterns',   'descripcion': 'Patrones de API y base de datos',        'categoria': 'Backend',   'ruta': ''},
            {'nombre': 'api-design',         'descripcion': 'Patrones de diseño REST API',            'categoria': 'Backend',   'ruta': ''},
            {'nombre': 'e2e-testing',        'descripcion': 'Patrones de pruebas E2E con Playwright',  'categoria': 'Pruebas',   'ruta': ''},
            {'nombre': 'verification-loop',  'descripcion': 'Verificación de build, tests y lint',    'categoria': 'General',   'ruta': ''},
            {'nombre': 'python-patterns',    'descripcion': 'Patrones e idiomas de Python',           'categoria': 'Python',    'ruta': ''},
            {'nombre': 'golang-patterns',    'descripcion': 'Patrones e idiomas de Go',               'categoria': 'Go',        'ruta': ''},
        ]

    return skills


def cargar_comandos(ruta_proyecto: str) -> List[Dict]:
    directorio_cmds = os.path.join(ruta_proyecto, "commands")
    comandos = []

    if os.path.exists(directorio_cmds):
        for elemento in os.listdir(directorio_cmds):
            if elemento.endswith('.md'):
                nombre_cmd = elemento[:-3]
                descripcion = ""

                try:
                    with open(os.path.join(directorio_cmds, elemento), 'r', encoding='utf-8') as f:
                        contenido = f.read()
                        for linea in contenido.split('\n'):
                            if linea.startswith('# '):
                                descripcion = linea[2:].strip()
                                break
                except Exception:
                    pass

                comandos.append({
                    'nombre': nombre_cmd,
                    'descripcion': descripcion or nombre_cmd.replace('-', ' ').title(),
                })

    if not comandos:
        comandos = [
            {'nombre': 'plan',          'descripcion': 'Crear plan de implementación'},
            {'nombre': 'tdd',           'descripcion': 'Flujo de desarrollo guiado por pruebas'},
            {'nombre': 'code-review',   'descripcion': 'Revisar calidad y seguridad del código'},
            {'nombre': 'build-fix',     'descripcion': 'Corregir errores de compilación y TypeScript'},
            {'nombre': 'e2e',           'descripcion': 'Generar y ejecutar pruebas E2E'},
            {'nombre': 'refactor-clean','descripcion': 'Eliminar código muerto'},
            {'nombre': 'verify',        'descripcion': 'Ejecutar bucle de verificación'},
            {'nombre': 'security',      'descripcion': 'Revisión de seguridad completa'},
            {'nombre': 'update-docs',   'descripcion': 'Actualizar documentación'},
        ]

    return comandos


def cargar_reglas(ruta_proyecto: str) -> List[Dict]:
    directorio_reglas = os.path.join(ruta_proyecto, "rules")
    reglas = []

    if os.path.exists(directorio_reglas):
        for elemento in os.listdir(directorio_reglas):
            ruta_elemento = os.path.join(directorio_reglas, elemento)
            if os.path.isdir(ruta_elemento):
                lenguaje = 'Común' if elemento == 'common' else elemento.title()
                for archivo in os.listdir(ruta_elemento):
                    if archivo.endswith('.md'):
                        reglas.append({
                            'nombre': archivo[:-3],
                            'lenguaje': lenguaje,
                            'ruta': os.path.join(ruta_elemento, archivo),
                        })

    if not reglas:
        reglas = [
            {'nombre': 'coding-style',  'lenguaje': 'Común',      'ruta': ''},
            {'nombre': 'git-workflow',  'lenguaje': 'Común',      'ruta': ''},
            {'nombre': 'testing',       'lenguaje': 'Común',      'ruta': ''},
            {'nombre': 'security',      'lenguaje': 'Común',      'ruta': ''},
            {'nombre': 'typescript',    'lenguaje': 'TypeScript',  'ruta': ''},
            {'nombre': 'python',        'lenguaje': 'Python',      'ruta': ''},
            {'nombre': 'golang',        'lenguaje': 'Go',          'ruta': ''},
        ]

    return reglas


# ============================================================================
# APLICACIÓN PRINCIPAL
# ============================================================================

class PanelECC(tk.Tk):
    """Panel de Control ECC en Español"""

    def __init__(self):
        super().__init__()

        self.ruta_proyecto = obtener_ruta_proyecto()
        self.title("Panel ECC — Everything Claude Code")

        maximize_window(self)

        try:
            self.icono = tk.PhotoImage(file='assets/images/ecc-logo.png')
            self.iconphoto(True, self.icono)
        except Exception:
            pass

        self.minsize(800, 600)

        # Cargar datos
        self.agentes  = cargar_agentes(self.ruta_proyecto)
        self.skills   = cargar_skills(self.ruta_proyecto)
        self.comandos = cargar_comandos(self.ruta_proyecto)
        self.reglas   = cargar_reglas(self.ruta_proyecto)

        self._configurar_estilos()
        self._crear_widgets()
        self._centrar_ventana()

    # ------------------------------------------------------------------
    # Estilos
    # ------------------------------------------------------------------

    def _configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure('TNotebook', background='#f0f0f0')
        estilo.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 10))
        estilo.map('TNotebook.Tab', background=[('selected', '#ffffff')])
        estilo.configure('Treeview', font=('Arial', 10), rowheight=25)
        estilo.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        estilo.configure('TButton', font=('Arial', 10), padding=5)

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho  = self.winfo_width()
        alto   = self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto  // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    # ------------------------------------------------------------------
    # Widgets raíz
    # ------------------------------------------------------------------

    def _crear_widgets(self):
        marco_principal = ttk.Frame(self)
        marco_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Cabecera
        marco_cabecera = ttk.Frame(marco_principal)
        marco_cabecera.pack(fill=tk.X, pady=(0, 10))

        try:
            self.logo = tk.PhotoImage(file='assets/images/ecc-logo.png').subsample(2, 2)
            ttk.Label(marco_cabecera, image=self.logo).pack(side=tk.LEFT, padx=(0, 10))
        except Exception:
            pass

        self.etiqueta_titulo = ttk.Label(
            marco_cabecera, text="Panel ECC", font=('Arial', 18, 'bold')
        )
        self.etiqueta_titulo.pack(side=tk.LEFT)

        self.etiqueta_version = ttk.Label(
            marco_cabecera, text="v2.0.0-rc.1", font=('Arial', 10), foreground='gray'
        )
        self.etiqueta_version.pack(side=tk.LEFT, padx=(10, 0))

        # Pestañas
        self.pestanas = ttk.Notebook(marco_principal)
        self.pestanas.pack(fill=tk.BOTH, expand=True)

        self._crear_pestana_agentes()
        self._crear_pestana_skills()
        self._crear_pestana_comandos()
        self._crear_pestana_reglas()
        self._crear_pestana_ajustes()

        # Barra de estado
        marco_estado = ttk.Frame(marco_principal)
        marco_estado.pack(fill=tk.X, pady=(10, 0))

        self.etiqueta_estado = ttk.Label(
            marco_estado,
            text=self._texto_estado(),
            font=('Arial', 9),
            foreground='gray',
        )
        self.etiqueta_estado.pack(side=tk.LEFT)

    def _texto_estado(self) -> str:
        return (
            f"Listo  |  Agentes: {len(self.agentes)}"
            f"  |  Skills: {len(self.skills)}"
            f"  |  Comandos: {len(self.comandos)}"
            f"  |  Reglas: {len(self.reglas)}"
        )

    # ------------------------------------------------------------------
    # Pestaña AGENTES
    # ------------------------------------------------------------------

    def _crear_pestana_agentes(self):
        marco = ttk.Frame(self.pestanas)
        self.pestanas.add(marco, text=f"Agentes ({len(self.agentes)})")

        # Búsqueda
        marco_busqueda = ttk.Frame(marco)
        marco_busqueda.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(marco_busqueda, text="Buscar:").pack(side=tk.LEFT)
        self.busq_agente = ttk.Entry(marco_busqueda, width=30)
        self.busq_agente.pack(side=tk.LEFT, padx=5)
        self.busq_agente.bind('<KeyRelease>', self._filtrar_agentes)

        ttk.Label(marco_busqueda, text="Total:").pack(side=tk.LEFT, padx=(20, 0))
        self.etiqueta_total_agentes = ttk.Label(marco_busqueda, text=str(len(self.agentes)))
        self.etiqueta_total_agentes.pack(side=tk.LEFT)

        # Panel dividido
        panel = ttk.PanedWindow(marco, orient=tk.HORIZONTAL)
        panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Lista
        marco_lista = ttk.Frame(panel)
        panel.add(marco_lista, weight=2)

        columnas = ('nombre', 'proposito')
        self.tabla_agentes = ttk.Treeview(marco_lista, columns=columnas, show='tree headings')
        self.tabla_agentes.heading('#0',       text='#')
        self.tabla_agentes.heading('nombre',   text='Agente')
        self.tabla_agentes.heading('proposito',text='Propósito')
        self.tabla_agentes.column('#0',        width=40)
        self.tabla_agentes.column('nombre',    width=190)
        self.tabla_agentes.column('proposito', width=260)
        self.tabla_agentes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        barra = ttk.Scrollbar(marco_lista, orient=tk.VERTICAL, command=self.tabla_agentes.yview)
        self.tabla_agentes.configure(yscrollcommand=barra.set)
        barra.pack(side=tk.RIGHT, fill=tk.Y)

        # Panel de detalles
        marco_detalle = ttk.Frame(panel)
        panel.add(marco_detalle, weight=1)

        ttk.Label(marco_detalle, text="Detalles", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=5)
        self.detalle_agente = scrolledtext.ScrolledText(marco_detalle, wrap=tk.WORD, height=15)
        self.detalle_agente.pack(fill=tk.BOTH, expand=True)

        self.tabla_agentes.bind('<<TreeviewSelect>>', self._al_seleccionar_agente)
        self._poblar_agentes(self.agentes)

    def _poblar_agentes(self, agentes: List[Dict]):
        for fila in self.tabla_agentes.get_children():
            self.tabla_agentes.delete(fila)
        for i, ag in enumerate(agentes, 1):
            self.tabla_agentes.insert('', tk.END, text=str(i), values=(ag['nombre'], ag['proposito']))

    def _filtrar_agentes(self, event=None):
        consulta = self.busq_agente.get().lower()
        if not consulta:
            filtrados = self.agentes
        else:
            filtrados = [
                a for a in self.agentes
                if consulta in a['nombre'].lower() or consulta in a['proposito'].lower()
            ]
        self._poblar_agentes(filtrados)
        self.etiqueta_total_agentes.config(text=str(len(filtrados)))

    def _al_seleccionar_agente(self, event=None):
        seleccion = self.tabla_agentes.selection()
        if not seleccion:
            return
        nombre = self.tabla_agentes.item(seleccion[0])['values'][0]
        agente = next((a for a in self.agentes if a['nombre'] == nombre), None)
        if agente:
            texto = (
                f"Agente:      {agente['nombre']}\n\n"
                f"Propósito:   {agente['proposito']}\n\n"
                f"Cuándo usar: {agente['cuando_usar']}\n\n"
                f"---\n"
                f"Uso en Claude Code:\n"
                f"  /{agente['nombre']}\n"
                f"  o mediante delegación de agentes."
            )
            self.detalle_agente.delete('1.0', tk.END)
            self.detalle_agente.insert('1.0', texto)

    # ------------------------------------------------------------------
    # Pestaña SKILLS
    # ------------------------------------------------------------------

    def _crear_pestana_skills(self):
        marco = ttk.Frame(self.pestanas)
        self.pestanas.add(marco, text=f"Skills ({len(self.skills)})")

        marco_filtro = ttk.Frame(marco)
        marco_filtro.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(marco_filtro, text="Buscar:").pack(side=tk.LEFT)
        self.busq_skill = ttk.Entry(marco_filtro, width=25)
        self.busq_skill.pack(side=tk.LEFT, padx=5)
        self.busq_skill.bind('<KeyRelease>', self._filtrar_skills)

        ttk.Label(marco_filtro, text="Categoría:").pack(side=tk.LEFT, padx=(20, 0))
        self.combo_categoria = ttk.Combobox(
            marco_filtro,
            values=['Todas'] + self._obtener_categorias(),
            width=15,
        )
        self.combo_categoria.set('Todas')
        self.combo_categoria.pack(side=tk.LEFT, padx=5)
        self.combo_categoria.bind('<<ComboboxSelected>>', self._filtrar_skills)

        ttk.Label(marco_filtro, text="Total:").pack(side=tk.LEFT, padx=(20, 0))
        self.etiqueta_total_skills = ttk.Label(marco_filtro, text=str(len(self.skills)))
        self.etiqueta_total_skills.pack(side=tk.LEFT)

        panel = ttk.PanedWindow(marco, orient=tk.HORIZONTAL)
        panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        marco_lista = ttk.Frame(panel)
        panel.add(marco_lista, weight=1)

        columnas = ('nombre', 'categoria', 'descripcion')
        self.tabla_skills = ttk.Treeview(marco_lista, columns=columnas, show='tree headings')
        self.tabla_skills.heading('#0',          text='#')
        self.tabla_skills.heading('nombre',      text='Skill')
        self.tabla_skills.heading('categoria',   text='Categoría')
        self.tabla_skills.heading('descripcion', text='Descripción')
        self.tabla_skills.column('#0',          width=40)
        self.tabla_skills.column('nombre',      width=180)
        self.tabla_skills.column('categoria',   width=100)
        self.tabla_skills.column('descripcion', width=300)
        self.tabla_skills.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        barra = ttk.Scrollbar(marco_lista, orient=tk.VERTICAL, command=self.tabla_skills.yview)
        self.tabla_skills.configure(yscrollcommand=barra.set)
        barra.pack(side=tk.RIGHT, fill=tk.Y)

        marco_detalle = ttk.Frame(panel)
        panel.add(marco_detalle, weight=1)

        ttk.Label(marco_detalle, text="Descripción", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=5)
        self.detalle_skill = scrolledtext.ScrolledText(marco_detalle, wrap=tk.WORD, height=15)
        self.detalle_skill.pack(fill=tk.BOTH, expand=True)

        self.tabla_skills.bind('<<TreeviewSelect>>', self._al_seleccionar_skill)
        self._poblar_skills(self.skills)

    def _obtener_categorias(self) -> List[str]:
        return sorted(set(s['categoria'] for s in self.skills))

    def _poblar_skills(self, skills: List[Dict]):
        for fila in self.tabla_skills.get_children():
            self.tabla_skills.delete(fila)
        for i, sk in enumerate(skills, 1):
            self.tabla_skills.insert('', tk.END, text=str(i),
                                     values=(sk['nombre'], sk['categoria'], sk['descripcion']))

    def _filtrar_skills(self, event=None):
        busqueda  = self.busq_skill.get().lower()
        categoria = self.combo_categoria.get()

        filtrados = self.skills
        if categoria != 'Todas':
            filtrados = [s for s in filtrados if s['categoria'] == categoria]
        if busqueda:
            filtrados = [
                s for s in filtrados
                if busqueda in s['nombre'].lower() or busqueda in s['descripcion'].lower()
            ]

        self._poblar_skills(filtrados)
        self.etiqueta_total_skills.config(text=str(len(filtrados)))

    def _al_seleccionar_skill(self, event=None):
        seleccion = self.tabla_skills.selection()
        if not seleccion:
            return
        nombre = self.tabla_skills.item(seleccion[0])['values'][0]
        skill  = next((s for s in self.skills if s['nombre'] == nombre), None)
        if skill:
            texto = (
                f"Skill:      {skill['nombre']}\n\n"
                f"Categoría:  {skill['categoria']}\n\n"
                f"Descripción:\n{skill['descripcion']}\n\n"
                f"Ruta:\n{skill['ruta']}\n\n"
                f"---\n"
                f"Esta skill se activa automáticamente al trabajar\n"
                f"con las tecnologías relacionadas."
            )
            self.detalle_skill.delete('1.0', tk.END)
            self.detalle_skill.insert('1.0', texto)

    # ------------------------------------------------------------------
    # Pestaña COMANDOS
    # ------------------------------------------------------------------

    def _crear_pestana_comandos(self):
        marco = ttk.Frame(self.pestanas)
        self.pestanas.add(marco, text=f"Comandos ({len(self.comandos)})")

        marco_info = ttk.Frame(marco)
        marco_info.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(marco_info, text="Comandos de barra inclinada para Claude Code:",
                  font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(marco_info,
                  text="Úsalos en Claude Code escribiendo  /nombre_del_comando",
                  foreground='gray').pack(anchor=tk.W)

        # Búsqueda
        marco_busqueda = ttk.Frame(marco)
        marco_busqueda.pack(fill=tk.X, padx=10, pady=(0, 5))
        ttk.Label(marco_busqueda, text="Buscar:").pack(side=tk.LEFT)
        self.busq_comando = ttk.Entry(marco_busqueda, width=30)
        self.busq_comando.pack(side=tk.LEFT, padx=5)
        self.busq_comando.bind('<KeyRelease>', self._filtrar_comandos)

        marco_lista = ttk.Frame(marco)
        marco_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        columnas = ('nombre', 'descripcion')
        self.tabla_comandos = ttk.Treeview(marco_lista, columns=columnas, show='tree headings')
        self.tabla_comandos.heading('#0',          text='#')
        self.tabla_comandos.heading('nombre',      text='Comando')
        self.tabla_comandos.heading('descripcion', text='Descripción')
        self.tabla_comandos.column('#0',          width=40)
        self.tabla_comandos.column('nombre',      width=160)
        self.tabla_comandos.column('descripcion', width=400)
        self.tabla_comandos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        barra = ttk.Scrollbar(marco_lista, orient=tk.VERTICAL, command=self.tabla_comandos.yview)
        self.tabla_comandos.configure(yscrollcommand=barra.set)
        barra.pack(side=tk.RIGHT, fill=tk.Y)

        self._poblar_comandos(self.comandos)

    def _poblar_comandos(self, comandos: List[Dict]):
        for fila in self.tabla_comandos.get_children():
            self.tabla_comandos.delete(fila)
        for i, cmd in enumerate(comandos, 1):
            self.tabla_comandos.insert('', tk.END, text=str(i),
                                       values=('/' + cmd['nombre'], cmd['descripcion']))

    def _filtrar_comandos(self, event=None):
        consulta = self.busq_comando.get().lower()
        if not consulta:
            filtrados = self.comandos
        else:
            filtrados = [
                c for c in self.comandos
                if consulta in c['nombre'].lower() or consulta in c['descripcion'].lower()
            ]
        self._poblar_comandos(filtrados)

    # ------------------------------------------------------------------
    # Pestaña REGLAS
    # ------------------------------------------------------------------

    def _crear_pestana_reglas(self):
        marco = ttk.Frame(self.pestanas)
        self.pestanas.add(marco, text=f"Reglas ({len(self.reglas)})")

        marco_info = ttk.Frame(marco)
        marco_info.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(marco_info, text="Reglas de codificación por lenguaje:",
                  font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(marco_info,
                  text="Estas reglas se aplican automáticamente en Claude Code",
                  foreground='gray').pack(anchor=tk.W)

        marco_filtro = ttk.Frame(marco)
        marco_filtro.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(marco_filtro, text="Lenguaje:").pack(side=tk.LEFT)
        self.combo_lenguaje = ttk.Combobox(
            marco_filtro,
            values=['Todos'] + self._obtener_lenguajes_reglas(),
            width=15,
        )
        self.combo_lenguaje.set('Todos')
        self.combo_lenguaje.pack(side=tk.LEFT, padx=5)
        self.combo_lenguaje.bind('<<ComboboxSelected>>', self._filtrar_reglas)

        marco_lista = ttk.Frame(marco)
        marco_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        columnas = ('nombre', 'lenguaje')
        self.tabla_reglas = ttk.Treeview(marco_lista, columns=columnas, show='tree headings')
        self.tabla_reglas.heading('#0',        text='#')
        self.tabla_reglas.heading('nombre',    text='Regla')
        self.tabla_reglas.heading('lenguaje',  text='Lenguaje')
        self.tabla_reglas.column('#0',        width=40)
        self.tabla_reglas.column('nombre',    width=260)
        self.tabla_reglas.column('lenguaje',  width=110)
        self.tabla_reglas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        barra = ttk.Scrollbar(marco_lista, orient=tk.VERTICAL, command=self.tabla_reglas.yview)
        self.tabla_reglas.configure(yscrollcommand=barra.set)
        barra.pack(side=tk.RIGHT, fill=tk.Y)

        self._poblar_reglas(self.reglas)

    def _obtener_lenguajes_reglas(self) -> List[str]:
        return sorted(set(r['lenguaje'] for r in self.reglas))

    def _poblar_reglas(self, reglas: List[Dict]):
        for fila in self.tabla_reglas.get_children():
            self.tabla_reglas.delete(fila)
        for i, reg in enumerate(reglas, 1):
            self.tabla_reglas.insert('', tk.END, text=str(i),
                                     values=(reg['nombre'], reg['lenguaje']))

    def _filtrar_reglas(self, event=None):
        lenguaje = self.combo_lenguaje.get()
        filtradas = self.reglas if lenguaje == 'Todos' else [
            r for r in self.reglas if r['lenguaje'] == lenguaje
        ]
        self._poblar_reglas(filtradas)

    # ------------------------------------------------------------------
    # Pestaña AJUSTES
    # ------------------------------------------------------------------

    def _crear_pestana_ajustes(self):
        marco = ttk.Frame(self.pestanas)
        self.pestanas.add(marco, text="Ajustes")

        # Ruta del proyecto
        marco_ruta = ttk.LabelFrame(marco, text="Ruta del proyecto", padding=10)
        marco_ruta.pack(fill=tk.X, padx=10, pady=10)

        self.entrada_ruta = ttk.Entry(marco_ruta, width=60)
        self.entrada_ruta.insert(0, self.ruta_proyecto)
        self.entrada_ruta.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(marco_ruta, text="Examinar…", command=self._examinar_ruta).pack(side=tk.LEFT, padx=5)

        # Apariencia
        marco_apariencia = ttk.LabelFrame(marco, text="Apariencia", padding=10)
        marco_apariencia.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(marco_apariencia, text="Tema:").pack(anchor=tk.W)
        self.var_tema = tk.StringVar(value='claro')
        ttk.Radiobutton(marco_apariencia, text="Claro", variable=self.var_tema,
                        value='claro', command=self._aplicar_tema).pack(anchor=tk.W)
        ttk.Radiobutton(marco_apariencia, text="Oscuro", variable=self.var_tema,
                        value='oscuro', command=self._aplicar_tema).pack(anchor=tk.W)

        # Fuente
        marco_fuente = ttk.LabelFrame(marco, text="Fuente", padding=10)
        marco_fuente.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(marco_fuente, text="Familia:").pack(anchor=tk.W)
        self.var_fuente = tk.StringVar(value='Arial')
        fuentes = ['Arial', 'Helvetica', 'Verdana', 'Tahoma', 'Georgia',
                   'Courier New', 'Times New Roman', 'Trebuchet MS']
        self.combo_fuente = ttk.Combobox(marco_fuente, textvariable=self.var_fuente,
                                          values=fuentes, state='readonly')
        self.combo_fuente.pack(anchor=tk.W, fill=tk.X, pady=(5, 0))
        self.combo_fuente.bind('<<ComboboxSelected>>', lambda e: self._aplicar_tema())

        ttk.Label(marco_fuente, text="Tamaño:").pack(anchor=tk.W, pady=(10, 0))
        self.var_tamano = tk.StringVar(value='10')
        self.combo_tamano = ttk.Combobox(marco_fuente, textvariable=self.var_tamano,
                                          values=['8','9','10','11','12','14','16','18','20'],
                                          state='readonly', width=10)
        self.combo_tamano.pack(anchor=tk.W, pady=(5, 0))
        self.combo_tamano.bind('<<ComboboxSelected>>', lambda e: self._aplicar_tema())

        # Acciones rápidas
        marco_acciones = ttk.LabelFrame(marco, text="Acciones rápidas", padding=10)
        marco_acciones.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Button(marco_acciones, text="Abrir terminal en el proyecto",
                   command=self._abrir_terminal).pack(fill=tk.X, pady=2)
        ttk.Button(marco_acciones, text="Abrir README",
                   command=self._abrir_readme).pack(fill=tk.X, pady=2)
        ttk.Button(marco_acciones, text="Abrir AGENTS.md",
                   command=self._abrir_agentes_md).pack(fill=tk.X, pady=2)
        ttk.Button(marco_acciones, text="Actualizar datos",
                   command=self._actualizar_datos).pack(fill=tk.X, pady=2)

        # Acerca de
        marco_acerca = ttk.LabelFrame(marco, text="Acerca de", padding=10)
        marco_acerca.pack(fill=tk.X, padx=10, pady=10)

        texto_acerca = (
            "Panel ECC — Everything Claude Code (ES)\n"
            "Versión: 2.0.0-rc.1\n\n"
            "Aplicación de escritorio multiplataforma para\n"
            "explorar y gestionar componentes ECC.\n\n"
            "Proyecto: github.com/affaan-m/everything-claude-code"
        )
        ttk.Label(marco_acerca, text=texto_acerca, justify=tk.LEFT).pack(anchor=tk.W)

    # ------------------------------------------------------------------
    # Acciones de ajustes
    # ------------------------------------------------------------------

    def _examinar_ruta(self):
        from tkinter import filedialog
        ruta = filedialog.askdirectory(initialdir=self.ruta_proyecto)
        if ruta:
            self.entrada_ruta.delete(0, tk.END)
            self.entrada_ruta.insert(0, ruta)

    def _abrir_terminal(self):
        ruta = self.entrada_ruta.get()
        argv, kwargs = build_terminal_launch(ruta)
        subprocess.Popen(argv, **kwargs)

    def _abrir_readme(self):
        ruta = os.path.join(self.entrada_ruta.get(), 'README.md')
        if os.path.exists(ruta):
            subprocess.Popen(['start' if os.name == 'nt' else 'xdg-open', ruta], shell=(os.name == 'nt'))
        else:
            messagebox.showerror("Error", "No se encontró README.md")

    def _abrir_agentes_md(self):
        ruta = os.path.join(self.entrada_ruta.get(), 'AGENTS.md')
        if os.path.exists(ruta):
            subprocess.Popen(['start' if os.name == 'nt' else 'xdg-open', ruta], shell=(os.name == 'nt'))
        else:
            messagebox.showerror("Error", "No se encontró AGENTS.md")

    def _actualizar_datos(self):
        self.ruta_proyecto = self.entrada_ruta.get()
        self.agentes  = cargar_agentes(self.ruta_proyecto)
        self.skills   = cargar_skills(self.ruta_proyecto)
        self.comandos = cargar_comandos(self.ruta_proyecto)
        self.reglas   = cargar_reglas(self.ruta_proyecto)

        self.pestanas.tab(0, text=f"Agentes ({len(self.agentes)})")
        self.pestanas.tab(1, text=f"Skills ({len(self.skills)})")
        self.pestanas.tab(2, text=f"Comandos ({len(self.comandos)})")
        self.pestanas.tab(3, text=f"Reglas ({len(self.reglas)})")

        self._poblar_agentes(self.agentes)
        self._poblar_skills(self.skills)
        self._poblar_comandos(self.comandos)
        self._poblar_reglas(self.reglas)

        self.etiqueta_estado.config(text=self._texto_estado())
        messagebox.showinfo("Éxito", "¡Datos actualizados correctamente!")

    def _aplicar_tema(self):
        tema       = self.var_tema.get()
        familia    = self.var_fuente.get()
        tamano     = int(self.var_tamano.get())
        fuente     = (familia, tamano)

        if tema == 'oscuro':
            fondo     = '#2b2b2b'
            texto     = '#ffffff'
            entrada   = '#3c3c3c'
            marco_bg  = '#2b2b2b'
            seleccion = '#0f5a9e'
        else:
            fondo     = '#f0f0f0'
            texto     = '#000000'
            entrada   = '#ffffff'
            marco_bg  = '#f0f0f0'
            seleccion = '#e0e0e0'

        self.configure(background=fondo)
        estilo = ttk.Style()
        estilo.configure('.',                background=fondo,    foreground=texto,  font=fuente)
        estilo.configure('TFrame',           background=fondo,    font=fuente)
        estilo.configure('TLabel',           background=fondo,    foreground=texto,  font=fuente)
        estilo.configure('TNotebook',        background=fondo,    font=fuente)
        estilo.configure('TNotebook.Tab',    background=marco_bg, foreground=texto,  font=fuente)
        estilo.map('TNotebook.Tab',          background=[('selected', seleccion)])
        estilo.configure('Treeview',         background=entrada,  foreground=texto,  fieldbackground=entrada, font=fuente)
        estilo.configure('Treeview.Heading', background=marco_bg, foreground=texto,  font=fuente)
        estilo.configure('TEntry',           fieldbackground=entrada, foreground=texto, font=fuente)
        estilo.configure('TButton',          background=marco_bg, foreground=texto,  font=fuente)

        self.etiqueta_titulo.configure(font=(familia, 18, 'bold'))
        self.etiqueta_version.configure(font=(familia, 10))
        self.update()


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == '__main__':
    app = PanelECC()
    app.mainloop()
