# Documento de Intención: El Sistema Motor del Conocimiento

## 🌟 La Visión: De la Sabiduría a la Acción

En los años 90, la "abuela" era el oráculo del hogar; la persona a la que acudíamos cuando no sabíamos cómo resolver un problema, la fuente de sabiduría práctica y conocimiento acumulado. Hoy en día, la Inteligencia Artificial ha asumido ese rol. El LLM es la nueva "abuela" a la que le preguntamos todo lo que desconocemos.

Sin embargo, hasta ahora, esta sabiduría ha estado atrapada en una caja de texto. Tiene la capacidad de razonar, planificar y comprender, pero carece de "manos". 

**El objetivo de este proyecto es darle manos a la IA.**

Queremos que el LLM no solo nos diga cómo hacer las cosas, sino que pueda interactuar con el mundo digital de la misma forma que lo haría un ser humano: moviendo el mouse, arrastrando ventanas y haciendo click en botones, pero con la precisión y la estrategia de una inteligencia superior.

## 🏗️ La Arquitectura del Movimiento

Para lograr esto, hemos implementado una separación jerárquica entre la razón y la ejecución:

### 1. La Capa Estratégica (El Cerebro - LLM)
El LLM actúa como el comandante. No se encarga de los píxeles ni de los frames, sino de los objetivos. Su función es:
- Analizar la pantalla.
- Definir un objetivo táctico (un `Rect` en la pantalla).
- Decidir la acción final (Click, Drag, Hold).

### 2. La Capa Táctica (El Sistema Motor - Modelo Elite)
El Modelo Elite es el "driver" biológico. Es una red neuronal evolucionada para convertir un objetivo abstracto en movimiento físico orgánico. Sus pilares son:
- **Navegación Sensorial**: Utiliza una brújula de ángulo relativo y un sensor de distancia para orientarse.
- **Cinemática Orgánica**: Se mueve mediante rotación y empuje, evitando las líneas rectas robóticas que disparan los sistemas anti-bot.
- **Protocolo de Confirmación (`arrived`)**: El modelo no solo se mueve, sino que "siente" cuando ha llegado. Al activar la señal de llegada, le notifica al LLM: *"He alcanzado el objetivo, puedes ejecutar la acción"*.

## 🎯 El Objetivo Final

Queremos habilitar la capacidad de realizar tareas complejas de forma fluida:
- **Arrastrar y Soltar**: El LLM marca el origen $\rightarrow$ el Elite navega y llega $\rightarrow$ el LLM presiona $\rightarrow$ el LLM marca el destino $\rightarrow$ el Elite navega y llega $\rightarrow$ el LLM suelta.
- **Interacción Humana**: Que el movimiento sea tan natural que sea indistinguible de un usuario real, permitiendo que la IA opere software complejo sin ser detectada ni bloquearse.

**Estamos construyendo el puente entre el pensamiento y la acción. Estamos haciendo que la "abuela del conocimiento" pueda finalmente usar el mouse.**