import random
import json
import time
import random

class Color:
    AMARILLO = "\033[93m"
    MAGENTA = "\033[95m"
    NEGRO = "\033[30m"
    ROJO = "\033[91m"
    VERDE = "\033[92m"
    BLANCO = "\033[97m"
    AZUL = "\033[38;5;45m"

    def estiloTexto(texto, color):
        return f"{color}{texto}{Color.BLANCO}"

class Estado:
    def __init__(self, posicion, problema=None):
        self.posicion = posicion
        self.problema = problema

    #Acciones de movimiento del robot
    def acciones(self, accion):
        
        if accion==0: # Arriba
            nueva_pos = ((self.posicion[0] - 1,self.posicion[1]))
        elif accion==1: # Derecha
            nueva_pos = ((self.posicion[0], self.posicion[1] + 1))
        elif accion==2: # Abajo
            nueva_pos = ((self.posicion[0] + 1,self.posicion[1]))
        elif accion==3: #Izquierda
            nueva_pos = ((self.posicion[0], self.posicion[1] - 1))
        
        # Verificar límites y bloqueados
        if (0 <= nueva_pos[0] < self.problema.nfilas and 0 <= nueva_pos[1] < self.problema.ncols 
            and list(nueva_pos) not in self.problema.bloqueados):
            return Estado(nueva_pos)
        else:
        # Si la nueva posición está fuera de los límites o es bloqueada, devolver el estado actual
            return self

class Problema:
    def __init__(self, problema):
        with open(problema, 'r') as file:
            self.nuevo_diccionario = json.load(file)

        self.nfilas=self.nuevo_diccionario["city"]["rows"]
        self.ncols=self.nuevo_diccionario["city"]["columns"]
        self.bloqueados=self.nuevo_diccionario["city"]["blocked"]
        self.partida=self.nuevo_diccionario["departure"]
        self.peligro=self.nuevo_diccionario["dangers"]
        self.peligro_fatal=self.nuevo_diccionario["fatal_dangers"]
        self.atrapados=self.nuevo_diccionario["trapped"]

    
    def finales(self):
        lista_buenos = [[fila, columna] for fila, columna, recompensa in self.atrapados]
        lista_malos = [[fila, columna] for fila, columna, recompensa in self.peligro_fatal]

        return lista_buenos, lista_malos


