"""
CLI de demostración para el recomendador.

Este archivo contiene un cliente mínimo que carga los datos de platos y la
red semántica (usuarios) desde `data/` y muestra por consola las
recomendaciones devueltas por la función `recomendar_platillos_bn`.

Propósito: facilitar pruebas manuales rápidas y debugging.
"""

import json
from pathlib import Path
from typing import Dict, Any
import argparse

from recomendador import recomendar_platillos_bn
from herramientas_semanticas import cargar_red_simplificada


# Rutas de datos relativas al proyecto
DATA_DIR = Path(__file__).parent / 'data'
DISHESPATH = DATA_DIR / 'platillos.json'
DISP_INGS_PATH = DATA_DIR / 'ingredientes_disponibilidad.json'


def load_json(path):
    """Carga un JSON desde disco y devuelve la estructura Python.

    Este pequeño helper encapsula la lectura con encoding UTF-8.
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def pretty_platillo(p: Dict[str, Any]) -> str:
    """Formato legible para imprimir un diccionario de plato.

    p: dic con keys esperadas: 'id', 'name', 'ingredients'.
    """
    return f"[{p['id']}] {p.get('name', '')} - ingredientes: {', '.join(p.get('ingredients', []))}"


def main(user_id: str | None = None):
    """Punto de entrada principal usado cuando se ejecuta el módulo.

    Si `user_id` es None se mostrarán las recomendaciones para todos los
    usuarios presentes en `data/red_semantica.json`. La función carga
    platos, disponibilidad de ingredientes y la red semántica antes de
    invocar a la BN.
    """
    platillos = load_json(DISHESPATH)
    disponibilidad = load_json(DISP_INGS_PATH)

    sn_path = DATA_DIR / 'red_semantica.json'
    red = cargar_red_simplificada(str(sn_path)) if sn_path.exists() else {'usuarios': {}}

    if not red['usuarios']:
        print('La red semántica está vacía. Pobla `data/red_semantica.json` con usuarios.')
        return


    def show_for(uid, perfil):
        """Imprime por consola las recomendaciones (posterior BN) del usuario.

        Se encapsula la llamada a `recomendar_platillos_bn` para separar
        la lógica de presentación del resto del flujo.
        """
        print(f"Usuario: {perfil.get('nombre', uid)} (id={uid}) [BN]")
        try:
            # Usar solo la posterior de la BN (una probabilidad por plato)
            recs_post = recomendar_platillos_bn(platillos, perfil, disponibilidad_ingredientes=disponibilidad, normalize=True)
        except Exception as e:
            print('Error al ejecutar la BN:', e)
            return
        if not recs_post:
            print('  -> No hay recomendaciones seguras para este usuario.')
            print('\n' + '-'*40 + '\n')
            return
        # mostrar TODOS los platillos con la probabilidad posterior (BN)
        for p in recs_post:
            print(f"  - {pretty_platillo(p)}  (P_posterior={p.get('probability', 0):.2f}, score={p.get('score'):.3f})")
        print('\n')
        print('\n' + '-'*40 + '\n')

    # Si se solicitó un user_id concreto, mostrar solo ese usuario
    if user_id:
        if user_id in red['usuarios']:
            show_for(user_id, red['usuarios'][user_id])
        else:
            print(f"Usuario '{user_id}' no encontrado en la red semántica.")
    else:
        # Mostrar para todos los usuarios
        for uid, perfil in red['usuarios'].items():
            show_for(uid, perfil)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mostrar todas las recomendaciones BN desde la red semántica (siempre normalizado)')
    parser.add_argument('user_id', nargs='?', help='ID del usuario a mostrar (opcional)')
    args = parser.parse_args()

    # pedir user_id si no se pasó (ENTER -> mostrar todos)
    user_id = args.user_id
    if not user_id:
        try:
            user_input = input('ID de usuario (ENTER para mostrar todos): ').strip()
        except EOFError:
            user_input = ''
        user_id = user_input or None

    main(user_id)
