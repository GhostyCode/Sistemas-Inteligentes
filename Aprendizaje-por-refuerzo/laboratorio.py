import json
import random


with open("Aprendizaje-por-refuerzo/initial-rl-instances/larger-rl.json", 'r', encoding="utf8") as file:
    t=json.load(file)

class Colores:
    RESET = "\033[0m"
    NEGRO = "\033[30m"
    ROJO = "\033[91m"
    VERDE = "\033[92m"
    AMARILLO = "\033[93m"
    AZUL = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"

def texto_coloreado(texto, color):
    return f"{color}{texto}{Colores.RESET}"

class Problema:
    
    def _init_(self):
        self.ciudad=t["city"]
        self.filas=t["city"]["rows"]
        self.columnas=t["city"]["columns"]
        self.muros=t["city"]["blocked"]
        self.salida=t["departure"]
        self.peligro=t["dangers"]
        self.peligro_fatal=t["fatal_dangers"]
        self.fin=t["trapped"]

    def mapa(self):
        matrizQ = [[ "⬜" for _ in range(t["city"]["columns"])] for _ in range(t["city"]["rows"])]

        partida_fila, partida_columna = t["departure"]
        matrizQ[partida_fila][partida_columna] = "🌌"

        for bloqueo in t["city"]["blocked"]:
            fila, columna = bloqueo
            matrizQ[fila][columna] = "🛑"
        for peligro in t["dangers"]:
            fila, columna = peligro
            matrizQ[fila][columna] = "🚸"
        for objetivo in t["trapped"]:
            fila, columna, a= objetivo
            matrizQ[fila][columna] = "👨‍💻"
        for Muerte in t["fatal_dangers"]:
            fila, columna, a = Muerte
            matrizQ[fila][columna] = "💀"

        for fila in matrizQ:
            for elemento in fila:
                print(elemento, end=" ")  # Usamos end=" " para imprimir en la misma línea
            print()

