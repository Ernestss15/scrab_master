from collections import Counter
from colorama import init, Fore, Back, Style
from exceptions import InvalidCoordinatesError, InvalidPlacementError, InvalidWordError

import json
import random
import os
import sys

class Tablero(object):

    def __init__(self):
        #definimos las cassillas especiales
        self.casillas_especiales = [
            'W  l   W   l  W',
            ' w   L   L   w ',
            '  w   l l   w  ',
            'l  w   l   w  l',
            '    w     w    ',
            ' L   L   L   L ',
            '  l   l l   l  ',
            'W  l   *   l  W',
            '  l   l l   l  ',
            ' L   L   L   L ',
            '    w     w    ',
            'l  w   l   w  l',
            '  w   l l   w  ',
            ' w   L   L   w ',
            'W  l   W   l  W',
        ]

        self.estado = [''.join([' ' for _ in range(15)]) for _ in range(15)]

    def __str__(self):

        #devuelve el tablero
        reiniciar = Style.RESET_ALL
        color_casillas_especiales = {
                            ' ': '',
                            'W': Fore.RED,
                            'w': Fore.MAGENTA,
                            'L': Fore.BLUE,
                            'l': Fore.CYAN,
                            '*': Fore.MAGENTA,
                            }

        rep_string=  "   " + ' '.join([str(hex(x))[-1] for x in range(15)]) + "\n"

        for i in range(15):
            linia=''
            for j, casilla in enumerate(self.estado[i]):
                if casilla != ' ':
                    linia += casilla
                else:
                    linia += color_casillas_especiales[self.casillas_especiales[i][j]] + self.casillas_especiales[i][j] + reiniciar
                linia += ' '

            rep_string += str(hex(i))[-1] + '  ' + linia + reiniciar + '\n'
        return rep_string + reiniciar

    def actualizarMovimiento(self,movimiento):

        #funcion que se encarga de actualizar el tablero con el movimiento actual

        y,x = movimiento.coordenadas

        if movimiento.dir == 'A':
            for i, c in enumerate (movimiento.palabra):
                self.estado[y+i] = self.estado[y+i][:x] + c + self.estado[y+i][x+1:]
        if movimiento.dir == 'D':
                self.estado[y]= self.estado[y][:x] + movimiento.palabra + self.estado[y][x+len(movimiento.palabra):]

        return True


