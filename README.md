# Modelos y Simulación

# Los omnibus

Una empresa de viajes interurbanos tiene un recorrido como el siguiente:

Las distancias en cada tramo son las de la tabla siguiente, donde se indica la velocidad esperada en cada tramo, aunque hay una baja probabilidad de que se encuentre mayor tránsito. Las velocidades de cada tramo son independientes de los demás tramos:

| Tramo | Distancia (km) | Velocidad esperada (km/h) | Velocidad esperada con P=0,2 (km/h) | Velocidad esperada P=0,1 (km/h) |
|------|------:|------:|------:|------:|
| 1 | 3 | 30 | 40 | 20 |
| 2 | 5 | 40 | 45 | 30 |
| 3 | 5 | 40 | 50 | 40 |
| 4 | 1 | 30 | 40 | 10 |
| 5 | 4 | 40 | 40 | 40 |
| 6 | 2 | 10 | 30 | 40 |
| 7 | 5 | 40 | 45 | 30 |
| 8 | 10 | 30 | 40 | 60 |
| 9 | 20 | 50 | 55 | 40 |
| 10 | 5 | 30 | 30 | 30 |
| 11 | 1 | 30 | 35 | 30 |
| 12 | 1 | 30 | 35 | 20 |
| 13 | 1 | 30 | 35 | 10 |

Los semáforos tienen las siguientes características, según modelo:

| Modelo | % tiempo verde | % tiempo rojo | % tiempo amarillo |
|---------|---------:|---------:|---------:|
| A (1, 2, 3) | 40 | 50 | 10 |
| B (4, 6, 8) | 30 | 60 | 10 |
| C (5, 7) | 60 | 30 | 10 |

Si el transporte encuentra un semáforo rojo tiene una demora de 1 minuto.

Si está en amarillo, un 50% de las veces puede pasar igual, por lo que no se afecta su recorrido, pero si nó pierde el ciclo completo del semáforo: frenar, esperar, acelerar, que consume 2 minutos.

---

# Modelos y Simulación

En el cruce de ferrocarril el conductor tiene una probabilidad del 20% de encontrar la barrera baja, y en ese caso los tiempos de espera son de 3 minutos el 60% de las veces, de 1,5 minutos el 30% de las veces y de 5 minutos el 10% de las veces.

Las paradas tienen las siguientes demoras, en función de la probabilidad de personas que estén esperando y/o que necesiten bajar en ese lugar:

| Parada | P = 0,4 | P = 0,3 | P = 0,2 | P = 0,2 |
|---------|---------|---------|---------|---------|
| 1 | 1 min | 2 min | 3 min | 4 min |
| 2 | 0,5 | 2 min | 3 min | 4 min |
| 3 | 0 min | 1 min | 2 min | 3 min |
| 4 | 3 min | 4 min | 5 min | 6 min |

Simulando 1000 viajes establezca un horario para el servicio, y con un alfa de 0,05 los tiempos más cortos y más largos del trayecto.
