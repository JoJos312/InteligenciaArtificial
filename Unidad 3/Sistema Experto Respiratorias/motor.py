class SistemaDiagnostico:
    def __init__(self, enfermedades):
        self.enfermedades = enfermedades
        self.hechos = {}
        
        self.mapeo_descripciones = {
            # Síntomas
            "fiebre": "Fiebre",
            "tos_seca": "Tos seca",
            "tos_flema": "Tos con flema",
            "sibilancias": "Sibilancias",
            "dificultad_respirar": "Dificultad respiratoria",
            "opresion_pecho": "Opresión en el pecho",
            "dolor_pecho": "Dolor en el pecho",
            "fatiga": "Fatiga",
            "ronquera": "Ronquera",
            "perdida_voz": "Pérdida de voz",
            "dolor_garganta": "Dolor de garganta",
            "perdida_olfato": "Pérdida del olfato",
            "expectoracion": "Expectoración",
            "dolor_cabeza": "Dolor de cabeza",
            "dolores_musculares": "Dolores musculares",
            "sudoracion_nocturna": "Sudoración nocturna",
            "perdida_peso": "Pérdida de peso",
            "disnea_progresiva": "Disnea progresiva",
            "molestias_toracicas": "Molestias torácicas",
            
            # Factores de riesgo
            "tabaquismo": "Tabaquismo",
            "contacto_infectados": "Contacto con infectados",
            "alergias": "Alergias respiratorias",
            "enfermedades_cronicas": "Enfermedades crónicas",
            "exposicion_humo": "Exposición a humo/polvo",
            "hacinamiento": "Hacinamiento",
            "inmunodepresion": "Sistema inmune debilitado",
            "antecedentes_familiares": "Antecedentes familiares",
            "infecciones_recientes": "Infecciones recientes",
            "exposicion_laboral": "Exposición laboral a gases",
            "irritantes_ambientales": "Irritantes ambientales",
            "uso_voz": "Uso excesivo de la voz",
            "epoca_invierno": "Temporada de invierno",
            "edad_avanzada": "Edad avanzada",
            "es_bebe": "Bebé menor de 2 años",
            
            # Hallazgos
            "pcr_positiva": "PCR positiva",
            "radiografia_infiltrados": "Infiltrados en radiografía",
            "crepitantes": "Crepitantes en auscultación",
            "hiperinsuflacion": "Hiperinsuflación pulmonar",
            "bacilos_acidorresistentes": "Bacilos ácido-resistentes",
            "inflamacion_cuerdas": "Inflamación de cuerdas vocales",
            "espiracion_prolongada": "Espiración prolongada",
            "mejora_broncodilatadores": "Mejora con broncodilatadores",
            "espirometria_alterada": "Espirometría alterada",
            "cavernas_pulmonares": "Cavernas pulmonares",
            "sibilancias_persistentes": "Sibilancias persistentes",
            "ruidos_bronquiales": "Ruidos bronquiales difusos",
            "test_influenza_positivo": "Test de influenza positivo"
        }

    def agregar_hecho(self, clave, valor):
        self.hechos[clave] = valor

    def _evaluar_regla(self, regla):
        if regla["tipo"] == "obligatorios_sugerentes":
            obligatorios_cumplidos = all(
                self.hechos.get(cond[0]) == cond[1] 
                for cond in regla["obligatorios"]
            )
            
            if not obligatorios_cumplidos:
                return 0.0 
            
            sugerentes_cumplidos = sum(
                1 for cond in regla["sugerentes"] 
                if self.hechos.get(cond[0]) == cond[1]
            )
            
            certeza = regla["certeza_base"] + (sugerentes_cumplidos * regla["incremento_sugerente"])
            certeza = min(0.95, certeza)
            
            return certeza 
            
        elif regla["tipo"] == "umbral":
            condiciones_cumplidas = sum(
                1 for cond in regla["condiciones"] 
                if self.hechos.get(cond[0]) == cond[1]
            )
            
            if condiciones_cumplidas >= regla["condiciones_minimas"]:
                return regla["certeza"] 
            else:
                return 0.0 

    def _obtener_coincidencias_desde_reglas(self, enfermedad):
        regla = self.enfermedades[enfermedad]["reglas"]
        coincidentes = []
        
        todas_condiciones = regla.get("obligatorios", []) + regla.get("sugerentes", [])
        
        for cond in todas_condiciones:
            clave, valor_esperado = cond
            if self.hechos.get(clave) == valor_esperado:
                descripcion = self.mapeo_descripciones.get(clave, clave)
                if descripcion not in coincidentes:
                    coincidentes.append(descripcion)
        
        return coincidentes

    def obtener_diagnostico(self, respuestas_sintomas, respuestas_factores, respuestas_hallazgos):
        self.hechos.clear()

        for clave, valor in {**respuestas_sintomas, **respuestas_factores, **respuestas_hallazgos}.items():
            self.agregar_hecho(clave, valor)

        diagnosticos = {}
        for enfermedad, datos in self.enfermedades.items():
            regla = datos["reglas"]
            certeza = self._evaluar_regla(regla) 

            if certeza > 0:
                todas_coincidencias = self._obtener_coincidencias_desde_reglas(enfermedad) 

                diagnosticos[enfermedad] = {
                    'certeza': certeza,
                    'porcentaje': certeza * 100,
                    'recomendaciones': datos['recomendaciones'],
                    'sintomas_coincidentes': todas_coincidencias
                }

        return dict(sorted(diagnosticos.items(), key=lambda x: x[1]['porcentaje'], reverse=True))