class Reglas(object):

    #Contiene las funciones que se encargan de comprobar que se cumplan las normas
    def __init__(self):

        self.casillas_especiales_tablero = [
             'W  l   W   l  W',
            ' w   L   L   w ',
            '  w   l l   w  ',
            'l  w   l   w  l',
            '    w     w    ',
            ' L   L   L   L ',
            '  l   l l   l  ',
            'W  l   *   l  W',
            '  l   l l   l  ',
            ' L   L   L   L ',
            '    w     w    ',
            'l  w   l   w  l',
            '  w   l l   w  ',
            ' w   L   L   w ',
            'W  l   W   l  W',
        ]

        #cargamos las putnuaciones correspondientes de cada ficha
        with open('data/puntuacion_fichas.json', 'r') as infile:
            self.puntuacion_fichas = json.loads(infile.read())

        #cargamos el diccionario general que contiene todas las palabras
        self.diccionario_root = self.generarArbolDiccionario()
        with open('data/diccionario_esp.json', 'r') as infile:
            self.diccionario_esp = json.loads(infile.read())


    def calcularPenalizacion(self, atril):

        #calcula la penalización por tener fichas en el atril al finalizar partida
        return sum (self.puntuacion_fichas[ficha] for ficha in atril)


    @staticmethod
    def generarArbolDiccionario(dicc_path='data/diccionario.txt'):

        if dicc_path == 'data/diccionario.txt':
            with open('data/diccionario_arbol.json', 'r') as infile:
                diccionario_arbol = json.load(infile)

        else:
            with open(dicc_path, 'r') as infile:
                linias_diccionario = [palabra[:-1] for palabra in infile]

            diccionario_arbol = {'VALID': False, 'WORD': ''}
            for palabra in linias_diccionario:
                rama_activa = diccionario_arbol
                for i,caracter in enumerate(palabra):
                    if caracter not in rama_activa:
                        rama_activa[caracter] = {'VALID':False, 'WORD':rama_activa['WORD'] + caracter}
                    rama_activa = rama_activa [caracter]
                    if i == len(palabra)-1:
                        rama_activa['VALID'] = True

        return diccionario_arbol


    def puntuacionMovimiento(self, movimiento, tablero_estado, palabra_ilegal=False):


        def vecinoX (y, x):
            if (x > 0 and tablero_estado[y][x-1] != ' ') or (x < 14 and tablero_estado[y][x+1] != ' '):
                return True

        def vecinoY (y, x):
            if (y > 0 and tablero_estado[y-1][x] != ' ') or (y < 14 and tablero_estado[y+1][x] != ' '):
                return True

        y , x = movimiento.coordenadas

        if palabra_ilegal or self.palabraValida(movimiento.palabra):
            puntuacion_total = self.puntuacionPalabra(y, x, movimiento.dir, movimiento.palabra, tablero_estado)
        else:
            return -1

        #obtenemos hacia que direccion se escribe la palabra
        abajo, derecha = int(movimiento.dir == 'A'), int(movimiento.dir == "D")


        posicion_valida = False

        for i, ficha in enumerate(movimiento.palabra):
            if(y+i*abajo,x+i*derecha) == (7,7):
                posicion_valida = True

            #si la palabra se escribira en vertical
            if movimiento.dir == 'A' and vecinoX(y+i,x):
                #print("comprobado posicion valida abajo: {}{}".format(y,x))
                posicion_valida = True
                #solo actuaremos si se trata de una casilla libre
                if tablero_estado[y+i][x] == ' ':
                    #si la palabra se forma hacia abajo comprobamos el eje X
                    palabra_inicio, palabra_fin = x, x
                    while palabra_inicio > 0 and tablero_estado[y+i][palabra_inicio-1] != ' ':
                        palabra_inicio -= 1
                    while palabra_fin < 14 and tablero_estado[y+i][palabra_fin +1] != ' ':
                        palabra_fin += 1

                    palabra_ext = tablero_estado[y+i][palabra_inicio:x] + ficha + tablero_estado[y+i][x+1:palabra_fin+1]

                    if palabra_ilegal or self.palabraValida(palabra_ext):
                        puntuacion_total += self.puntuacionPalabra(y+i, palabra_inicio, 'D', palabra_ext, tablero_estado)
                    else:
                        return -1

            #se repite el mismo proceso para las palabras horizontales
            elif movimiento.dir == 'D' and vecinoY(y, x+i):
                #print("comprobado posicion valida derecha: {}{}".format(y,x))
                posicion_valida = True
                if tablero_estado[y][x+i] == ' ':
                    #si la palabra se forma hacia la derecha comprobamos el eje Y
                    palabra_inicio, palabra_fin = y, y
                    while palabra_inicio > 0 and tablero_estado[palabra_inicio-1][x+i] != ' ':
                        palabra_inicio -= 1
                    while palabra_fin < 14 and tablero_estado[palabra_fin +1][x+i] != ' ':
                        palabra_fin += 1

                    palabra_ext = ''.join([tablero_estado[palabra_y][x+i] if palabra_y != y else ficha for palabra_y in range(palabra_inicio,palabra_fin+1)])

                    if palabra_ilegal or self.palabraValida(palabra_ext):
                        puntuacion_total += self.puntuacionPalabra(palabra_inicio,x+i, 'A', palabra_ext, tablero_estado)
                    else:
                        return -1

        #si esta palabra no intersecciona con ninguna otra letra del tablero, entonce la palabra no vale
        if not posicion_valida and not palabra_ilegal:
            return -1
        else:
            return puntuacion_total


    def puntuacionPalabra(self, y, x, direccion, palabra, tablero_estado):

        #print("las coordenadas son : {} {}".format(y,x))
        puntuacion = 0
        palabra_multiplicador = 1

        assert(direccion == 'D' or direccion == 'A')

        fichas_atril_usadas = 0     # si se utilizan todas la fichas del atril del jugador hay un bonus de 20 puntos
        abajo, derecha = int(direccion == 'A'), int(direccion=='R')

        for i, ficha in enumerate(palabra):
            if ficha.islower():
                ficha= '?'
            #print("estoy comprobando puntuaciones")
            tablero_ficha_actual = tablero_estado[y+i*abajo][x+i*derecha] #recuperamos el estado actualizar
            #print("estado del tablero actual: {}".format(tablero_ficha_actual))
            if tablero_ficha_actual != ' ':
                if tablero_ficha_actual != ficha and not (tablero_ficha_actual.islower() and ficha == '?'):
                    raise InvalidPlacementError(word=palabra, true_tile=tablero_ficha_actual, attempted_tile=ficha) #se genera una excepcion, la ficha no es la que deberia ser

                else:
                    puntuacion += self.puntuacion_fichas[ficha]
            else:
                fichas_atril_usadas += 1
                #en este caso la casilla esta libre y observaremos la puntuacion especial de la casilla
                casilla_especial = self.casillas_especiales_tablero[y+i*abajo][x+i*derecha]
                if casilla_especial == ' ':
                    puntuacion += self.puntuacion_fichas[ficha]
                else:
                    if casilla_especial == 'l':
                        puntuacion += self.puntuacion_fichas[ficha]*2
                    elif  casilla_especial == 'L':
                            puntuacion += self.puntuacion_fichas[ficha]*3
                    else:
                        puntuacion += self.puntuacion_fichas[ficha]
                        #en este caso la casilla multiplica
                        if casilla_especial == 'W':
                            palabra_multiplicador *= 3
                        else:
                            palabra_multiplicador *= 2


        puntuacion *= palabra_multiplicador
        if fichas_atril_usadas == 7:
            puntuacion += 20

        return puntuacion

    def palabraValida(self, palabra):

        #buscamos en el diccionario si la palabra existe
        palabra = palabra.upper()
        rama = self.diccionario_root

        for caracter in palabra:
            if caracter in rama:
                rama = rama[caracter]
            else:
                return False

        return rama['VALID']

class Atril(object):

    def __init__(self):

        with open('data/fichas.json', 'r') as infile:
            self.fichas = json.load(infile)

        self.total_fichas = []
        for ficha, contador in self.fichas.items():
            self.total_fichas += [ficha for _ in range(contador)]


    def grab(self, n_fichas):

        random.shuffle(self.total_fichas)

        #cogemos el numero de fichss para completar el atril y actualizamos las fichas totales
        nuevas_fichas, self.total_fichas = self.total_fichas[:n_fichas], self.total_fichas[n_fichas:]

        return nuevas_fichas


    def __str__(self):

        contador = Counter(self.atril).items()
        contador = sorted(contador, key=lambda x: x[0])

        contador = contador[1:] + contador[:1]
        return ', '.join([letter + ': ' + str(contador) for letter, contar in contador])