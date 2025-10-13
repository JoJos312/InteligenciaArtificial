import json
from typing import List, Dict, Any


def construir_red_semantica_simplificada(usuarios: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Construye la red simplificada que contiene, por usuario, solo las listas requeridas:
        {
            "usuarios": {
                 "u_id": {
                         "platos_gustan": ["p1","p2"],
                         "platos_no_gustan": ["p3"],
                         "ingredientes_gustan": ["lechuga"],
                         "alergias": ["salmón"],
                         "restricciones": ["carne"]
                 }, ...
            }
        }
    """
    out: Dict[str, Any] = {"usuarios": {}}
    for u in usuarios:
        uid = u.get('id') or u.get('nombre')
        out['usuarios'][uid] = {
            'platos_gustan': [p for p in u.get('platos_gustan', [])],
            'platos_no_gustan': [p for p in u.get('platos_no_gustan', [])],
            'ingredientes_gustan': [i.lower() for i in u.get('ingredientes_gustan', [])],
            'alergias': [i.lower() for i in u.get('alergias', [])],
            'restricciones': [r.lower() for r in u.get('restricciones', [])]
        }
    return out


def guardar_red(path: str, estructura: Dict[str, Any]):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(estructura, f, indent=2, ensure_ascii=False)
