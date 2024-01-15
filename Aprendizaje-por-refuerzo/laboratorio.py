import random
import json
import time

class Color:
    AMARILLO = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    NEGRO = "\033[30m"
    ROJO = "\033[91m"
    VERDE = "\033[92m"
    RESET = "\033[0m"
    AZUL = "\033[94m"

def texto_coloreado(texto, color):
    return f"{color}{texto}{Color.RESET}"

class Estado:
    def __init__(self, posicion):
        self.posicion = posicion

    #Acciones de movimiento del robot
    def acciones(self, accion):
        if accion==0:
            nueva_pos = ((self.posicion[0] - 1,self.posicion[1]))
        elif accion==1:
            nueva_pos = ((self.posicion[0], self.posicion[1] + 1))
        elif accion==2:
            nueva_pos = ((self.posicion[0] + 1,self.posicion[1]))
        elif accion==3:
            nueva_pos = ((self.posicion[0], self.posicion[1] - 1))

        return Estado(nueva_pos)

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

    def QTabla(self):
        QTabla = [[[0.0 for _ in range(4)] for _ in range(self.ncols)] for _ in range(self.nfilas)]

        for objetivo in self.atrapados:
            fila, columna, recompensa = objetivo
            QTabla[fila][columna] = [recompensa]

        for muerte in self.peligro_fatal:
            fila, columna, recompensa = muerte
            QTabla[fila][columna] = [recompensa]

        return QTabla
    
    def finales(self):
        lista_buenos = [[fila, columna] for fila, columna, recompensa in self.atrapados]
        lista_malos = [[fila, columna] for fila, columna, recompensa in self.peligro_fatal]
        # lista_peligros = [[fila, columna] for fila, columna in self.peligro]

        return lista_buenos, lista_malos


class Agente():
    def __init__(self, problema):
        self.problema = problema

    
    def busqueda(self, gamma, r, alfa, iteraciones, exploracion = True):
        inicio_tiempo = time.time()
        QTabla = self.problema.QTabla()
        finales_buenos, finales_malos = self.problema.finales()

        for _ in range(iteraciones):
            estado_actual = Estado(posicion=self.problema.partida)
            vida = True
            while vida:

                if exploracion and random.uniform(0, 1) < gamma:
                    #Exploración
                    direccion = QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]].index(max(QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]]))
                else:
                    numeros = [numero for numero in range(4) if numero != QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]].index(max(QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]]))]
                    direccion = random.choice(numeros)
                
                #Explotación
                if 0 <= direccion <= 3:
                    nueva_pos = estado_actual.acciones(direccion).posicion

                    if 0 <= nueva_pos[0] < self.problema.nfilas and 0 <= nueva_pos[1] < self.problema.ncols and list(nueva_pos) not in self.problema.bloqueados:
                        res = self.recompensa(nueva_pos[0], nueva_pos[1], r) 
                        QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]][direccion ] = (1 - alfa) * QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]][direccion] + alfa * (res + gamma * max(QTabla[nueva_pos[0]][nueva_pos[1]]))
                        estado_actual = Estado(posicion=nueva_pos)
                    else:
                        res = self.recompensa(estado_actual.posicion[0], estado_actual.posicion[1], r)
                        QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]][direccion] = (1 - alfa) * QTabla[estado_actual.posicion[0]][estado_actual.posicion[1]][direccion] + alfa * (res)
                if list(estado_actual.posicion) in finales_buenos or list(estado_actual.posicion) in finales_malos:
                    vida = False
        tiempo_ejecucion = time.time() - inicio_tiempo
        print("Tiempo de ejecución: ", tiempo_ejecucion) 

        return QTabla
    
    def evaluacionPoliticas(self):
        pass

    def mejoraPolitica(self):
        pass

    def iteracionPolitica(self):
        pass      

    
    def recompensa(self, x, y, recompensa):

        posiciones_buenas = {tuple(obj[:2]): obj[2] for obj in self.problema.atrapados}
        posiciones_malas = {tuple(obj[:2]): obj[2] for obj in self.problema.peligro_fatal}

        if (x, y) in posiciones_buenas:
            return posiciones_buenas[(x, y)]

        if (x, y) in posiciones_malas:
            return posiciones_malas[(x, y)]

        if (x, y) in self.problema.peligro:
            return -5

        return recompensa
    
    def formatearElemento(self, elemento, decimales):
        try:
            if isinstance(elemento, (int, float)):
                return f"{elemento:.{decimales}f}"
            elif isinstance(elemento, list):
                return [self.formatearElemento(e, decimales) for e in elemento]
            else:
                raise TypeError("Tipo de dato no admitido para formateo.")
        except Exception as e:
            print(f"Error al formatear el elemento: {e}")
            return elemento

    def mostrarQTabla(self, QTabla):

        finales_buenos, finales_malos = self.problema.finales()

        for i, fila in enumerate(QTabla):
            for j, elemento in enumerate(self.formatearElemento(fila, 2)):
                if [i, j] in self.problema.bloqueados:
                    print(texto_coloreado(elemento, Color.MAGENTA), end=" ")
                else:
                    if [i, j] in finales_buenos:
                        print(texto_coloreado(elemento, Color.AZUL), end="                          ")
                    elif [i, j] in finales_malos:
                        print(texto_coloreado(elemento, Color.ROJO), end="                          ")
                    elif [i, j] in self.problema.peligro:
                        print(texto_coloreado(elemento, Color.AMARILLO), end=" ")
                    elif [i, j] == self.problema.partida:
                        print(texto_coloreado(elemento, Color.VERDE), end=" ")
                    else:
                        print(elemento, end=" ")  # Usamos end=" " para imprimir en la misma línea
            print()


problema = Problema("Aprendizaje-por-refuerzo/initial-rl-instances/larger-rl.json")
agente = Agente(problema)
q_tabla_resultante = agente.busqueda(0.8, -0.05, 0.1, 10000)
agente.mostrarQTabla(q_tabla_resultante)