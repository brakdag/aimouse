# Guía de Despliegue e Implantación: Neural Mouse Interface (NMI)

Este documento contiene las instrucciones críticas para integrar el SDK de NMI en el software de control del LLM.

## 🚀 1. Instalación Rápida

Una vez copiada la carpeta del proyecto en el entorno de destino, instale el paquete en modo editable para asegurar que todas las dependencias (`mss`, `pynput`, `Pillow`, `onnxruntime`, etc.) se configuren correctamente:

```bash
pip install -e .
```

## 🧠 2. Verificación del Modelo (El Cerebro)

El sistema depende de un modelo neuronal pre-entrenado para generar movimientos orgánicos.
- **Ruta por defecto:** `models/elite_model.onnx`.
- **Importante:** Asegúrese de que el archivo `.onnx` esté presente en la carpeta `models/`.
- Si el modelo tiene un nombre distinto, instancie la API especificando la ruta:
  `nmi = NeuralMouseInterface(model_path="models/mi_modelo_especifico.onnx")`.

## 🖱️ 3. Permisos del Sistema Operativo (El Cuerpo)

Dado que el SDK controla el hardware del ratón físicamente, el sistema operativo puede bloquear las acciones por seguridad:
- **Linux (Wayland/X11):** Puede requerir permisos de administrador o configuración de accesibilidad.
- **macOS:** Es obligatorio otorgar permisos de "Accesibilidad" a la aplicación o terminal que ejecute el script en `Ajustes del Sistema > Privacidad y Seguridad > Accesibilidad`.
- **Windows:** Generalmente funciona sin restricciones, a menos que haya un antivirus bloqueando la simulación de entrada.

## 👁️ 4. Integración con el LLM (La Vista)

Para que el LLM pueda navegar la pantalla, debe entender el **Encoder de Colores Recursivo**. 

**Acción Obligatoria:**
Copie el resultado de la función `nmi.get_vision_guide()` y péguelo directamente en el **System Prompt** del LLM. Sin esta guía, el LLM verá los tintes de color pero no sabrá cómo traducirlos a coordenadas $[X, Y]$.

## 🔄 5. Flujo de Trabajo Recomendado (Ciclo de Turnos)

Para maximizar la eficiencia, implemente el flujo de "Turnos":

1. **Captura Inicial:** Llame a `nmi.capture_and_encode()` $ightarrow$ Envíe la imagen al LLM.
2. **Decisión:** El LLM analiza la imagen y devuelve un `rect(x, y, w, h)`.
3. **Ejecución:** Llame a `nmi.perform_action(x, y, w, h)`.
   - El sistema moverá el ratón orgánicamente.
   - Ejecutará el clic al llegar al objetivo.
   - Esperará 0.5s a que la UI reaccione.
   - Capturará la nueva pantalla automáticamente.
4. **Retroalimentación:** El LLM recibe la imagen del "después de" y decide el siguiente paso.

## 📂 6. Mapa de la Estructura

```text
/proyecto-nmi
├── models/               <-- Archivos .onnx (Pesos del Elite)
├── src/
│   ├── common/
│   │   ├── vision_encoder.py  <-- Lógica de Quadtree de colores
│   │   ├── screen_manager.py  <-- Captura en RAM (mss)
│   │   └── vision_tool.py     <-- Procesamiento y Base64
│   ├── inference/
│   │   ├── api.py             <-- Punto de entrada único (Fachada)
│   │   ├── engine.py          <-- Ejecución del MLP
│   │   └── actuator.py        <-- Control físico del ratón
│   └── training/             <-- Entorno de evolución (Opcional)
├── pyproject.toml        <-- Definición de dependencias
└── INSTALL.md            <-- Guía rápida de instalación
```