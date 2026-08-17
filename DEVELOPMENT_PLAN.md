# Evaluación de Continuidad y Plan de Desarrollo para Credential Digger

## 1. Resumen Ejecutivo y Diagnóstico del Proyecto

### 1.1 Propuesta de Valor Única
Credential Digger destaca en el ecosistema de herramientas DevSecOps por abordar la principal falencia de los escáneres de secretos tradicionales (como GitLeaks, TruffleHog o SecretScanner): **la altísima tasa de falsos positivos**. Mediante la combinación de reglas de expresiones regulares, filtrado por patrones de rutas (`PathModel`) y modelos de Machine Learning / Transformers (`PasswordModel` con CodeBERT/RoBERTa), Credential Digger reduce drásticamente el esfuerzo manual de revisión de alertas.

Cuenta además con soporte multi-interfaz (CLI, librería Python, interfaz web Flask, extensión VS Code, hook de `pre-commit` e integración con pipelines de CI/CD como SAP Piper).

### 1.2 Evaluación de Continuidad con Presupuesto Cero ($0 USD)
El proyecto es **completamente viable y sostenible** sin presupuesto financiero, apalancándose en infraestructura y recursos open-source gratuitos:
- **CI/CD y Automatización**: GitHub Actions (gratuito para proyectos open-source).
- **Alojamiento y Distribución**: PyPI (paquetes Python), Docker Hub (imágenes de contenedores), GitHub Releases.
- **Documentación y Difusión**: GitHub Pages (sitios estáticos con MkDocs/Docusaurus).
- **Ejecución Local**: Inferencia de ML optimizada para CPU sin necesidad de servidores ni GPUs dedicadas en la nube.

### 1.3 Principales Desafíos y Puntos de Dolor Identificados
1. **Huella de Dependencias Pesada e Inestabilidad de Instalación**:
   - Dependencia directa de TensorFlow (`tensorflow==2.19.0`, `tf-models-official`, `transformers`), lo que genera instalaciones pesadas (>2 GB), tiempos de inicio lentos y frialdad de ejecución en entornos CI/CD.
   - Dependencia de C++ `hyperscan`, la cual restringe la ejecución nativa en entornos Windows y requiere compiladores del sistema (`build-essential`, `python3-dev`).
2. **Falta de Reconocimiento y Visibilidad en la Comunidad ("Underrated Product")**:
   - Falta de un **benchmark público formal** que demuestre cuantitativamente la superioridad en reducción de falsos positivos frente a alternativas populares.
   - Ausencia de una **GitHub Action oficial publicada en el GitHub Marketplace** para integración de un solo paso (`uses: SAP/credential-digger-action`).
   - Sin soporte directo de exportación en formato **SARIF** (Static Analysis Results Interchange Format), estándar para la pestaña de seguridad (*Code Scanning*) de GitHub y GitLab.

---

## 2. Opciones Estratégicas para el Plan de Desarrollo

A continuación se presentan 3 opciones estratégicas diseñadas para ejecutarse con **presupuesto cero** y alineadas con la motivación de dar al producto el reconocimiento técnico que merece.

---

### **Opción A: Optimización y Modernización del Core Técnico (Enfoque "Lightweight & Developer Experience")**

* **Objetivo**: Eliminar barreras de adopción técnica, reducir el peso del proyecto y hacer la herramienta ultra rápida y multiplataforma.
* **Componentes Clave**:
  1. **Migración a ONNX Runtime para Inferencia de ML**:
     - Convertir los modelos Transformers (CodeBERT/RoBERTa) de TensorFlow al formato **ONNX**.
     - Reemplazar `tensorflow` y `tf-models-official` por `onnxruntime` en CPU.
     - *Resultado*: Reducción del tamaño de dependencias de >2 GB a ~150 MB, velocidad de inferencia de 2x a 5x más rápida en entornos CI/CD cotidianos.
  2. **Compatibilidad Multiplataforma Completa (Soporte Windows Nativo)**:
     - Implementar una capa de abstracción para el motor de regex que permita fallback transparente entre `hyperscan`, `vectorscan` o el módulo `regex` de Python cuando no haya binarios C++ disponibles.
  3. **Exportador SARIF (Static Analysis Results Interchange Format)**:
     - Agregar opción `--format sarif` en el CLI y cliente Python para integrar los resultados directamente en la pestaña "Security / Code Scanning" de GitHub y GitLab.
  4. **Optimización de Contenedores Docker**:
     - Rediseñar el `Dockerfile` usando builds multietapa (*multi-stage builds*) para reducir el tamaño de la imagen final.

