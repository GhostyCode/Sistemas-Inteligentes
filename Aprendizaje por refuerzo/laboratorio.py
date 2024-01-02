import json
from abc import ABC, abstractmethod
import time
from queue import PriorityQueue

class Accion:
    def __init__(self, movimiento, costo):
        self.movimiento = movimiento
        self.costo = costo

class Nodo:
    def __init__(self, estado, accion, padre, costo, altura):
        self.estado = estado
        self.accion = accion    
        self.padre = padre
        self.costo = costo
        self.altura = altura

class Estado:
    def __init__(self, posicion):
        self.posicion = tuple(posicion)

    #Acciones de movimiento del robot
    def acciones(self, accion):
        if accion=="Arriba":
            nueva_pos = ((self.posicion[0] - 1,self.posicion[1]))
        elif accion=="Abajo":
            nueva_pos = ((self.posicion[0] + 1,self.posicion[1]))
        elif accion=="Derecha":
            nueva_pos = ((self.posicion[0],self.posicion[1] + 1))
        elif accion=="Izquierda":
            nueva_pos = ((self.posicion[0],self.posicion[1] - 1))

        return Estado(nueva_pos)


class Problema:
    def __init__(self, problema):
        with open(problema, 'r') as file:
            self.new_dictionary = json.load(file)
        
        self.nfilas = self.new_dictionary['city']['rows']
        self.ncols = self.new_dictionary['city']['columns']
        self.bloqueados = set(map(tuple, self.new_dictionary['city']['blocked']))
        self.partida = self.new_dictionary['departure']
        self.peligro = set(map(tuple, self.new_dictionary['dangers']))
        self.atrapados = list(map(tuple, self.new_dictionary['trapped']))        

        '''grid = [['[Libre]'] * ncols for x in range(nfilas)]

        # Posiciones bloqueadas
        for position in self.new_dictionary["city"]["blocked"]:
            row, col = position
            grid[row][col] = "[Bloqueados]"

        # Posición de partida
        departure_row, departure_col = self.new_dictionary["departure"]
        grid[departure_row][departure_col] = "[Partida]"

        # Posiciones de peligro
        for danger_position in self.new_dictionary["dangers"]:
            row, col = danger_position
            grid[row][col] = "[Peligro]"

        for trapped_position in self.new_dictionary["trapped"]:
            row, col = trapped_position
            grid[row][col] = "[Atrapados]"

        # Imprimir el grid
        for row in grid:
            print(" ".join(row))'''
        
    #Retornar la lista de sucerores
    def generarSucesores(self, nodo):
        sucesores = []
        estado_actual = nodo.estado

        acciones_posibles = ["Arriba", "Derecha", "Abajo", "Izquierda"]

        for accion in acciones_posibles:
            nuevo_estado = estado_actual.acciones(accion)
            nueva_posicion = nuevo_estado.posicion

            if (
                0 <= nueva_posicion[0] < self.nfilas
                and 0 <= nueva_posicion[1] < self.ncols
                and nueva_posicion not in self.bloqueados
            ):
                #SI la posicion es peligro el costo suma 5 en lugar de 1
                if nueva_posicion not in self.peligro:
                    nuevo_costo = nodo.costo + 1
                else:
                    nuevo_costo = nodo.costo + 5

                nuevo_nodo = Nodo(
                    estado=nuevo_estado,
                    accion=Accion(accion, nuevo_costo),
                    padre=nodo,
                    costo=nuevo_costo,
                    altura=nodo.altura + 1,
                )

                sucesores.append(nuevo_nodo)

        return sucesores


class Busqueda:
    def __init__(self, problema):
        self.problema = problema

    def insertar(self, nodo, abiertos):
        pass

    def eliminar(self, abiertos):
        pass

    def estaCerrado(self, estado, cerrados):
        return estado in cerrados

    
    def buscar(self, objetivo):

        inicio_tiempo = time.time()

        # Insertar en lista de nodos abierto el nodo inicial
        nodo_inicial = Nodo(
            estado=Estado(self.problema.partida),
            accion=None,
            padre=None,
            costo=0,
            altura=0,
        )

        abiertos = [nodo_inicial]
        cerrados = set()

        nodos_expandidos = 0
        nodos_generados = 1

        # Mientras haya nodos en la lista de nodos abiertos
        while abiertos:

            # Extraigo un nodo de la lista de abiertos 
            nodo_actual = self.eliminar(abiertos)

            # Compruebo si es el final
            if nodo_actual.estado.posicion == objetivo.posicion:
                # Termino y recupero el camino
                camino = []
                nodo_final = nodo_actual
                while nodo_actual.padre:
                    camino.insert(0, nodo_actual.accion.movimiento)
                    nodo_actual = nodo_actual.padre

                tiempo_ejecucion = time.time() - inicio_tiempo
                        
                # Imprimir resultados
                print("Profundidad de la solución:", nodo_final.altura)
                print("Costo de la solución:", nodo_final.costo)
                print("Número de nodos expandidos:", nodos_expandidos)
                print("Nodos generados:", nodos_generados)
                print("Tiempo de ejecución:", tiempo_ejecucion)
                # print("Recorrido de la solución:")

                return camino
                
            # Compruebo si no esta cerrado
            if not self.estaCerrado(nodo_actual.estado.posicion, cerrados):
                # Lo añado a los cerrados para no volver a expandirlos
                cerrados.add(nodo_actual.estado.posicion)

                # Expando, es decir, saco los sucesores
                sucesores = self.problema.generarSucesores(nodo_actual)
                

                # Por cada sucesor
                # Meto en la lista de nodos abiertos el sucesor
                for sucesor in sucesores:
                    self.insertar(sucesor, abiertos)
                    nodos_generados += 1

                nodos_expandidos += 1

        # print("No se encontró un camino.")
        return None


