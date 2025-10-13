"""
Utilidades simples para leer/escribir la "red semántica" y una colección
de triples en formato JSON.

Este módulo agrupa I/O ligero usado por la GUI y el CLI. No contiene
ninguna lógica de inferencia, solo funciones para persistencia y normalización.
"""

import json
from typing import List, Dict, Any


def cargar_triples(path: str) -> List[Dict[str, Any]]:
    """Carga una lista de triples (JSON) desde `path`.

    Un "triple" aquí se modela como un dict con keys 's', 'p', 'o'.
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def guardar_triples(path: str, triples: List[Dict[str, Any]]):
    """Guarda la lista de triples en `path` en formato JSON legible."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(triples, f, indent=2, ensure_ascii=False)


def existe_triple(triples: List[Dict[str, Any]], s: str, p: str, o: Any) -> bool:
    """Comprueba si un triple ya existe en la lista (comparación exacta)."""
    for t in triples:
        if t.get('s') == s and t.get('p') == p and t.get('o') == o:
            return True
    return False


def añadir_triple(path: str, s: str, p: str, o: Any) -> bool:
    """Añade un triple a `path` si no existía.

    Devuelve True si se añadió; False si ya existía.
    """
    triples = cargar_triples(path)
    if existe_triple(triples, s, p, o):
        return False
    triples.append({"s": s, "p": p, "o": o})
    guardar_triples(path, triples)
    return True


def cargar_red_simplificada(path: str) -> Dict[str, Any]:
    """Carga la estructura simplificada de la red semántica.

    Formato esperado: { 'usuarios': { <uid>: { ...perfil... } } }
    Se usa directamente por la GUI y por el CLI.
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def guardar_red_simplificada(path: str, estructura: Dict[str, Any]):
    """Guarda la estructura simplificada de la red semántica en JSON."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(estructura, f, indent=2, ensure_ascii=False)


def agregar_o_actualizar_usuario_en_red(path: str, usuario: Dict[str, Any]) -> None:
    """Helper para añadir o actualizar un usuario en el archivo de red.

    Normaliza a minúsculas ciertos campos y asegura la clave `usuarios`.
    `usuario` debe contener al menos una clave 'id' o 'nombre' para usarla
    como identificador.
    """
    try:
        red = cargar_red_simplificada(path)
    except FileNotFoundError:
        red = {'usuarios': {}}

    uid = usuario.get('id') or usuario.get('nombre')
    red.setdefault('usuarios', {})
    # normalizar campos
    red['usuarios'][uid] = {
        'platos_gustan': usuario.get('platos_gustan', []),
        'platos_no_gustan': usuario.get('platos_no_gustan', []),
        'ingredientes_gustan': [i.lower() for i in usuario.get('ingredientes_gustan', [])],
        'alergias': [i.lower() for i in usuario.get('alergias', [])],
        'restricciones': [r.lower() for r in usuario.get('restricciones', [])]
    }
    guardar_red_simplificada(path, red)
