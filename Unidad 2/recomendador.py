"""
Algoritmo de recomendación central basado en una Red Bayesiana
discreta construida a partir de la relación "Plato -> Ingrediente".

Flujo general:
  1. Construir una BN donde la variable `Plato` es padre de cada variable
     `Ingred__<nombre>` que indica presencia/ausencia del ingrediente.
  2. Hacer inferencia P(Plato | evidencia) usando como evidencia los
     ingredientes que al usuario le gustan (o directamente los ingredientes
     marcados en su perfil).
  3. Aplicar vetos deterministas (platos que explícitamente no le gustan y
     platos que contienen ingredientes en `alergias` o `restricciones`).
  4. Aplicar penalizaciones multiplicativas por ingredientes que no le
     gustan o que no están disponibles.
  5. Reforzar suavemente platos con ingredientes similares a los de los
     platos marcados como `platos_gustan` (Jaccard) y aplicar un pequeño
     "boost" directo a los platos explicitamente marcados como gusta.
  6. Renormalizar y devolver la lista de platos con su probabilidad.
"""

from typing import List, Dict, Any
import math

# Import directo de pgmpy (se espera que esté instalado en el entorno)
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination


def recomendar_platillos_bn(platillos: List[Dict[str, Any]], usuario: Dict[str, Any], disponibilidad_ingredientes: Dict[str, bool] = None, normalize: bool = True) -> List[Dict[str, Any]]:
    """Calcula recomendaciones usando una Red Bayesiana simple.

    Entradas:
      - platillos: lista de dicts con keys 'id', 'name', 'ingredients', 'available'
      - usuario: perfil con campos esperados (platos_gustan, platos_no_gustan,
        ingredientes_gustan, alergias, restricciones, ingredientes_no_gustan).
      - disponibilidad_ingredientes: mapping ingrediente -> bool (opcional).

    Salida: lista de diccionarios de plato con campos adicionales:
      - 'probability': probabilidad posterior normalizada
      - 'score': log(probability) para ranking estable
    """
    # Normalizar diversos campos del perfil de usuario a conjuntos en minúsculas
    likes = set(i.lower() for i in usuario.get('likes', []) or usuario.get('ingredientes_gustan', []))
    allergies = set(i.lower() for i in usuario.get('allergies', []) or usuario.get('alergias', []))
    restrictions = set(i.lower() for i in usuario.get('restricciones', []) or usuario.get('restricciones', []))
    platos_no_gustan = set(usuario.get('platos_no_gustan', []))
    platos_gustan = set(str(x) for x in usuario.get('platos_gustan', []) or [])
    ingredientes_no_gustan = set(i.lower() for i in usuario.get('ingredientes_no_gustan', []) or usuario.get('ingredientes_no_gustan', []))

    # Preparar estructuras auxiliares para construir la BN
    ids_platos = tuple(str(plato.get('id')) for plato in platillos)
    mapa_platos = {str(plato.get('id')): plato for plato in platillos}
    todos_ingredientes = sorted({ing.lower() for plato in platillos for ing in plato.get('ingredients', [])})
    plato_var = 'Plato'
    vars_ingredientes = [f'Ingred__{i.replace(" ","_")}' for i in todos_ingredientes]
    edges = [(plato_var, v) for v in vars_ingredientes]

    # Crear el modelo BN y CPDs
    model = DiscreteBayesianNetwork(edges)

    n_platos = len(ids_platos)
    prior_values = [1.0 / n_platos] * n_platos
    prior_matrix = [[p] for p in prior_values]
    cpd_plato = TabularCPD(variable=plato_var, variable_card=n_platos, values=prior_matrix, state_names={plato_var: list(ids_platos)})

    cpds = [cpd_plato]
    for ing in todos_ingredientes:
        var = f'Ingred__{ing.replace(" ","_")}'
        absent_row = []
        present_row = []
        for id_plato in ids_platos:
            plato = mapa_platos[id_plato]
            ings_plato = {x.lower() for x in plato.get('ingredients', [])}
            if ing in ings_plato:
                absent_row.append(0.2)
                present_row.append(0.8)
            else:
                absent_row.append(0.9)
                present_row.append(0.1)
        cpd = TabularCPD(variable=var, variable_card=2, values=[absent_row, present_row],
                         evidence=[plato_var], evidence_card=[n_platos], state_names={var: ['absent','present'], plato_var: list(ids_platos)})
        cpds.append(cpd)

    model.add_cpds(*cpds)
    if not model.check_model():
        raise RuntimeError('El modelo BN no pasó la validación de consistencia.')

    mapa_indice_plato = {pid: i for i, pid in enumerate(ids_platos)}

    # --- Fase 1: inferencia BN base usando solamente 'likes' como evidencia ---
    inferencia = VariableElimination(model)
    evidencia: Dict[str, str] = {}
    for ing in likes:
        key = f'Ingred__{ing.replace(" ","_")}'
        if key in vars_ingredientes:
            evidencia[key] = 'present'

    q = inferencia.query(variables=['Plato'], evidence=evidencia, show_progress=False)
    dist_plato = q['Plato'] if isinstance(q, dict) else q

    probabilidades: Dict[str, float] = {}
    valores = getattr(dist_plato, 'values', None)
    try:
        if valores is not None:
            for id_plato in ids_platos:
                idx = mapa_indice_plato.get(id_plato, None)
                probabilidades[id_plato] = float(valores[idx]) if idx is not None else 0.0
        elif hasattr(dist_plato, 'state_names') and dist_plato.state_names and 'Plato' in dist_plato.state_names:
            nombres = dist_plato.state_names['Plato']
            for id_plato in ids_platos:
                idx = nombres.index(id_plato)
                probabilidades[id_plato] = float(dist_plato.values[idx])
        else:
            for id_plato in ids_platos:
                probabilidades[id_plato] = float(dist_plato.get(id_plato, 0.0) if hasattr(dist_plato, 'get') else 0.0)
    except Exception:
        probabilidades = {}
        try:
            for k, v in dist_plato.items():
                probabilidades[k] = float(v)
        except Exception:
            probabilidades = {id_plato: 1.0 / n_platos for id_plato in ids_platos}

    # --- Fase 2: aplicar vetos deterministas ---
    for id_plato in list(probabilidades.keys()):
        plato = mapa_platos[id_plato]
        ings_plato = {i.lower() for i in plato.get('ingredients', [])}
        if str(id_plato) in platos_no_gustan:
            probabilidades[id_plato] = 0.0
            continue
        if ings_plato & allergies:
            probabilidades[id_plato] = 0.0
            continue
        if ings_plato & restrictions:
            probabilidades[id_plato] = 0.0
            continue

    # --- Fase 3: aplicar penalizaciones multiplicativas ---
    factor_penalizacion_ingred_no_gusta = 0.1
    factor_penalizacion_no_disponible = 0.2
    for id_plato in list(probabilidades.keys()):
        if probabilidades[id_plato] <= 0:
            continue
        plato = mapa_platos[id_plato]
        ings_plato = {i.lower() for i in plato.get('ingredients', [])}
        if disponibilidad_ingredientes is not None:
            for ing in ings_plato:
                if not disponibilidad_ingredientes.get(ing, True):
                    probabilidades[id_plato] *= factor_penalizacion_no_disponible
        if ingredientes_no_gustan and (ings_plato & ingredientes_no_gustan):
            probabilidades[id_plato] *= factor_penalizacion_ingred_no_gusta

    # --- Reforzar platos similares ---
    ingredientes_referencia = set()
    for pid in platos_gustan:
        if pid in mapa_platos:
            ingredientes_referencia |= {i.lower() for i in mapa_platos[pid].get('ingredients', [])}

    if ingredientes_referencia:
        alpha_sim = 1.0
        for id_plato in list(probabilidades.keys()):
            if probabilidades[id_plato] <= 0:
                continue
            ings_plato = {i.lower() for i in mapa_platos[id_plato].get('ingredients', [])}
            inter = len(ings_plato & ingredientes_referencia)
            union = len(ings_plato | ingredientes_referencia)
            simil = (inter / union) if union > 0 else 0.0
            multiplicador = 1.0 + alpha_sim * simil
            probabilidades[id_plato] *= multiplicador

    boost_plato_gusta = 1.3
    for pid in platos_gustan:
        if pid in probabilidades and probabilidades[pid] > 0:
            probabilidades[pid] *= boost_plato_gusta

    # --- Fase 4: renormalizar y construir resultado final ---
    total = sum(probabilidades.values())
    resultados = []
    for id_plato in ids_platos:
        p_copy = dict(mapa_platos[id_plato])
        prob = (probabilidades.get(id_plato, 0.0) / total) if total > 0 else 0.0
        p_copy['probability'] = prob
        p_copy['score'] = float(math.log(prob) if prob > 0 else float('-inf'))
        resultados.append(p_copy)

    resultados.sort(key=lambda x: x['probability'], reverse=True)
    return resultados