* **Costo**: $0 USD.
* **Impacto**: Experiencia de usuario ágil, instalación fluida en cualquier SO, integración nativa con herramientas modernas.

---

### **Opción B: Posicionamiento, Visibilidad y Ecosistema DevSecOps (Enfoque "Recognition & Community Growth")**

* **Objetivo**: Demostrar empíricamente la calidad del producto, masificar su uso en la comunidad open-source y posicionarlo como referente en reducción de falsos positivos.
* **Componentes Clave**:
  1. **Benchmark Público de Falsos Positivos**:
     - Crear un conjunto de datos público de pruebas (*Secret Detection Benchmark Dataset*) comparando Credential Digger vs GitLeaks vs TruffleHog.
     - Publicar un informe gráfico con métricas claras (Precisión, Recall, F1-Score, Tasa de Falsos Positivos) en el README y en artículos de divulgación.
  2. **GitHub Action Oficial en el GitHub Marketplace**:
     - Crear el repositorio de la acción `credential-digger-action` y publicarla en el Marketplace de GitHub para habilitar escaneos en 3 líneas de YAML.
  3. **Documentación Moderna e Interactiva**:
     - Desplegar en GitHub Pages una documentación estructurada usando **MkDocs Material** o **Docusaurus**, incluyendo guías paso a paso, casos de uso y ejemplos de integración.
  4. **Salida Interactiva en CLI y Reportes Locales**:
     - Mejorar la experiencia de consola utilizando `rich` (tablas formateadas, barras de progreso, paneles de resumen) y generación de reportes HTML/Markdown descargables.

* **Costo**: $0 USD.
* **Impacto**: Incremento exponencial en adopción, reconocimiento en la comunidad de ciberseguridad, mayor tracción en estrellas/contribuciones en GitHub.

---

### **Opción C: Inteligencia de Detección Avanzada y Era AI/LLM (Enfoque "Next-Gen AI & Smart Remediation")**

* **Objetivo**: Evolucionar el motor de ML incorporando capacidad de análisis contextual inteligente mediante LLMs locales/gratuitos y sugerencias de remediación.
* **Componentes Clave**:
  1. **Integración con Small Language Models (SLMs) y Embeddings Locales**:
     - Permitir la validación contextual de secretos dudosos utilizando motores de inferencia local sin costo (ej. soporte para Ollama, Llamafile o embeddings ligeros de Hugging Face).
  2. **Reglas Extendidas para Servicios Cloud/SaaS Modernos**:
     - Actualizar la biblioteca de reglas (`rules.yml`) con patrones recientes para tokens de IA (OpenAI, Anthropic, Cohere), plataformas Cloud (AWS IAM, GCP Service Accounts, Azure Tokens) y SaaS (Slack, Discord, GitHub Fine-Grained Tokens).
  3. **Asistente de Remediación y Rotación de Secretos**:
     - Generar recomendaciones automáticas sobre el nivel de riesgo de la credencial filtrada y pasos sugeridos para su revocación/rotación.
  4. **Filtro Avanzado por Entropía y Contexto Sintáctico**:
     - Combinar el análisis de entropía de Shannon con el AST (*Abstract Syntax Tree*) del código fuente para ignorar variables de prueba (`dummy`, `test_key`, `example_token`).

* **Costo**: $0 USD.
* **Impacto**: Posicionamiento como herramienta pionera de análisis estático asistido por IA local (privacidad garantizada y sin costos de API).

---

## 3. Matriz Comparativa de Opciones

| Criterio | Opción A: Core Lightweight | Opción B: Visibilidad y DevSecOps | Opción C: Next-Gen AI |
| :--- | :--- | :--- | :--- |
| **Enfoque Principal** | Rendimiento y DX | Adopción y Reconocimiento | Innovación Técnica |
| **Esfuerzo de Desarrollo** | Medio | Medio | Medio-Alto |
| **Impacto en Reconocimiento** | Alto (Soporte SARIF / Windows) | **Máximo** (Marketplace + Benchmark) | Alto (Factor Innovación) |
| **Costo Financiero** | **$0 USD** | **$0 USD** | **$0 USD** |
| **Complejidad de Mantenimiento**| Baja (Menos dependencias) | Baja | Media |

---

## 4. Hoja de Ruta Recomendada (Roadmap Sugerido)

Para maximizar los resultados sin presupuesto, se recomienda un enfoque híbrido por fases:

1. **Fase 1 (Corto Plazo / Mes 1-2)**:
   - Implementar formato de salida **SARIF** y exportador.
   - Publicar la **GitHub Action oficial** en GitHub Marketplace.
   - Migrar el modelo ML a **ONNX Runtime** para aligerar instalaciones.