class Agente():
    def __init__(self, problema):
        self.problema = problema


    def QTabla(self):
        QTabla = [[[0.0 for _ in range(4)] for _ in range(self.problema.ncols)] for _ in range(self.problema.nfilas)]

        for objetivo in self.problema.atrapados:
            fila, columna, recompensa = objetivo
            QTabla[fila][columna] = [recompensa]

        for muerte in self.problema.peligro_fatal:
            fila, columna, recompensa = muerte
            QTabla[fila][columna] = [recompensa]

        return QTabla
    
    def qLearning(self, gamma, r, alfa, epsilon, iteraciones):
        inicio_tiempo = time.time()
        QTabla = self.QTabla() # Define la función de valor inicial y todos los estados de la tabla
        finales_buenos, finales_malos = self.problema.finales() 

        for iteracion in range(iteraciones):
            estado_actual = Estado(posicion=self.problema.partida, problema=self.problema)
            camino = {}
            recompensaTotal = 0


            while list(estado_actual.posicion) not in finales_buenos and list(estado_actual.posicion) not in finales_malos:

                if random.uniform(0, 1) < epsilon: # Probabilidad de exploración
                    #   Exploración, vamos a una posición aleatoria
                    # numeros = [numero for numero in range(4) if numero != QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]].index(max(QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]]))]
                    accion = random.choice([0,1,2,3]) # Accion de acuerdo a una Politica aleatoria
                else:
                    #   Explotación, vamos a la posición con más valor
                    accion = QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]].index(max(QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]]))
                    
                #  Obtener la nueva posición
                if 0 <= accion <= 3:
                    nueva_pos = estado_actual.acciones(accion).posicion

                    recompensa = self.recompensa(nueva_pos[0], nueva_pos[1], r) # Recompensa de la nueva posición
                    recompensaTotal += recompensa

                    #Q-Learning
                    QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]][accion] = (1 - alfa) * QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]][accion] + alfa * (recompensa + gamma * max(QTabla[nueva_pos[0]][nueva_pos[1]]))

                    acciones = {0: "Arriba", 1: "Derecha", 2: "Abajo", 3: "Izquierda"}
                    accion = acciones.get(accion, "Acción no válida")

                    camino[tuple(estado_actual.posicion)] = accion
                    estado_actual = Estado(posicion=nueva_pos, problema=self.problema)
            
            #   Estadisticas
            # print(f"Iteracion: {iteracion + 1}/{iteraciones}, | Total de recompensas: {recompensaTotal}, | Camino: {camino}")

        tiempo_ejecucion = time.time() - inicio_tiempo
        print("Tiempo de ejecución: ", tiempo_ejecucion)

        return QTabla   

    def iteracionValores(self, gamma, r, iteraciones):

        QTabla = self.QTabla()

        for _ in range(iteraciones):
            nuevaQTabla = QTabla.copy()

            for i in range(self.problema.nfilas):
                for j in range(self.problema.ncols):
                    maxima_utilidad = 0
                    estado_actual = Estado(posicion=(i, j), problema=self.problema)

                    if list(estado_actual.posicion) not in self.problema.bloqueados and list(estado_actual.posicion) not in self.problema.atrapados and 0 <= estado_actual.posicion[0] < self.problema.nfilas and 0 <= estado_actual.posicion[1] < self.problema.ncols:
                        valores = []
                        for accion in range(4):
                            nueva_pos = estado_actual.acciones(accion).posicion
                            recompensa = self.recompensa(nueva_pos[0], nueva_pos[1], r) 
                            maxima_utilidad = max(QTabla[nueva_pos[0]][nueva_pos[1]])

                            valores.append(recompensa + gamma * maxima_utilidad)
                        
                        # print("Valores:", valores)
                        # valor = max(valores)
                        # print("Valor:", valor)
                        # Santander Iglesias
                        
                        nuevaQTabla[i][j][:] = valores

            QTabla = nuevaQTabla.copy()
        
        return QTabla
    
    
    
    
    def recompensa(self, fila, columna, recompensa):

        # Recompensa de las posiciones de los objetivos
        posiciones_buenas = {tuple(obj[:2]): obj[2] for obj in self.problema.atrapados}
        posiciones_malas = {tuple(obj[:2]): obj[2] for obj in self.problema.peligro_fatal}

        if (fila, columna) in posiciones_buenas:
            return posiciones_buenas[(fila, columna)]

        if (fila, columna) in posiciones_malas:
            return posiciones_malas[(fila, columna)]

        if (fila, columna) in self.problema.peligro:
            return -5

        return recompensa
    
    def formato(self, elemento, decimales):
        # Santander Iglesias
        try:
            if isinstance(elemento, (int, float)):
                return f"{elemento:.{decimales}f}"
            elif isinstance(elemento, list):
                return [self.formato(e, decimales) for e in elemento]
            else:
                raise TypeError("Tipo de dato no admitido para formateo.")
        except Exception as e:
            print(f"Error al formatear el elemento: {e}")
            return elemento

    def mostrarQTabla(self, QTabla):

        finales_buenos, finales_malos = self.problema.finales()

        for i, fila in enumerate(QTabla):
            for j, elemento in enumerate(self.formato(fila, 2)):
                if [i, j] in self.problema.bloqueados:
                    print(Color.estiloTexto(elemento, Color.MAGENTA), end=" ")
                else:
                    if [i, j] in finales_buenos:
                        print(Color.estiloTexto(elemento, Color.AZUL), end="                          ")
                    elif [i, j] in finales_malos:
                        print(Color.estiloTexto(elemento, Color.ROJO), end="                          ")
                    elif [i, j] in self.problema.peligro:
                        print(Color.estiloTexto(elemento, Color.AMARILLO), end=" ")
                    elif [i, j] == self.problema.partida:
                        print(Color.estiloTexto(elemento, Color.VERDE), end=" ")
                    else:
                        print(elemento, end=" ")
            print()


problema = Problema("Aprendizaje-por-refuerzo/initial-rl-instances/lesson5-rl.json")
agente = Agente(problema)
qTablaResultante = agente.qLearning(0.8, 1.05, 0.1, 0.5, 1000) # gamma, r, alfa, epsilon, iteraciones
# qTablaResultante = agente.iteracionValores(0.8, -0.5, 1000) # gamma, r, iteraciones
agente.mostrarQTabla(qTablaResultante)