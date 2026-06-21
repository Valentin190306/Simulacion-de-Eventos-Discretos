# Documentación del Simulador — Los Ómnibus

**Materia:** Modelos, Simulación y Teoría de la Decisión  
**Archivo:** `simulacion_omnibus.py`

---

## 1. Descripción del problema

Una empresa de viajes interurbanos realiza un recorrido compuesto por **13 tramos** consecutivos. El tiempo total de un viaje es la suma de:

- Tiempo de circulación por cada tramo (depende de la distancia y la velocidad sorteada)
- Demoras en **8 semáforos** distribuidos a lo largo del recorrido
- Demora en **1 cruce ferroviario**
- Demoras en **4 paradas** de pasajeros

El objetivo es simular **1000 viajes** para establecer un horario de servicio y determinar, con un nivel de significación **α = 0,05**, los tiempos más cortos y más largos esperables del trayecto.

---

## 2. Datos del modelo

### 2.1 Tramos

Cada tramo $i$ tiene una distancia $d_i$ (km) y tres velocidades posibles (km/h):

| Concepto | Probabilidad |
|---|---|
| Velocidad normal $v_{i,0}$ | $P = 0,7$ |
| Velocidad con tránsito moderado $v_{i,1}$ | $P = 0,2$ |
| Velocidad con tránsito intenso $v_{i,2}$ | $P = 0,1$ |

| Tramo | $d_i$ (km) | $v_{i,0}$ | $v_{i,1}$ | $v_{i,2}$ |
|------:|-----------:|----------:|----------:|----------:|
| 1  | 3  | 30 | 40 | 20 |
| 2  | 5  | 40 | 45 | 30 |
| 3  | 5  | 40 | 50 | 40 |
| 4  | 1  | 30 | 40 | 10 |
| 5  | 4  | 40 | 40 | 40 |
| 6  | 2  | 10 | 30 | 40 |
| 7  | 5  | 40 | 45 | 30 |
| 8  | 10 | 30 | 40 | 60 |
| 9  | 20 | 50 | 55 | 40 |
| 10 | 5  | 30 | 30 | 30 |
| 11 | 1  | 30 | 35 | 30 |
| 12 | 1  | 30 | 35 | 20 |
| 13 | 1  | 30 | 35 | 10 |

**Tiempo de circulación del tramo $i$:**

$$t_{\text{tramo},i} = \frac{d_i}{v_i} \times 60 \text{ (minutos)}$$

donde $v_i$ se sortea de la distribución discreta $\{(0,7; v_{i,0}),\; (0,2; v_{i,1}),\; (0,1; v_{i,2})\}$.

### 2.2 Semáforos

Existen 8 semáforos, clasificados en 3 modelos según su distribución de estados:

| Modelo | Semáforos | Verde | Rojo | Amarillo |
|:------:|:---------:|:-----:|:----:|:--------:|
| A | 1, 2, 3 | 40% | 50% | 10% |
| B | 4, 6, 8 | 30% | 60% | 10% |
| C | 5, 7 | 60% | 30% | 10% |

**Demoras según el estado:**

- **Rojo**: demora fija de **1 minuto**
- **Amarillo**: 50% de probabilidad de pasar sin demora; 50% de probabilidad de perder el ciclo completo (**2 minutos**)
- **Verde**: sin demora

Por lo tanto, la demora esperada para un semáforo del modelo $m$ es:

$$E[D_{\text{sem},m}] = p_{\text{rojo}} \times 1 + p_{\text{amarillo}} \times \Big(0,5 \times 0 + 0,5 \times 2\Big) = p_{\text{rojo}} + p_{\text{amarillo}}$$

### 2.3 Cruce ferroviario

- **Probabilidad de encontrar la barrera baja**: 20%
- Cuando la barrera está baja, las demoras posibles son:

| Demora | Probabilidad |
|:------:|:------------:|
| 3,0 min | 60% |
| 1,5 min | 30% |
| 5,0 min | 10% |

**Demora esperada por cruce:**