2. **Fase 2 (Mediano Plazo / Mes 3-4)**:
   - Construir y publicar el **Benchmark Comparativo de Falsos Positivos**.
   - Desplegar la documentación renovada en GitHub Pages (MkDocs).
   - Añadir reglas para tokens Cloud/SaaS modernos.
3. **Fase 3 (Largo Plazo / Mes 5-6)**:
   - Incorporar validación contextual con SLMs locales (Ollama/ONNX).
   - Mejorar la CLI con soporte interactivo `rich` y reportes HTML.

---

## 5. Guía de Ejecución Paso a Paso para Agentes de Inteligencia Artificial (AI Agents)

Esta sección contiene instrucciones estructuradas, deterministas y de bajo consumo de tokens para que **Agentes de IA** ejecuten autónomamente las tareas de la Hoja de Ruta aprobada.

### 5.1 Principios de Diseño e Interpretación para Agentes
- **Token Efficiency**: Instrucciones estructuradas mediante esquemas directos y comandos sin prosa redundante.
- **Deterministic Verification**: Cada acción incluye comandos de prueba ejecutables en la terminal para confirmar la correcta implementación.
- **Strict File Contracts**: Rutas relativas explícitas y firmas de funciones estandarizadas.

---

### 5.2 FASE 1: Core Ligero, Formato SARIF y GitHub Action (Mes 1-2)

#### Tarea 1.1: Implementación del Exportador SARIF v2.1.0
* **Objetivo**: Permitir la exportación de descubrimientos a formato SARIF estandarizado.
* **Archivos Afectados**:
  - Crear: `src/credentialdigger/export/sarif_exporter.py`
  - Modificar: `src/credentialdigger/cli/export.py` y `src/credentialdigger/client.py`
  - Crear Test: `tests/unit_tests/test_sarif_exporter.py`
* **Contrato de Código**:
  ```python
  # src/credentialdigger/export/sarif_exporter.py
  import json

  def export_to_sarif(discoveries: list, rules: list = None) -> dict:
      """
      Transforms Credential Digger discoveries into a SARIF v2.1.0 JSON dictionary.
      Schema URL: https://json.schemastore.org/sarif-2.1.0.json
      """
      # Return valid SARIF 2.1.0 structure
  ```
* **Paso a Paso del Agente**:
  1. Crear `src/credentialdigger/export/sarif_exporter.py` con el esquema SARIF 2.1.0 conteniendo `version: "2.1.0"`, `$schema`, y el objeto `runs` con la herramienta `Credential Digger`.
  2. Mapear cada `discovery` a un objeto `result` dentro de `runs[0].results` especificando `ruleId`, `message.text`, y `locations[0].physicalLocation`.
  3. Extender el CLI en `src/credentialdigger/cli/export.py` para aceptar el argumento `--format sarif` y escribir el archivo `.sarif`.
  4. Escribir test unitario en `tests/unit_tests/test_sarif_exporter.py` validando la estructura del JSON exportado.
* **Comando de Verificación Estándar**:
  ```bash
  python3 -m pytest tests/unit_tests/test_sarif_exporter.py
  ```

---

#### Tarea 1.2: Migración de Inferencia ML de TensorFlow a ONNX Runtime
* **Objetivo**: Reemplazar `tensorflow` por `onnxruntime` en `PasswordModel` para reducir el peso de instalación a ~150MB.
* **Archivos Afectados**:
  - Modificar: `src/credentialdigger/models/password_model.py`
  - Modificar: `requirements.txt` (reemplazar `tensorflow` por `onnxruntime`)
* **Contrato de Código**:
  ```python
  # src/credentialdigger/models/password_model.py
  import onnxruntime as ort
  from transformers import AutoTokenizer

  class PasswordModel(BaseModel):
      def __init__(self, model_path="SAP/password-model-onnx", tokenizer_path="microsoft/codebert-base-mlm"):
          self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
          self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
  ```
* **Paso a Paso del Agente**:
  1. Convertir el checkpoint del modelo RoBERTa/CodeBERT a `model.onnx` usando `optimum-cli` o script de exportación ONNX.
  2. Actualizar `PasswordModel` para usar `ort.InferenceSession` en lugar de `TFRobertaForSequenceClassification`.
  3. Reemplazar la predicción `self.model.predict(data)` por `self.session.run(None, inputs)`.
  4. Actualizar `requirements.txt` eliminando `tensorflow` y `tf-models-official`, añadiendo `onnxruntime`.
* **Comando de Verificación Estándar**:
  ```bash
  python3 -m pytest tests/unit_tests/test_scans.py
  ```

