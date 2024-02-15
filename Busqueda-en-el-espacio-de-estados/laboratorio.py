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
    def generarSucesores(self, nodo):
        sucesores = []
        estado_actual = nodo.estado
        
        acciones_posibles = ["Arriba", "Derecha", "Abajo", "Izquierda"] #Lista de acciones posibles

        for accion in acciones_posibles: # Derecha - 
            nuevo_estado = estado_actual.acciones(accion) # 2,1
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
        self.total_nodos_generados = 0
        self.total_nodos_expandidos = 0
        self.total_tiempo_ejecucion = 0
        self.total_solucion_length = 0
        self.total_solucion_costo = 0

    def insertar(self, nodo, abiertos, objetivo):
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
        # Santander Iglesias


        abiertos = self.inicializarAbiertos() # Inicializar la lista de abiertos
        self.insertar(nodo_inicial, abiertos, objetivo)
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
                print("Generated nodes:", nodos_generados)
                print("Expanded nodes:", nodos_expandidos)
                print("Execution time:", tiempo_ejecucion)
                print("Solution lengt:", nodo_final.altura)
                print("Solution cost:", nodo_final.costo)
                print("Solution:", camino)
                print("")

                self.total_nodos_generados += nodos_generados
                self.total_nodos_expandidos += nodos_expandidos
                self.total_tiempo_ejecucion += tiempo_ejecucion
                self.total_solucion_length += nodo_final.altura
                self.total_solucion_costo += nodo_final.costo
                
                return camino
                
            # Compruebo si no esta cerrado
            if not self.estaCerrado(nodo_actual.estado.posicion, cerrados):
                # Lo añado a los cerrados para no volver a expandirlos
                cerrados.add(nodo_actual.estado.posicion)
                
                # Expando, es decir, saco los sucesores
                sucesores = self.problema.generarSucesores(nodo_actual)
                for sucesor in sucesores:
                    self.insertar(sucesor, abiertos, objetivo)
                    nodos_generados += 1

                nodos_expandidos += 1

        # print("No se encontró un camino = busqueda.buscar(estado_objetivo).")
        return None
    
    def inicializarAbiertos(self):
        # Devuelve la estructura de datos para la lista de abiertos
        pass



class BusquedaAnchura(Busqueda): #FIFO - Cola

    def insertar(self, nodo, abiertos, objetivo):
        abiertos.append(nodo) #Inserta al final de la lista

    def eliminar(self, abiertos):
        return abiertos.pop(0)
    
    def inicializarAbiertos(self):
        return []

class BusquedaProfundidad(Busqueda): #LIFO - Pila

    def insertar(self, nodo, abiertos, objetivo):
        abiertos.insert(0, nodo) #Inserta al inicio de la lista

    def eliminar(self, abiertos):
        return abiertos.pop(0)
    
    def inicializarAbiertos(self):
        return []
    
class BusquedaProfundidadLimitada(BusquedaProfundidad):

    def __init__(self, problema, limite=None):
        super().__init__(problema)
        self.limite = limite

    def insertar(self, nodo, abiertos, objetivo):
        if nodo.altura <= self.limite:
            abiertos.insert(0, nodo)
    
class BusquedaProfundidadIterativa(BusquedaProfundidadLimitada):

    def buscar(self, objetivo):
        self.limite = 1
        while True:
            camino = super().buscar(objetivo)
            if camino:
                return camino
            else:
                self.limite += 1


class PrimeroMejor(Busqueda):
    def insertar(self, nodo, abiertos, objetivo):
        # Utilizando PriorityQueue solo para PrimeroMejor
        abiertos.put((self.heuristica(nodo, objetivo), nodo))

    def eliminar(self, abiertos):
        # Eliminar y devolver el primer elemento de la lista (el de menor heurística)
        return abiertos.get()[1]
        
    def heuristica(self, nodo, objetivo):
        # Implementación de la heurística (distancia de Manhattan)
        return abs(nodo.estado.posicion[0] - objetivo.posicion[0]) + abs(nodo.estado.posicion[1] - objetivo.posicion[1])

    def inicializarAbiertos(self):
        return PriorityQueue()


class AEstrella(Busqueda):

    def insertar(self, nodo, abiertos, objetivo):
        # Utilizando PriorityQueue solo para AEstrella
        costoNodoHeuristica = self.f(nodo, objetivo)
        abiertos.put((costoNodoHeuristica, nodo))

    def eliminar(self, abiertos):
        return abiertos.get()[1]
        
    def f(self, nodo, objetivo):
        # Función f(n) = g(n) + h(n), donde g(n) es el costo acumulado y h(n) es la heurística
        return nodo.costo + self.heuristica(nodo, objetivo)
    
    def heuristica(self, nodo, objetivo):
        # Implementación de la heurística (distancia de Manhattan)
        return abs(nodo.estado.posicion[0] - objetivo.posicion[0]) + abs(nodo.estado.posicion[1] - objetivo.posicion[1])
    
    def inicializarAbiertos(self):
        return PriorityQueue()
        


if __name__ == '__main__':

    problema = Problema("Busqueda-en-el-espacio-de-estados/Problema-distinta-dimension/instance-50-75-563-4-563-2023.json")

    #Metodo de busqueda, si la busqueda es limitada se debe ingresar el limite de profundidad 
    busqueda = BusquedaProfundidadIterativa(problema)
    # busqueda = BusquedaProfundidad(problema)

    total_rescatados = 0

    for atrapado in problema.atrapados:
        total_rescatados += 1
        estado_objetivo = Estado(atrapado)
        print("Objetivo:", estado_objetivo.posicion)
        camino = busqueda.buscar(estado_objetivo)

    
    # Imprimir estadísticas finales
    print("\nFinal statistics")
    print("----------------")
    print("Number of rescued people:", total_rescatados , "of", len(problema.atrapados))
    print("Mean number of generated nodes:", int(busqueda.total_nodos_generados / len(problema.atrapados)))
    print("Mean number of expanded nodes:", busqueda.total_nodos_expandidos / len(problema.atrapados))
    print("Mean execution time:", busqueda.total_tiempo_ejecucion / len(problema.atrapados), "seconds")
    print("Mean solution length:", busqueda.total_solucion_length / len(problema.atrapados))
    print("Mean solution cost:", busqueda.total_solucion_costo / len(problema.atrapados))
