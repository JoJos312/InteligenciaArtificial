enfermedades = {
    "asma": {
        "recomendaciones": ["Evitar exposición a humo o polvo","Usar broncodilatadores según indicación médica","Consultar con neumólogo si los síntomas empeoran"],
        
        "reglas": {
            "tipo": "obligatorios_sugerentes",
            "obligatorios": [
                ("sibilancias", "Sí"),
                ("dificultad_respirar", "Sí")
            ],
            "sugerentes": [
                ("tos_seca", "Sí"),
                ("opresion_pecho", "Sí"),
                ("alergias", "Sí"),
                ("antecedentes_familiares", "Sí"),
                ("exposicion_humo", "Sí"),
                ("espiracion_prolongada", "Sí"),
                ("mejora_broncodilatadores", "Sí")
            ],
            "certeza_base": 0.7,
            "incremento_sugerente": 0.05,
        }
    },
    
    "neumonia": {
        "recomendaciones": ["Realizar radiografía de tórax","Consultar con un médico especialista","Tomar antibióticos solo bajo supervisión médica"],
        
        "reglas": {
            "tipo": "umbral",
            "condiciones_minimas": 4,
            "condiciones": [
                ("fiebre", "Sí"),
                ("tos_flema", "Sí"),
                ("dificultad_respirar", "Sí"),
                ("dolor_pecho", "Sí"),
                ("crepitantes", "Sí"),
                ("radiografia_infiltrados", "Sí"),
                ("edad_avanzada", "Sí"),
                ("tabaquismo", "Sí"),
                ("enfermedades_cronicas", "Sí")
            ],
            "certeza": 0.85,
        }
    },

    "bronquitis": {
        "recomendaciones": ["Evitar fumar y ambientes con humo","Beber líquidos calientes y descansar","Consultar al médico si la tos dura más de 3 semanas"],

        "reglas": {
            "tipo": "obligatorios_sugerentes",
            "obligatorios": [
                ("tos_flema", "Sí"),
                ("expectoracion", "Sí")
            ],
            "sugerentes": [
                ("molestias_toracicas", "Sí"),
                ("fatiga", "Sí"),
                ("infecciones_recientes", "Sí"),
                ("tabaquismo", "Sí"),
                ("exposicion_humo", "Sí"),
                ("ruidos_bronquiales", "Sí")
            ],
            "certeza_base": 0.65,
            "incremento_sugerente": 0.06,
        }
    },
    
    "covid19": {
        "recomendaciones": ["Aislarse y usar cubrebocas", "Controlar la temperatura y la oxigenación", "Buscar atención médica si hay dificultad respiratoria"],

        "reglas": {
            "tipo": "obligatorios_sugerentes",
            "obligatorios": [
                ("fiebre", "Sí"),
                ("tos_seca", "Sí")
            ],
            "sugerentes": [
                ("fatiga", "Sí"),
                ("dificultad_respirar", "Sí"),
                ("perdida_olfato", "Sí"),
                ("contacto_infectados", "Sí"),
                ("enfermedades_cronicas", "Sí"),
                ("pcr_positiva", "Sí"),
                ("radiografia_infiltrados", "Sí")
            ],
            "certeza_base": 0.6,
            "incremento_sugerente": 0.06
        }
    },
    
    "tuberculosis": {
        "recomendaciones": ["Realizar prueba de bacilos ácido-alcohol resistentes", "Completar tratamiento antituberculoso según indicación médica", "Evitar contacto cercano con otras personas"],

        "reglas": {
            "tipo": "obligatorios_sugerentes",
            "obligatorios": [
                ("tos_flema", "Sí"),
                ("perdida_peso", "Sí")
            ],
            "sugerentes": [
                ("fiebre", "Sí"),
                ("sudoracion_nocturna", "Sí"),
                ("inmunodepresion", "Sí"),
                ("hacinamiento", "Sí"),
                ("contacto_infectados", "Sí"),
                ("bacilos_acidorresistentes", "Sí"),
                ("cavernas_pulmonares", "Sí")
            ],
            "certeza_base": 0.75,
            "incremento_sugerente": 0.04,
        }
    },
    
    "laringitis": {
        "recomendaciones": ["Guardar reposo vocal", "Evitar irritantes (humo, alcohol, gritar)", "Tomar líquidos tibios para aliviar la garganta"],

        "reglas": {
            "tipo": "obligatorios_sugerentes",
            "obligatorios": [
                ("ronquera", "Sí"),
                ("dolor_garganta", "Sí")
            ],
            "sugerentes": [
                ("tos_seca", "Sí"),
                ("perdida_voz", "Sí"),
                ("uso_voz", "Sí"),
                ("infecciones_recientes", "Sí"),
                ("irritantes_ambientales", "Sí"),
                ("inflamacion_cuerdas", "Sí")
            ],
            "certeza_base": 0.8,
            "incremento_sugerente": 0.04
        }
    },
    
    "epoc": {
        "recomendaciones": ["Dejar de fumar completamente", "Seguir tratamiento broncodilatador o con oxígeno", "Realizar controles regulares de espirometría"],

        "reglas": {
            "tipo": "obligatorios_sugerentes",
            "obligatorios": [
                ("disnea_progresiva", "Sí"),
                ("tos_seca", "Sí"),
                ("expectoracion", "Sí")
            ],
            "sugerentes": [
                ("fatiga", "Sí"),
                ("tabaquismo", "Sí"),
                ("exposicion_laboral", "Sí"),
                ("edad_avanzada", "Sí"),
                ("hiperinsuflacion", "Sí"),
                ("sibilancias_persistentes", "Sí"),
                ("espirometria_alterada", "Sí")
            ],
            "certeza_base": 0.7,
            "incremento_sugerente": 0.05
        }
    },
    
    "bronquiolitis": {
        "recomendaciones": ["Mantener buena hidratación del bebé","Evitar exposición al humo de tabaco","Consultar al pediatra si hay dificultad respiratoria severa"],

        "reglas": {
            "tipo": "obligatorios_sugerentes",
            "obligatorios": [
                ("es_bebe", "Sí"),
                ("dificultad_respirar", "Sí")
            ],
            "sugerentes": [
                ("tos_seca", "Sí"),
                ("fiebre", "Sí"),
                ("sibilancias", "Sí"),
                ("crepitantes", "Sí"),
                ("hiperinsuflacion", "Sí")
            ],
            "certeza_base": 0.8,
            "incremento_sugerente": 0.04,
        }
    },
    
    "influenza": {
        "recomendaciones": ["Descansar y mantenerse hidratado","Tomar medicamentos antipiréticos según indicación médica","Evitar contacto con otras personas durante el contagio"],

        "reglas": {
            "tipo": "obligatorios_sugerentes",
            "obligatorios": [
                ("fiebre", "Sí"),
                ("dolores_musculares", "Sí")
            ],
            "sugerentes": [
                ("dolor_cabeza", "Sí"),
                ("tos_seca", "Sí"),
                ("fatiga", "Sí"),
                ("contacto_infectados", "Sí"),
                ("inmunodepresion", "Sí"),
                ("epoca_invierno", "Sí"),
                ("test_influenza_positivo", "Sí")
            ],
            "certeza_base": 0.75,
            "incremento_sugerente": 0.04
        }
    }
}