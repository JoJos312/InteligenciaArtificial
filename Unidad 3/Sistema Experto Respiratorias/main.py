import tkinter as tk
from tkinter import messagebox, scrolledtext
import BC
from motor import SistemaDiagnostico

class SistemaExperto:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Experto en Enfermedades Respiratorias")
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        self.datos = {}
        self.historial_pantallas = []
        self.motor = SistemaDiagnostico(BC.enfermedades)

        self.crear_formulario_demografico()

    # ====== FORMULARIO DEMOGRÁFICO ======
    def crear_formulario_demografico(self):
        self.limpiar_pantalla()
        self.historial_pantallas.clear()

        tk.Label(self.root, text="=== Datos Demográficos ===", font=("Arial", 14, "bold")).pack(pady=10)
        self.campos = {}

        for texto in ["Edad", "Sexo (M/F)", "Altura (cm)", "Peso (kg)"]:
            tk.Label(self.root, text=texto + ":").pack()
            entrada = tk.Entry(self.root, width=30)
            entrada.pack(pady=3)
            self.campos[texto] = entrada

        tk.Button(self.root, text="Continuar", command=self.validar_datos).pack(pady=15)

    def validar_datos(self):
        self.datos = {k: v.get().strip() for k, v in self.campos.items()}
        if any(not valor for valor in self.datos.values()):
            messagebox.showwarning("Campos vacíos", "Por favor complete todos los datos demográficos.")
            return
        
        # Validar que la edad sea un número
        try:
            int(self.datos["Edad"])
        except ValueError:
            messagebox.showwarning("Edad inválida", "Por favor ingrese una edad válida (número entero).")
            return
            
        self.mostrar_lista_sintomas()

    def mostrar_lista_sintomas(self):
        self.historial_pantallas.append(self.crear_formulario_demografico)
        self.limpiar_pantalla()
        self.crear_pantalla_preguntas("Síntomas Respiratorios", self.obtener_sintomas(), self.guardar_sintomas)

    def guardar_sintomas(self, respuestas):
        self.resp_sintomas = respuestas
        self.mostrar_factores_riesgo()

    def mostrar_factores_riesgo(self):
        self.historial_pantallas.append(self.mostrar_lista_sintomas)
        self.limpiar_pantalla()
        self.crear_pantalla_preguntas("Factores de Riesgo", self.obtener_factores(), self.guardar_factores)

    def mostrar_hallazgos(self):
        self.historial_pantallas.append(self.mostrar_factores_riesgo)
        self.limpiar_pantalla()
        self.crear_pantalla_preguntas("Hallazgos Clínicos", self.obtener_hallazgos(), self.finalizar_encuesta)

    def guardar_factores(self, respuestas):
        self.resp_factores = respuestas

        try:
            edad = int(self.datos["Edad"])
            if edad > 60:
                self.resp_factores["edad_avanzada"] = "Sí"
            else:
                self.resp_factores["edad_avanzada"] = "No"

            if edad < 2:
                self.resp_factores["es_bebe"] = "Sí"
            else:
                self.resp_factores["es_bebe"] = "No"

        except:
            self.resp_factores["edad_avanzada"] = "No"
            self.resp_factores["es_bebe"] = "No"

        self.mostrar_hallazgos()

    # ====== MÉTODO GENERAL PARA PANTALLAS ======
    def crear_pantalla_preguntas(self, titulo, preguntas_dict, siguiente_funcion):
        contenedor = tk.Frame(self.root)
        contenedor.pack(fill="both", expand=True)

        canvas = tk.Canvas(contenedor)
        scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
        frame_scrollable = tk.Frame(canvas)

        frame_scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame_scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(frame_scrollable, text=f"=== {titulo} ===", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(frame_scrollable, text="Responda Sí o No según corresponda:", font=("Arial", 11)).pack(pady=5)

        respuestas = {}
        for clave, pregunta in preguntas_dict.items():
            fila = tk.Frame(frame_scrollable)
            fila.pack(fill="x", pady=3, padx=10)
            tk.Label(fila, text=pregunta, anchor="w", justify="left", wraplength=500).pack(side="left", padx=5)
            var = tk.StringVar(value="No")
            respuestas[clave] = var
            tk.Radiobutton(fila, text="Sí", variable=var, value="Sí").pack(side="right", padx=5)
            tk.Radiobutton(fila, text="No", variable=var, value="No").pack(side="right")

        # --- Botones de navegación ---
        boton_frame = tk.Frame(frame_scrollable)
        boton_frame.pack(pady=20)

        tk.Button(boton_frame, text="Volver atrás", command=self.volver_atras).pack(side="left", padx=10)
        tk.Button(boton_frame, text="Continuar", command=lambda: siguiente_funcion({k: v.get() for k, v in respuestas.items()})).pack(side="left")

    # ====== FINAL - MOSTRAR DIAGNÓSTICO ======
    def finalizar_encuesta(self, respuestas):
        self.resp_hallazgos = respuestas
        
        # Obtener diagnóstico del motor
        diagnostico = self.motor.obtener_diagnostico(
            self.resp_sintomas, 
            self.resp_factores, 
            self.resp_hallazgos
        )
        
        self.mostrar_resultados(diagnostico)

    def obtener_coincidencias_usuario(self, datos_enfermedad, respuestas_usuario, mapeo):
        coincidencias = []
        for item_enfermedad in datos_enfermedad:
            for clave_respuesta, items_mapeados in mapeo.items():
                if item_enfermedad in items_mapeados and respuestas_usuario.get(clave_respuesta, "No") == "Sí":
                    coincidencias.append(item_enfermedad)
                    break
        return coincidencias
    
    def mostrar_resultados(self, diagnostico):
        self.limpiar_pantalla()

        tk.Label(self.root, text="=== RESULTADOS DEL DIAGNÓSTICO ===", 
                 font=("Arial", 16, "bold")).pack(pady=10)

        texto_frame = tk.Frame(self.root)
        texto_frame.pack(fill="both", expand=True, padx=10, pady=5)

        texto_resultado = scrolledtext.ScrolledText(texto_frame, width=80, height=25, font=("Arial", 10))
        texto_resultado.pack(fill="both", expand=True)

        resultados_ordenados = sorted(
            diagnostico.items(), 
            key=lambda x: x[1]['porcentaje'], 
            reverse=True
        )

        texto_resultado.insert(tk.END, "DATOS DEMOGRÁFICOS:\n")
        texto_resultado.insert(tk.END, "-" * 40 + "\n")
        for k, v in self.datos.items():
            texto_resultado.insert(tk.END, f"{k}: {v}\n")

        try:
            edad = int(self.datos["Edad"])
            if edad > 60:
                texto_resultado.insert(tk.END, "Factor de riesgo automático: Edad avanzada (mayor de 60 años)\n")
        except:
            pass

        texto_resultado.insert(tk.END, "\n\nDIAGNÓSTICO:\n")
        texto_resultado.insert(tk.END, "=" * 50 + "\n\n")

        for enfermedad, datos in resultados_ordenados:
            if datos['porcentaje'] > 0:
                texto_resultado.insert(tk.END, f"{enfermedad.upper()}: {datos['porcentaje']:.1f}% de coincidencia\n")

                if datos['sintomas_coincidentes']:
                    texto_resultado.insert(tk.END, f"   Síntomas detectados: {', '.join(datos['sintomas_coincidentes'])}\n")

                if datos['recomendaciones']:
                    texto_resultado.insert(tk.END, "   Recomendaciones:\n")
                    for rec in datos['recomendaciones']:
                        texto_resultado.insert(tk.END, f"      - {rec}\n")

                texto_resultado.insert(tk.END, "-" * 50 + "\n\n")

        texto_resultado.config(state=tk.DISABLED)

        botones_frame = tk.Frame(self.root)
        botones_frame.pack(pady=10)

        tk.Button(botones_frame, text="Nueva Consulta", 
                  command=self.crear_formulario_demografico).pack(side="left", padx=5)
        tk.Button(botones_frame, text="Salir", 
                  command=self.root.quit).pack(side="left", padx=5)
    

    # ====== NAVEGACIÓN HACÍA ATRÁS ======
    def volver_atras(self):
        if self.historial_pantallas:
            pantalla_anterior = self.historial_pantallas.pop()
            pantalla_anterior()
        else:
            messagebox.showinfo("Inicio", "Ya estás en la primera pantalla.")

    # ====== LISTAS DE PREGUNTAS ======
    def obtener_sintomas(self):
        return {
            "fiebre": "¿Tiene fiebre?",
            "tos_seca": "¿Tiene tos seca?",
            "tos_flema": "¿Tose con flema?",
            "sibilancias": "¿Escucha silbidos al respirar?",
            "dificultad_respirar": "¿Tiene dificultad para respirar?",
            "opresion_pecho": "¿Siente opresión en el pecho?",
            "dolor_pecho": "¿Tiene dolor en el pecho?",
            "fatiga": "¿Se siente fatigado?",
            "ronquera": "¿Tiene la voz ronca?",
            "perdida_voz": "¿Ha perdido la voz?",
            "dolor_garganta": "¿Tiene dolor de garganta?",
            "perdida_olfato": "¿Ha perdido el sentido del olfato?",
            "expectoracion": "¿Tiene expectoración o flemas?",
            "dolor_cabeza": "¿Tiene dolor de cabeza?",
            "dolores_musculares": "¿Tiene dolores musculares?",
            "sudoracion_nocturna": "¿Tiene sudoración nocturna?",
            "perdida_peso": "¿Ha perdido peso recientemente sin causa aparente?",
            "molestias_toracicas": "¿Siente molestias torácicas?",
            "disnea_progresiva": "¿Ha notado que su dificultad para respirar ha empeorado con el tiempo?",
        }

    def obtener_factores(self):
        return {
            "tabaquismo": "¿Fuma actualmente o ha fumado en el pasado?",
            "contacto_infectados": "¿Ha tenido contacto con personas infectadas?",
            "alergias": "¿Sufre de alergias respiratorias?",
            "enfermedades_cronicas": "¿Padece enfermedades crónicas (como diabetes o hipertensión)?",
            "exposicion_humo": "¿Está expuesto frecuentemente a polvo o humo?",
            "hacinamiento": "¿Vive en un lugar con muchas personas?",
            "inmunodepresion": "¿Tiene el sistema inmune debilitado?",
            "antecedentes_familiares": "¿Tiene antecedentes familiares de enfermedades respiratorias?",
            "infecciones_recientes": "¿Ha tenido infecciones virales recientemente?",
            "exposicion_laboral": "¿Está expuesto a gases o químicos en su trabajo?",
            "irritantes_ambientales": "¿Está expuesto a irritantes ambientales?",
            "uso_voz": "¿Usa mucho la voz en su trabajo o actividades?",
            "epoca_invierno": "¿Es temporada de invierno?"
        }

    def obtener_hallazgos(self):
        return {
            "pcr_positiva": "¿Tiene una prueba PCR positiva?",
            "radiografia_infiltrados": "¿Su radiografía muestra infiltrados?",
            "crepitantes": "¿El médico ha detectado crepitantes al auscultar?",
            "hiperinsuflacion": "¿Tiene signos de hiperinsuflación pulmonar?",
            "bacilos_acidorresistentes": "¿Se detectaron bacilos ácido-alcohol resistentes?",
            "inflamacion_cuerdas": "¿Hay inflamación visible en las cuerdas vocales?",
            "espiracion_prolongada": "¿Se ha detectado espiración prolongada en la exploración?",
            "mejora_broncodilatadores": "¿Mejora con broncodilatadores?",
            "espirometria_alterada": "¿Tiene alteraciones en la espirometría?",
            "cavernas_pulmonares": "¿Se observan cavernas pulmonares en las pruebas?",
            "sibilancias_persistentes": "¿Tiene sibilancias persistentes?",
            "test_influenza_positivo": "¿Tiene una prueba positiva de influenza?",
            "ruidos_bronquiales": "¿Se detectaron ruidos bronquiales difusos?"
        }

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaExperto(root)
    root.mainloop()
