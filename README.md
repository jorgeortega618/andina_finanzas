# 📊 Dashboard Financiero - Distribuciones Andina Comercial S.A.S. (2021–2025)

Aplicación interactiva desarrollada en **Python** con **Streamlit** y **Plotly** para el análisis financiero avanzado de la empresa **Distribuciones Andina Comercial S.A.S.**, diseñada bajo estándares de presentación ejecutiva para la alta dirección (C-Suite).

---

## 🚀 Características Principales

1. **📊 Resumen Ejecutivo (C-Suite):**
   - Tarjetas KPI dinámicas con variaciones interanuales (YoY) para Ventas, EBITDA, Margen EBITDA, Utilidad Neta y Flujo de Caja Libre (FCF).
   - Trayectoria de crecimiento frente a evolución de márgenes.
   - Ciclo de Conversión de Efectivo (CCC) y estructura de financiamiento.

2. **📈 Rentabilidad & Modelo DuPont:**
   - Análisis de ROE, ROA y ROIC.
   - Descomposición piramidal DuPont de 3 factores (Margen Neto $\times$ Rotación de Activos $\times$ Multiplicador de Capital).
   - Cascada de pérdidas y ganancias (Waterfall P&L).

3. **💧 Liquidez & Ciclo de Efectivo:**
   - Razón Corriente, Prueba Ácida y Cobertura de Efectivo.
   - Capital de Trabajo Neto Operativo (KTNO) y días de calle (DSO, DIO, DPO).

4. **⚖️ Endeudamiento & Solvencia:**
   - Deuda financiera bruta vs. neta, ratios Deuda/EBITDA y cobertura de intereses.

5. **💵 Flujo de Caja & Creación de Valor:**
   - Flujo de Efectivo por actividades (Operación, Inversión, Financiación).
   - Análisis de Autofinanciamiento vs. Pago de Dividendos.
   - Valor Económico Agregado (EVA) estimado.

6. **📑 Estados Financieros Detallados:**
   - Balance General, Estado de Resultados y Estado de Flujo de Efectivo completos.
   - Matriz de ratios financieros históricos y opción de descarga en CSV.

7. **🎯 Simulador de Sensibilidad (What-If):**
   - Proyección dinámica de variaciones en ventas, márgenes y días de cartera (DSO) con impacto en P&L y caja.

---

## 🛠️ Instalación y Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/jorgeortega618/andina_finanzas.git
   cd andina_finanzas
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   ```bash
   python -m streamlit run app.py
   ```

4. Abrir en el navegador: `http://localhost:8501`

---

## 📁 Estructura del Proyecto

```text
andina_finanzas/
├── app.py                     # Código principal del dashboard en Streamlit
├── requirements.txt           # Dependencias requeridas
├── .gitignore                 # Archivos excluidos del control de versiones
├── README.md                  # Documentación del proyecto
└── archivos/                  # Estados financieros y caso de estudio
    ├── balance_general.xlsx
    ├── estado_de_resultados.xlsx
    ├── estado_flujo_efectivo.xlsx
    └── Caso Distribuciones Andina Comercial SAS.docx
```