$$E[D_{\text{ffcc}}] = 0,2 \times \big(0,6 \times 3,\!0 + 0,3 \times 1,\!5 + 0,1 \times 5,\!0\big)$$

### 2.4 Paradas

Hay 4 paradas, cada una con 4 demoras posibles según la afluencia de pasajeros. La distribución de probabilidad es común a todas:

$$P = \{0,4;\; 0,3;\; 0,2;\; 0,1\}$$

| Parada | Demora 1 ($P=0,4$) | Demora 2 ($P=0,3$) | Demora 3 ($P=0,2$) | Demora 4 ($P=0,1$) |
|:------:|:-------------------:|:-------------------:|:-------------------:|:-------------------:|
| 1 | 1,0 min | 2,0 min | 3,0 min | 4,0 min |
| 2 | 0,5 min | 2,0 min | 3,0 min | 4,0 min |
| 3 | 0,0 min | 1,0 min | 2,0 min | 3,0 min |
| 4 | 3,0 min | 4,0 min | 5,0 min | 6,0 min |

> **Nota:** El encabezado de la tabla original mostraba $P=0,2$ para el último valor, pero las cuatro probabilidades deben sumar 1,0. Se interpreta que el valor correcto es $P=0,1$, consistente con una distribución de probabilidad válida.

### 2.5 Secuencia del recorrido

El orden de eventos del recorrido se define explícitamente para reflejar la estructura del viaje:

```
T1 → S1 → T2 → S2 → T3 → P1 → T4 → S3 → T5 → P2 →
T6 → S4 → T7 → S5 → T8 → P3 → T9 → S6 → T10 → S7 →
T11 → F → S8 → T12 → P4 → T13
```

Donde:
- T = tramo (1 a 13)
- S = semáforo (1 a 8)
- P = parada (1 a 4)
- F = cruce ferroviario

---

## 3. Método de simulación

### 3.1 Simulación Monte Carlo

Se utiliza el método de **Monte Carlo**: se realizan $N = 1000$ réplicas independientes del viaje completo, donde cada réplica sortea los valores aleatorios de todas las variables involucradas (velocidades, estados de semáforos, demoras de cruce y paradas).

**Semilla de aleatoriedad:** `seed = 42` para garantizar reproducibilidad de los resultados.

### 3.2 Algoritmo de un viaje

```
función simular_viaje():
    tiempo_total ← 0
    para cada evento (tipo, id) en RECORRIDO:
        si tipo = 'T':  tiempo_total += d_id / v_sortear(id) × 60
        si tipo = 'S':  tiempo_total += demora_semáforo(id)
        si tipo = 'P':  tiempo_total += demora_parada(id)
        si tipo = 'F':  tiempo_total += demora_ffcc()
    retornar tiempo_total
```

### 3.3 Muestreo de distribuciones discretas

Dada una distribución discreta $\{(p_1, x_1), (p_2, x_2), \dots, (p_k, x_k)\}$ con $\sum p_i = 1$, se muestrea mediante el método de la **transformada inversa**:

1. Generar $U \sim \mathcal{U}(0, 1)$
2. Hallar el menor $j$ tal que $\sum_{i=1}^{j} p_i > U$
3. Retornar $x_j$

Este método está implementado en la función `_muestrear()`.

---

## 4. Cálculos estadísticos

### 4.1 Estadísticos muestrales

Sea $\{x_1, x_2, \dots, x_N\}$ el conjunto de $N = 1000$ tiempos de viaje simulados.

**Media muestral:**

$$\bar{x} = \frac{1}{N} \sum_{i=1}^{N} x_i$$

**Desvío estándar muestral:**

$$s = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (x_i - \bar{x})^2}$$

Se utiliza $N-1$ (corrección de Bessel) para obtener un estimador insesgado de la varianza poblacional.

### 4.2 Percentiles (P5 y P95)

Los percentiles se calculan mediante interpolación lineal entre los valores ordenados. Con $\alpha = 0,05$:

- **P5** (tiempo más corto esperado): el valor por debajo del cual se encuentra el 5% de los viajes más rápidos.
- **P95** (tiempo más largo esperado): el valor por debajo del cual se encuentra el 95% de los viajes (o, equivalentemente, solo el 5% de los viajes supera este tiempo).

Estos percentiles definen un **intervalo central del 90%** para los tiempos de viaje.

### 4.3 Valor esperado analítico

Como validación del simulador, se calcula analíticamente el tiempo esperado por componente:

**Tramos:**

$$E[T_{\text{tramos}}] = 60 \times \sum_{i=1}^{13} \left[ 0,\!7 \frac{d_i}{v_{i,0}} + 0,\!2 \frac{d_i}{v_{i,1}} + 0,\!1 \frac{d_i}{v_{i,2}} \right] \text{ (minutos)}$$

**Semáforos:**

$$E[D_{\text{sem}}] = \sum_{s=1}^{8} \big( p_{\text{rojo},s} + p_{\text{amarillo},s} \big)$$

donde $p_{\text{rojo},s}$ y $p_{\text{amarillo},s}$ dependen del modelo del semáforo $s$.

**Cruce ferroviario:**

$$E[D_{\text{ffcc}}] = 0,\!2 \times \big( 0,\!6 \times 3,\!0 + 0,\!3 \times 1,\!5 + 0,\!1 \times 5,\!0 \big)$$

**Paradas:**

$$E[D_{\text{paradas}}] = \sum_{p=1}^{4} \big( 0,\!4 \times d_{p,1} + 0,\!3 \times d_{p,2} + 0,\!2 \times d_{p,3} + 0,\!1 \times d_{p,4} \big)$$

El **tiempo total esperado** es la suma de estos cuatro componentes:

$$E[T_{\text{total}}] = E[T_{\text{tramos}}] + E[D_{\text{sem}}] + E[D_{\text{ffcc}}] + E[D_{\text{paradas}}]$$

La comparación entre $E[T_{\text{total}}]$ y la media simulada $\bar{x}$ permite verificar que el simulador converge al valor teórico esperado.

---

## 5. Interpretación de resultados

### 5.1 Horario sugerido para el servicio

Se sugiere programar el servicio con una duración igual al **percentil 95** redondeado, de modo que el 95% de los viajes se completen dentro del tiempo programado y solo el 5% exceda el horario previsto.

Alternativamente, se puede usar la **media** redondeada como tiempo base y el rango P5–P95 como margen de variabilidad esperado.

### 5.2 Nivel de significación $\alpha = 0,05$

Con $\alpha = 0,05$:

- El **P5** representa el tiempo mínimamente esperable: solo el 5% de los viajes son más cortos.
- El **P95** representa el tiempo máximamente esperable: solo el 5% de los viajes son más largos.

Esto equivale a un intervalo central del $100\% \times (1 - \alpha) = 90\%$ para los tiempos de viaje.

---

## 6. Programación de horarios

### 6.1 Circuito cerrado

El recorrido simulado (13 tramos, 8 semáforos, 4 paradas, 1 cruce FFCC) forma un **circuito cerrado**: el vehículo parte de la terminal, completa el trayecto de 63 km, y regresa al mismo punto de origen. El tiempo simulado es, por lo tanto, un **Round Trip Time (RTT)** completo.

### 6.2 Criterio de selección del tiempo de ciclo

| Criterio | Tiempo | Viajes que exceden el horario |
|---|---|---|
| **Media** (~119 min) | 119 min | ≈50% |
| **P90** (~127 min) | 127 min | ≈10% |
| **P95** (~129 min) | 129 min | ≈5% |

Se adopta el **P95** como tiempo de ciclo por las siguientes razones:

