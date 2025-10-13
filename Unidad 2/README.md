Pasos mínimos para instalar PGMPY y ejecutar el programa

1) Actualizar pip y herramientas:

```powershell
python -m pip install --upgrade pip setuptools wheel
```

2) Instalar dependencias binarias (ayuda en Windows):

```powershell
python -m pip install numpy scipy pandas networkx
```

3) Instalar pgmpy:

```powershell
python -m pip install pgmpy==1.0.0
```

4) Alternativa con conda (si pip falla):

```powershell
conda install -c conda-forge pgmpy
```

5) Verificar instalación:

```powershell
python -c "import pgmpy; print(pgmpy.__version__)"
```

6-. ejecutar interfaz


