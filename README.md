# 🌋 Pipeline ETL y Dashboard Analítico de Sismología en Chile

Solución end-to-end de ingeniería de datos para el análisis de sismicidad en Chile utilizando Python, SQLite y Streamlit.

---

## 🚀 Instrucciones de Ejecución

Sigue estos pasos en tu terminal (Git Bash, PowerShell o Símbolo del sistema) para ejecutar el proyecto en cualquier computadora:

### 1. Crear y activar el entorno virtual
* **En Git Bash / Mac / Linux:**
```bash
python -m venv venv
source venv/Scripts/activate

En PowerShell (Windows):
PowerShell

python -m venv venv
.\venv\Scripts\Activate.ps1

2. Instalar las librerías necesarias
Bash
pip install -r requirements.txt

3. Ejecutar la canalización ETL
Procesa el dataset CSV, aplica los criterios de calidad de datos y crea el repositorio analítico SQLite con sus vistas SQL:  

Bash
python src/etl.py

4. Lanzar el Dashboard

Bash

streamlit run app.py