- La documentación original (sección 5.1) recomienda usar P95 para programar el servicio: _el 95% de los viajes se completan dentro del tiempo programado y solo el 5% excede el horario previsto._
- Usar la media implicaría que la mitad de los viajes demoren más de lo previsto, generando **atrasos acumulativos** a lo largo del día: un bus que llega tarde a la terminal retrasa su siguiente salida, el intervalo entre unidades se distorsiona, y los pasajeros en la parada experimentan **esperas mayores a la frecuencia nominal**.
- Usar P95 **no retrasa el servicio**. Significa que el bus completa el circuito dentro del tiempo asignado el 95% de las veces, por lo que está disponible en terminal para su próxima salida programada. Los intervalos se mantienen estables durante todo el día, y el pasajero en cualquier parada ve un bus cada \(f\) minutos como está previsto.

### 6.3 Relación ciclo–frecuencia–flota–descanso

La cantidad de unidades necesarias se calcula como:

\[
\text{unidades} = \left\lceil \frac{\text{ciclo} + \text{descanso\_min}}{\text{frecuencia}} \right\rceil
\]

donde:

- **ciclo**: P95 del tiempo de viaje (RTT)
- **descanso\_min**: tiempo mínimo de descanso del conductor en terminal (default: 10 min)
- **frecuencia**: intervalo entre salidas consecutivas desde la terminal

Cada unidad opera en un **turno** de \( \text{turno} = \text{unidades} \times \text{frecuencia} \) minutos. Al completar el circuito, dispone de un **descanso real** de:

\[
\text{descanso\_real} = \text{turno} - \text{ciclo}
\]

que siempre es \(\geq \text{descanso\_min}\) por construcción.

**Ejemplo con P95 = 129 min y descanso\_min = 10 min:**

| Frecuencia | Unidades | Turno | Descanso real | Servicios/día (06:00–22:00) |
|---|---|---|---|---|
| 20 min | 7 | 140 min | 11 min | 48 |
| 30 min | 5 | 150 min | 21 min | 32 |
| 45 min | 4 | 180 min | 51 min | 22 |
| 60 min | 3 | 180 min | 51 min | 16 |

### 6.4 Ejemplo de horario (frecuencia 30 min, 5 unidades)

```
Unidad 1: 06:00 | 08:30 | 11:00 | 13:30 | 16:00 | 18:30 | 21:00
Unidad 2: 06:30 | 09:00 | 11:30 | 14:00 | 16:30 | 19:00 | 21:30
Unidad 3: 07:00 | 09:30 | 12:00 | 14:30 | 17:00 | 19:30
Unidad 4: 07:30 | 10:00 | 12:30 | 15:00 | 17:30 | 20:00
Unidad 5: 08:00 | 10:30 | 13:00 | 15:30 | 18:00 | 20:30
```

El intervalo en terminal de 21 min por vuelta permite al conductor descansar y absorber pequeñas demoras sin que el horario global se desvíe.

### 6.5 Generación automatizada

El script `generar_horario.py` calcula e imprime el horario completo para cualquier combinación de frecuencia y descanso mínimo, y genera un diagrama de Gantt de las unidades:

```bash
python generar_horario.py                          # default: 30 min, descanso 10 min
python generar_horario.py --frecuencia 20          # cada 20 min
python generar_horario.py --frecuencia 45 --descanso 15
python generar_horario.py --no-plot                # solo texto
```

---

## 7. Estructura del archivo `simulacion_omnibus.py`

| Sección | Líneas | Descripción |
|---------|:------:|-------------|
| Parámetros generales | 12–17 | Constantes $N$, $\alpha$, semilla |
| Datos del modelo | 19–82 | Definición de tramos, semáforos, paradas, cruce y recorrido |
| Funciones auxiliares | 84–127 | `_muestrear()`, `tiempo_tramo()`, `demora_semaforo()`, `demora_parada()`, `demora_ffcc()` |
| Simulación de un viaje | 129–142 | Bucle principal que recorre la secuencia de eventos |
| Validación analítica | 144–174 | Cálculo de $E[T]$ descompuesto por componentes |
| Ejecución principal | 176–218 | Generación de 1000 viajes, estadísticas y salida por consola |
| Visualización | 220–255 | Histograma y gráfico de barras de comparación analítico vs. simulado |