class BusquedaAnchura(Busqueda):

    def insertar(self, nodo, abiertos):
        abiertos.append(nodo)

    def eliminar(self, abiertos):
        return abiertos.pop(0)

class BusquedaProfundidad(Busqueda):

    def insertar(self, nodo, abiertos):
        abiertos.insert(0, nodo)

    def eliminar(self, abiertos):
        return abiertos.pop(0)


class PrimeroMejor(Busqueda):
    def insertar(self, nodo, abiertos):
        # Si la lista de abiertos está vacía, simplemente agregamos el nodo
        costoNodoHeuristica = self.heuristica(nodo)
        if len(abiertos) == 0:
            abiertos.append((costoNodoHeuristica, nodo))
        else:
            # Recorrer la lista para introducir el nodo en orden
            for i in range(len(abiertos)):
                # Si el nodo a introducir tiene menor coste que el nodo de la lista
                if costoNodoHeuristica < abiertos[i][0]:
                    # Introducimos el nodo en la posición i
                    abiertos.insert(i, (costoNodoHeuristica, nodo))
                    # Salimos del bucle
                    break
                # Si el nodo a introducir tiene el mismo coste que el nodo de la lista
                elif costoNodoHeuristica == abiertos[i][0]:
                    # Introducimos el nodo en la posición i + 1
                    abiertos.insert(i + 1, (costoNodoHeuristica, nodo))
                    # Salimos del bucle
                    break
                # Si hemos llegado al final de la lista
                elif i == len(abiertos) - 1:
                    # Introducimos el nodo al final
                    abiertos.append((costoNodoHeuristica, nodo))
                    # Salimos del bucle
                    break

    def eliminar(self, abiertos):
        # Eliminar y devolver el primer elemento de la lista (el de menor heurística)
        if len(abiertos) > 1:
            return abiertos.pop(0)[1]
        else:
            return abiertos.pop(0)


    def heuristica(self, nodo):
        # Implementación de la heurística (distancia de Manhattan)
        objetivo = self.problema.atrapados[0]
        return abs(nodo.estado.posicion[0] - objetivo[0]) + abs(nodo.estado.posicion[1] - objetivo[1])


class AEstrella(Busqueda):

    def insertar(self, nodo, abiertos):
        # abiertos.append(nodo)
        # abiertos.sort(key=lambda x: self.f(x))
        costoNodoHeuristica = self.f(nodo)
        if len(abiertos) == 0:
            abiertos.append((costoNodoHeuristica, nodo))
        else:
            # Recorrer la lista para introducir el nodo en orden
            for i in range(len(abiertos)):
                # Si el nodo a introducir tiene menor coste que el nodo de la lista
                if costoNodoHeuristica < abiertos[i][0]:
                    # Introducimos el nodo en la posición i
                    abiertos.insert(i, (costoNodoHeuristica, nodo))
                    # Salimos del bucle
                    break
                # Si el nodo a introducir tiene el mismo coste que el nodo de la lista
                elif costoNodoHeuristica == abiertos[i][0]:
                    # Introducimos el nodo en la posición i + 1
                    abiertos.insert(i + 1, (costoNodoHeuristica, nodo))
                    # Salimos del bucle
                    break
                # Si hemos llegado al final de la lista
                elif i == len(abiertos) - 1:
                    # Introducimos el nodo al final
                    abiertos.append((costoNodoHeuristica, nodo))
                    # Salimos del bucle
                    break

    def eliminar(self, abiertos):
        if len(abiertos) > 1:
            return abiertos.pop(0)[1]
        else:
            return abiertos.pop(0)

    def f(self, nodo):
        # Función f(n) = g(n) + h(n), donde g(n) es el costo acumulado y h(n) es la heurística
        return nodo.costo + self.heuristica(nodo)
    
    def heuristica(self, nodo):
        # Implementación de la heurística (distancia de Manhattan)
        objetivo = self.problema.atrapados[0]
        return abs(nodo.estado.posicion[0] - objetivo[0]) + abs(nodo.estado.posicion[1] - objetivo[1])

# Añadir la heuristica y el medoto f(n) a la clase Problema
# Iterar los atrapados, porque solo esta accediendo al primer objetivo en la heuristica

# Utilizar una cola de priorida para para los algoritmos de Primero al Mejor y A Estrella, utilizando la libreria PriorityQueue


if __name__ == '__main__':

    problema = Problema("Problema-distinta-dimension/instance-30-18-12-3-12-2023.json")

    #Metodo de busqueda 
    busqueda = AEstrella(problema)

    for atrapado in problema.atrapados:
        estado_objetivo = Estado(atrapado)
        camino = busqueda.buscar(estado_objetivo)