class QLearn:
    def _init_(self):
        self.ciudad=t["city"]
        self.filas=t["city"]["rows"]
        self.columnas=t["city"]["columns"]
        self.muros=t["city"]["blocked"]
        self.salida=t["departure"]
        self.peligro=t["dangers"]
        self.peligro_fatal=t["fatal_dangers"]
        self.fin=t["trapped"]

    def hacerQTabla(self):
        QTabla = [[[0.0 for _ in range(4)] for _ in range(t["city"]["columns"])] for _ in range(t["city"]["rows"])]

        for objetivo in t["trapped"]:
            fila, columna, valor= objetivo
            QTabla[fila][columna] = [valor]

        for Muerte in t["fatal_dangers"]:
            fila, columna, valor = Muerte
            QTabla[fila][columna] = [valor]

        return QTabla

    def finales(self):
        lista_buenos = []
        lista_malos = []
        lista_peligros = []
        for objetivo in t["trapped"]:
            fila, columna, valor= objetivo
            lista_buenos.append([fila,columna])

        for Muerte in t["fatal_dangers"]:
            fila, columna, valor = Muerte
            lista_malos.append([fila,columna])

        for peligro in t["dangers"]:
            fila, columna= peligro
            lista_peligros.append([fila,columna])

        return lista_buenos, lista_malos

    def busqueda(self, gamma, r, alfa, bucle):
        aux = QLearn()
        QTabla = aux.hacerQTabla()
        finalesBuenos, finalesMalos= aux.finales()

        for i in range(bucle):
            x, y = t["departure"]
            vida= True
            while vida:
                #___________
                #Elección de forma de moverse
                #__________print("__________", i)
                ran1=random.random()
                if gamma > ran1:
                    match QTabla[x][y].index(max(QTabla[x][y])):
                        case 0:#Arriba
                            if (x > 0) and ([x-1, y] not in t["city"]["blocked"]):
                                res = aux.recompensa(x-1, y, r)
                                QTabla[x][y][0] = (1-alfa)* QTabla[x][y][0] + alfa * (res + gamma * max(QTabla[x-1][y]))
                                x=x-1
                            else:
                                res = aux.recompensa(x, y, r)
                                QTabla[x][y][0] = (1-alfa)* QTabla[x][y][0] + alfa * (res)
                        case 1:#Derecha
                            if (y+1 < t["city"]["columns"]) and ([x, y+1] not in t["city"]["blocked"]):
                                res = aux.recompensa(x, y+1, r)
                                QTabla[x][y][1] = (1-alfa)* QTabla[x][y][1] + alfa * (res + gamma * max(QTabla[x][y+1]))
                                y=y+1
                            else:
                                res = aux.recompensa(x, y, r)
                                QTabla[x][y][1] = (1-alfa)* QTabla[x][y][1] + alfa * (res)
                        case 2:#Abajo
                            if (x+1 < t["city"]["rows"]) and ([x+1, y] not in t["city"]["blocked"]):
                                res = aux.recompensa(x+1, y, r)
                                QTabla[x][y][2] = (1-alfa)* QTabla[x][y][2] + alfa * (res + gamma * max(QTabla[x+1][y]))
                                x=x+1
                            else:
                                res = aux.recompensa(x, y, r)
                                QTabla[x][y][2] = (1-alfa)* QTabla[x][y][2] + alfa * (res)
                        case 3:#Izquierda
                            if (y > 0) and ([x, y-1] not in t["city"]["blocked"]):
                                res = aux.recompensa(x, y-1, r)
                                QTabla[x][y][3] = (1-alfa)* QTabla[x][y][3] + alfa * (res + gamma * max(QTabla[x][y-1]))
                                y=y-1
                            else:
                                res = aux.recompensa(x, y, r)
                                QTabla[x][y][3] = (1-alfa)* QTabla[x][y][3] + alfa * (res)

                else:
                    numeros = [numero for numero in range(0, 3) if numero != QTabla[x][y].index(max(QTabla[x][y]))]
                    match random.choice(numeros):
                        case 0:#Arriba
                            if (x > 0) and ([x-1, y] not in t["city"]["blocked"]):
                                res = aux.recompensa(x-1, y, r)
                                QTabla[x][y][0] = (1-alfa)* QTabla[x][y][0] + alfa * (res + gamma * max(QTabla[x-1][y]))
                                x=x-1
                            else:
                                res = aux.recompensa(x, y, r)
                                QTabla[x][y][0] = (1-alfa)* QTabla[x][y][0] + alfa * (res)
                        case 1:#Derecha
                            if (y+1 < t["city"]["columns"]) and ([x, y+1] not in t["city"]["blocked"]):
                                res = aux.recompensa(x, y+1, r)
                                QTabla[x][y][1] = (1-alfa)* QTabla[x][y][1] + alfa * (res + gamma * max(QTabla[x][y+1]))
                                y=y+1
                            else:
                                res = aux.recompensa(x, y, r)
                                QTabla[x][y][1] = (1-alfa)* QTabla[x][y][1] + alfa * (res)
                        case 2:#Abajo
                            if (x+1 < t["city"]["rows"]) and ([x+1, y] not in t["city"]["blocked"]):
                                res = aux.recompensa(x+1, y, r)
                                QTabla[x][y][2] = (1-alfa)* QTabla[x][y][2] + alfa * (res + gamma * max(QTabla[x+1][y]))
                                x=x+1
                            else:
                                res = aux.recompensa(x, y, r)
                                QTabla[x][y][2] = (1-alfa)* QTabla[x][y][2] + alfa * (res)
                        case 3:#Izquierda
                            if (y > 0) and ([x, y-1] not in t["city"]["blocked"]):
                                res = aux.recompensa(x, y-1, r)
                                QTabla[x][y][3] = (1-alfa)* QTabla[x][y][3] + alfa * (res + gamma * max(QTabla[x][y-1]))
                                y=y-1
                            else:
                                res = aux.recompensa(x, y, r)
                                QTabla[x][y][3] = (1-alfa)* QTabla[x][y][3] + alfa * (res)
                if ([x, y] in finalesBuenos) or ([x, y] in finalesMalos):
                    vida=False
        return QTabla

    def recompensa(self, x, y, res):
        aux = QLearn()
        finalesBuenos, finalesMalos = aux.finales()
        if ([x, y] in finalesBuenos):
            for objBueno in t["trapped"]:
                fila, columna, r= objBueno
                if (x == fila) and (y == columna):
                    return r
        if ([x, y] in finalesMalos):
            for objMalo in t["fatal_dangers"]:
                fila, columna, r= objMalo
            if (x == fila) and (y == columna):
                return r
        if([x, y] in t["dangers"]):
            return -5

        return res

    def formatear_vector(self, vector, decimales):
        aux = QLearn()
        if isinstance(vector, list):
            return [aux.formatear_vector(elemento, decimales) for elemento in vector]
        elif isinstance(vector, (int, float)):
            return "{: .{}f}".format(vector, decimales)
        else:
            return vector

    def imprimirQTabla(self, QTabla):
        aux = QLearn()
        print("    🢁       🢂       🢃       🢀         🢁       🢂       🢃       🢀​")
        finalesBuenos, finalesMalos = aux.finales()
        i=0
        for fila in QTabla:
            j=0
            for elemento in aux.formatear_vector(fila, 2):
                if [i, j] in t["city"]["blocked"]:
                    print(texto_coloreado(elemento, Colores.NEGRO),end=" ")
                else:
                    if [i, j] in finalesBuenos:
                        print(texto_coloreado(elemento, Colores.AZUL),end="                          ")
                    else:
                        if [i, j] in finalesMalos:
                            print(texto_coloreado(elemento, Colores.ROJO),end="                          ")
                        else:
                            if  [i, j] in t["dangers"]:
                                print(texto_coloreado(elemento, Colores.AMARILLO),end=" ")
                            else:
                                if [i, j] == t["departure"]:
                                    print(texto_coloreado(elemento, Colores.VERDE),end=" ")
                                else: print(elemento, end=" ")  # Usamos end=" " para imprimir en la misma línea
                j=j+1
            print()
            i=i+1

primer = QLearn()
a=primer.busqueda(0.8, -0.05, 0.1, 10000)
primer.imprimirQTabla(a)