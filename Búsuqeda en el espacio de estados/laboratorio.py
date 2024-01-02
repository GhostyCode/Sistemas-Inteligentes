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

    def __lt__(self, otro_nodo):
        # Define la comparación basada en la heurística
        return self.costo < otro_nodo.costo
        

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
            nueva_pos = ((self.posicion[0], self.posicion[1] + 1))
        elif accion=="Izquierda":
            nueva_pos = ((self.posicion[0], self.posicion[1] - 1))

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

        
    #Retornar la lista de sucerores
    def generarSucesores(self, nodo, limite=None):
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

                #Si el limite es None, no se aplica la busqueda limitada
                if limite is None:
                    sucesores.append(nuevo_nodo)
                elif nuevo_nodo.altura <= limite:
                    sucesores.append(nuevo_nodo)

        return sucesores
    



class Busqueda:
    def __init__(self, problema, limite=None):
        self.problema = problema
        self.indice_objetivo_actual = 0
        self.busquedad_tipo_limitada = True if isinstance(self, BusquedaProfundidadLimitada) else False
        self.busquedad_tipo_iterativa = True if isinstance(self, BusquedaProfundidadIterativa) else False
        self.limite = limite

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

        # abiertos = [nodo_inicial]

        abiertos = self.inicializarAbiertos()
        self.insertar(nodo_inicial, abiertos)
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
                print("Nodos generados:", nodos_generados)
                print("Número de nodos expandidos:", nodos_expandidos)
                print("Tiempo de ejecución:", tiempo_ejecucion)
                print("Profundidad de la solución:", nodo_final.altura)
                print("Costo de la solución:", nodo_final.costo)
                print("Camino de la solución:", camino)
                print("")
                # print("Recorrido de la solución:")

                if self.indice_objetivo_actual < len(self.problema.atrapados) - 1:
                    self.indice_objetivo_actual += 1
                return camino
                
            # Compruebo si no esta cerrado
            if not self.estaCerrado(nodo_actual.estado.posicion, cerrados):
                # Lo añado a los cerrados para no volver a expandirlos
                cerrados.add(nodo_actual.estado.posicion)

                # Por cada sucesor
                # Meto en la lista de nodos abiertos el sucesor
                if self.busquedad_tipo_limitada:
                    # Expando, es decir, saco los sucesores
                    sucesores = self.problema.generarSucesores(nodo_actual, self.limite)
                    for sucesor in sucesores:
                        self.insertar(sucesor, abiertos)
                        nodos_generados += 1

                elif self.busquedad_tipo_iterativa:
                    # Expando, es decir, saco los sucesores
                    """Algoritmo de Iterative Deepening Search."""
                    #Inicializa la profundidad
                    self.limite = 0
                    #Revisa si hay resultados
                    resultado = self.problema.generarSucesores(nodo_actual, self.limite)

                    for sucesor in resultado:
                        print("Sucesor:", sucesor.estado.posicion)
                        self.insertar(sucesor, abiertos)
                        nodos_generados += 1
                        
                    #Itera hasta encontrar una solución
                    while not resultado:
                        #Agrega una profundidad más
                        self.limite += 1
                        #Revisa el resultado
                        resultado = self.problema.generarSucesores(nodo_actual, self.limite)
                        for sucesor in resultado:
                            self.insertar(sucesor, abiertos)
                            nodos_generados += 1
                else:
                    # Expando, es decir, saco los sucesores
                    sucesores = self.problema.generarSucesores(nodo_actual)
                    for sucesor in sucesores:
                        self.insertar(sucesor, abiertos)
                        nodos_generados += 1

                nodos_expandidos += 1

                

        # print("No se encontró un camino = busqueda.buscar(estado_objetivo).")
        return None
    
    def inicializarAbiertos(self):
        # Devuelve la estructura de datos para la lista de abiertos
        pass



class BusquedaAnchura(Busqueda):

    def insertar(self, nodo, abiertos):
        abiertos.append(nodo)

    def eliminar(self, abiertos):
        return abiertos.pop(0)
    
    def inicializarAbiertos(self):
        return []

class BusquedaProfundidad(Busqueda):

    def insertar(self, nodo, abiertos):
        abiertos.insert(0, nodo)

    def eliminar(self, abiertos):
        return abiertos.pop(0)
    
    def inicializarAbiertos(self):
        return []
    
class BusquedaProfundidadLimitada(Busqueda):

    def insertar(self, nodo, abiertos):
        abiertos.insert(0, nodo)

    def eliminar(self, abiertos):
        return abiertos.pop(0)
    
    def inicializarAbiertos(self):
        return []
    
class BusquedaProfundidadIterativa(Busqueda):

    def insertar(self, nodo, abiertos):
        abiertos.insert(0, nodo)

    def eliminar(self, abiertos):
        return abiertos.pop(0)
    
    def inicializarAbiertos(self):
        return []


class PrimeroMejor(Busqueda):
    def insertar(self, nodo, abiertos):
        # Utilizando PriorityQueue solo para PrimeroMejor
        abiertos.put((self.heuristica(nodo), nodo))

    def eliminar(self, abiertos):
        # Eliminar y devolver el primer elemento de la lista (el de menor heurística)
        if not abiertos.empty():
            return abiertos.get()[1]
        else:
            return abiertos.get()
        
    def heuristica(self, nodo):
        # Implementación de la heurística (distancia de Manhattan)
        objetivo = self.problema.atrapados[self.indice_objetivo_actual]
        return abs(nodo.estado.posicion[0] - objetivo[0]) + abs(nodo.estado.posicion[1] - objetivo[1])

    def inicializarAbiertos(self):
        return PriorityQueue()


class AEstrella(Busqueda):

    def insertar(self, nodo, abiertos):
        # Utilizando PriorityQueue solo para AEstrella
        costoNodoHeuristica = self.f(nodo)
        abiertos.put((costoNodoHeuristica, nodo))

    def eliminar(self, abiertos):
        if not abiertos.empty():
            return abiertos.get()[1]
        else:
            return abiertos.get()
        
    def f(self, nodo):
        # Función f(n) = g(n) + h(n), donde g(n) es el costo acumulado y h(n) es la heurística
        return nodo.costo + self.heuristica(nodo)
    
    def heuristica(self, nodo):
        # Implementación de la heurística (distancia de Manhattan)
        objetivo = self.problema.atrapados[self.indice_objetivo_actual]
        return abs(nodo.estado.posicion[0] - objetivo[0]) + abs(nodo.estado.posicion[1] - objetivo[1])
    
    def inicializarAbiertos(self):
        return PriorityQueue()
        

# Iterar los atrapados, porque solo esta accediendo al primer objetivo en la heuristica(listo)
# Utilizar una cola de priorida para para los algoritmos de Primero al Mejor y A Estrella, utilizando la libreria PriorityQueue(listo)


if __name__ == '__main__':

    problema = Problema("Problema-distinta-dimension/instance-20-20-33-8-33-2023.json")

    #Metodo de busqueda, si la busqueda es limitada se debe ingresar el limite de profundidad 
    # busqueda = BusquedaProfundidadLimitada(problema, limite=20)
    busqueda = BusquedaProfundidad(problema)

    for atrapado in problema.atrapados:
        estado_objetivo = Estado(atrapado)
        print("Objetivo:", estado_objetivo.posicion)
        camino = busqueda.buscar(estado_objetivo)