---

#### Tarea 1.3: Creación de la GitHub Action Oficial (`action.yml`)
* **Objetivo**: Proveer una GitHub Action reutilizable para escaneo en pipelines CI/CD.
* **Archivos Afectados**:
  - Crear: `action.yml` en la raíz del repositorio.
* **Contrato de Configuración (`action.yml`)**:
  ```yaml
  name: 'Credential Digger Scan'
  description: 'Scan code for hardcoded secrets and filter false positives with ML'
  inputs:
    repo_path:
      description: 'Target repository path or URL'
      required: true
      default: '.'
    export_sarif:
      description: 'Path to save output SARIF file'
      required: false
      default: 'credential-digger-results.sarif'
  runs:
    using: 'composite'
    steps:
      - shell: bash
        run: |
          pip install --no-cache-dir .
          credentialdigger add_rules --sqlite /tmp/cd.db ui/backend/rules.yml
          credentialdigger scan ${{ inputs.repo_path }} --sqlite /tmp/cd.db --models PathModel PasswordModel --export ${{ inputs.export_sarif }} --format sarif
  ```
* **Comando de Verificación Estándar**:
  ```bash
  actionlint action.yml || echo "Action syntax valid"
  ```

---

### 5.3 FASE 2: Benchmark Público y Renovación de Documentación (Mes 3-4)

#### Tarea 2.1: Dataset de Prueba y Script de Benchmark Comparativo
* **Objetivo**: Generar métricas públicas comparando Credential Digger frente a GitLeaks y TruffleHog.
* **Archivos Afectados**:
  - Crear: `tests/benchmark/benchmark_runner.py`
  - Crear: `tests/benchmark/dataset.json` (100 muestras de secretos reales y 100 falsos positivos etiquetados).
* **Métricas a Calcular**:
  - $\text{Precisión} = \frac{TP}{TP + FP}$
  - $\text{Recall} = \frac{TP}{TP + FN}$
  - $\text{Tasa de Reducción de Falsos Positivos} = \frac{FP_{\text{GitLeaks}} - FP_{\text{CredentialDigger}}}{FP_{\text{GitLeaks}}} \times 100\%$
* **Comando de Verificación Estándar**:
  ```bash
  python3 tests/benchmark/benchmark_runner.py --dataset tests/benchmark/dataset.json
  ```

---

#### Tarea 2.2: Actualización de Reglas para Servicios Cloud/SaaS Modernos
* **Objetivo**: Expandir patrones de detección para nuevas claves de API.
* **Archivos Afectados**:
  - Modificar: `ui/backend/rules.yml`
* **Patrones a Agregar**:
  - OpenAI API Key (`sk-[a-zA-Z0-9]{32,}`)
  - Anthropic API Key (`sk-ant-api[0-9]{2}-[a-zA-Z0-9_-]{86,}`)
  - GitHub Fine-Grained Personal Access Token (`github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}`)
  - AWS Secret Access Key (`[A-Za-z0-9/+=]{40}`)
* **Comando de Verificación Estándar**:
  ```bash
  python3 -m pytest tests/unit_tests/test_file_scanner.py
  ```

---

### 5.4 FASE 3: Next-Gen AI y Remediación Inteligente (Mes 5-6)

#### Tarea 3.1: Módulo de Detección por Entropía y AST (Abstract Syntax Tree)
* **Objetivo**: Filtrar asignaciones de variables dummy/test mediante análisis del AST del lenguaje.
* **Archivos Afectados**:
  - Crear: `src/credentialdigger/models/ast_model.py`
  - Modificar: `src/credentialdigger/models/model_manager.py`
* **Paso a Paso del Agente**:
  1. Analizar si la línea del hallazgo pertenece a una prueba o variable mock (`test_*`, `mock_*`, `dummy_*`, `example_*`).
  2. Calcular la entropía de Shannon del token extraído ($H(X) = -\sum P(x_i) \log_2 P(x_i)$).
  3. Marcar como `false_positive` si la entropía es $< 3.0$ y está contenida en un contexto de test AST.
* **Comando de Verificación Estándar**:
  ```bash
  python3 -m pytest tests/unit_tests/
  ```

---

### 5.5 Lista de Verificación General para el Agente (Checklist de Finalización)
Antes de finalizar cualquier tarea de la hoja de ruta, el Agente de IA **debe ejecutar**:
1. `python3 -m pytest tests/unit_tests` (Asegurar que no existan regresiones).
2. `git status` (Verificar la limpieza del directorio de trabajo).
3. Confirmar que la modificación cumple con el principio de **$0 costos de infraestructura externa**.
