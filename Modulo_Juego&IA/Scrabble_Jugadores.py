# -*- coding: utf-8 -*-
from collections import namedtuple
from multiprocessing.dummy import Pool
from Scrabble_Elementos import Reglas
from exceptions import InvalidPlacementError
#from exepciones import ColocacionInvalida

import sys

class Jugador(object):

    def __init__(self, id, atril, reglas, nombre=None):

        while nombre is None:
            nombre = input("Introduce tu nombre: ".format(id))
            if nombre.isspace():
                print("El nombre no puede contener espacios")
                nombre=None

        self.nombre= nombre
        self.id = id

        #creamos un regsitro de las palabras creadas necesario para
        #el conteo de la puntuacion final

        self.palabra_historial = []
        self.palabra_puntuacion = []
        self.atril = atril
        self.reglas = reglas

    def __str__(self):

        return self.nombre

    def siguienteMovimiento(self, tablero_estado):
        pass

    def mostrarMovimiento(self, tablero_estado):
        def eliminarFichasUsadas(movimiento):

            coordenadas, palabra, direccion = movimiento.coordenadas, movimiento.palabra, movimiento.dir
            if coordenadas == (-2, -2):
                for ficha in movimiento.palabra:
                    self.atril.remove(ficha)

            else:
                abajo, derecha = (direccion == 'A' , direccion == 'D')
                y, x = coordenadas
                for i, ficha in enumerate (palabra.upper()):
                    if tablero_estado[y+i*abajo][x+i*derecha]==' ':
                        if ficha not in self.atril and '?' in self.atril:
                            ficha = '?'
                        self.atril.remove(ficha)

        #actualizamos al siguiente movimiento
        #print("Estoy aqui 2")
        movimiento = self.siguienteMovimiento(tablero_estado)
       # print("Estoy aqui 2")
        #comprobamos la senyal de paso de turno
        if movimiento.coordenadas != (-1,-1):
            eliminarFichasUsadas(movimiento)

        return movimiento

    def cogerFichas(self, fichas_nuevas):

        self.atril += fichas_nuevas

    def setearAtril (self, atril):

        self.atril = atril

class Humano(Jugador):

    def __init__(self, id, atril, reglas, nombre=None):
        Jugador.__init__(self, id, atril, reglas, nombre)

    def siguienteMovimiento(self, tablero_estado):
        #print("soy el humano")
        #comprueba si el jugador tiene las fichas necesarias para formar la palabra
        def atrilActual(movimiento):

            atril_copia = self.atril.copy()
            abajo, derecha = (movimiento.dir == 'A' , movimiento.dir == 'D')
            y, x = movimiento.coordenadas

            #Comprobamos que la palabra cabe en el sitio
            if max(y+abajo*len(movimiento.palabra), x+derecha*len(movimiento.palabra)) >14:
                return False

            for i, ficha in enumerate (movimiento.palabra.upper()):
                #si la casilla esta vacia se elimina la ficha de nuestro atril (se coloca en el tablero)
                if movimiento.coordenadas == (-2,-2) or tablero_estado[y+i*abajo][x+i*derecha] == ' ':
                    if ficha not in self.atril and '?' in self.atril:
                        ficha = '?'
                    try:
                        atril_copia.remove(ficha)
                    except ValueError:
                        return False

            return True

        Movimiento = namedtuple('movimiento', 'coordenadas dir palabra')
        print("Atril: ["+ str(self.atril) + "]")

        while True:
            movimiento_jugador = input("Juega: (Recuerda y, x ,A/D y palabra): ")
            n_segmentos = movimiento_jugador.lower().strip().split(' ')

            if len(n_segmentos) ==1:
                if n_segmentos[0] == 'pasar':
                    return Movimiento((-1,-1),'','')
                elif n_segmentos[0] == 'salir':
                    return Movimiento((-3, -3),'','')
                elif n_segmentos[0] == 'ayuda':
                    print("\n".join(["Commandos:" "'salir' sale del juego", "'saltar' pasar turno", "'X Y A/D PALABRA' juegas la palabra"]))
                else:
                    print("Commando {} no encontrado.".format(n_segmentos[0]))

            elif len(n_segmentos) == 4:
                x,y, direccion, palabra = n_segmentos
                direccion = direccion.upper()
                print("El movimeinto es: {}".format(n_segmentos))
                movimiento = Movimiento ((int(y,16), int(x,16)),direccion, palabra.upper())
                if movimiento.coordenadas[0] < 0 or movimiento.coordenadas[0] < 0 or movimiento.coordenadas[1] > 14  or movimiento.coordenadas[1] > 14:
                    print("El movimiento esta fuera del tablero")
                elif direccion != 'A' and direccion != 'D':
                    print("La dirección no es correcta, debe ser 'A'(arriba a bajo) o 'D'(de izquierda a dereha)")
                else:
                    try:
                        #comprobamos que el jugador tiene las letras
                        if not atrilActual(movimiento):
                            print("El atril del jugador no contiene las letras necesaria para formar la palabra")
                        else:
                            #comprobamos si la palabra existe y tiene sitio suficiente
                            if self.reglas.puntuacionMovimiento(movimiento, tablero_estado) < 0:
                                print("La palabra formada no es valida o no cabe")
                            else:
                                return movimiento
                    except InvalidPlacementError:
                        print (InvalidPlacementError)
            else:
                print ("Commando {} no reconocido. Escribe 'ayuda' para mas informacion".format(n_segmentos))


class Robot(Jugador):

    def __init__(self,id, atril, reglas, nombre="ScrabbMaster"):
        Jugador.__init__(self,id,atril, reglas, nombre)

    def encontrarPalabras(self, atril=None, rama_inicial=None, fichas_fijas=(),pos=0, longuitud_min=2, longuitud_max=15):
        #print("Estamos buscando la palabra")
        if pos > longuitud_max:
            return []

        if atril is None:
            atril = self.atril.copy()

        if rama_inicial is None:
            rama_inicial = self.reglas.diccionario_root

        assert (len(fichas_fijas) == 1 or all([fichas_fijas[i][1] < fichas_fijas[i+1][1] for i in range (len(fichas_fijas)-1)]))

        if rama_inicial['VALID'] and len(rama_inicial['WORD']) >= longuitud_min and len(atril) < len (self.atril):
            if not fichas_fijas or fichas_fijas[0][1] > len(rama_inicial['WORD']):
                palabras_validas = [rama_inicial['WORD']]
            else:
                palabras_validas = []
        else:
            palabras_validas = []

        if fichas_fijas  and fichas_fijas[0][1] == pos:
            if fichas_fijas[0][0] in rama_inicial:
                palabras_validas += self.encontrarPalabras(atril=atril, rama_inicial= rama_inicial[fichas_fijas[0][0]],fichas_fijas=fichas_fijas[1:], pos = pos+1, longuitud_min=longuitud_min, longuitud_max=longuitud_max)

        else:
            for ficha in set(atril):
                fichas_nuevas = atril.copy()
                fichas_nuevas.remove(ficha)
                if ficha == '?':
                    palabras_con_espacios = []
                    for clave, valor in rama_inicial.items():
                        if clave != 'VALID' and clave !='WORD':
                            palabras_con_espacios += self.encontrarPalabras(atril=fichas_nuevas,rama_inicial = rama_inicial[clave], pos=pos+1, longuitud_min=longuitud_min, longuitud_max=longuitud_max,fichas_fijas=fichas_fijas)

                    palabras_con_espacios= [palabra[:pos] + palabra[pos].lower()+ palabra[pos+1:] for palabra in palabras_con_espacios]
                    palabras_validas += palabras_con_espacios

                else:
                    if ficha in rama_inicial:
                        palabras_validas += self.encontrarPalabras(atril=fichas_nuevas,rama_inicial = rama_inicial[ficha], pos=pos+1, longuitud_min=longuitud_min, longuitud_max=longuitud_max,fichas_fijas=fichas_fijas)

        return palabras_validas


    def parametrosMovimiento(self, coordenadas, direccion, tablero_estado):
        #print("Estoy aqui 5")
        def estaAislado(y, x): #saber si no hay letras alrededor

            if (y, x) == (7, 7):
                return False


            x_min, x_max = max(x - 1, 0), min(x + 1, 14)
            y_min, y_max = max(y - 1, 0), min(y + 1, 14)

            for y_cer in range(y_min, y_max +1):
                if tablero_estado[y_cer][x]!=' ':
                    return False
            for x_cer in range(x_min, x_max +1):
                if tablero_estado[y][x_cer] !=' ':
                    return False
            return True


        y_ini, x_ini = coordenadas
        y, x = coordenadas
        fichas_fijas = []
        atril_rem = len(self.atril)

        fichas_validar = -1

        if direccion == 'A':

            if y > 0 and tablero_estado[y-1][x] != ' ':
                return -1, []
            #print("Estoy aqui final")
            while y < 15 and (atril_rem or tablero_estado[y][x] != ' '):
                if fichas_validar == -1:
                    if not estaAislado(y, x):
                        fichas_validar =  y - y_ini +1
                if tablero_estado[y][x] == ' ':
                    atril_rem -= 1
                else:
                    fichas_fijas.append((tablero_estado[y][x], y - y_ini))

                y += 1
                print("soy la y: {}".format(y))
            #print("Movimiento Abajo: {}{}".format(x,y))
            print("fichas fijas y: {}".format(fichas_fijas))
            return fichas_validar, fichas_fijas

        else:
            if x > 0 and tablero_estado[y][x-1] != ' ':
                return -1, []
            #print("Estoy aqui final2")
            while x < 15 and (atril_rem or tablero_estado[y][x] != ' '):
                #print("Estoy aqui")
                if fichas_validar == -1:
                    if not estaAislado(y, x):
                        fichas_validar = x - x_ini + 1
                if tablero_estado[y][x] == ' ':
                        atril_rem -= 1
                else:
                    fichas_fijas.append((tablero_estado[y][x], x - x_ini))
                x += 1
                print("soy la x: {}".format(x))
            #print("Estoy aqui final3")
            #print("Movimiento Abajo: {}{}".format(x,y))
            print("fichas fijas x: {}".format(fichas_fijas))
            return fichas_validar, fichas_fijas


    def posicionesValidas(self, tablero_estado):

        #print("Estoy aqui 2")
        posicion = namedtuple('posicion', 'coordenadas dir min max fijas')

        parametros_validos = []

        for y in range(15):
            for x in range(15):
                for direccion in ['A', 'D']:
                    print("entro {}".format(direccion))
                    longuitud_min, fichas_fijas = self.parametrosMovimiento((y,x), direccion, tablero_estado)
                    if longuitud_min !=  -1 :
                        #print("Estoy aqui 8")
                        if direccion == 'A':
                            parametros_validos.append(posicion((y,x), direccion, longuitud_min, 15-y, fichas_fijas))
                        else:
                            parametros_validos.append(posicion((y,x), direccion, longuitud_min, 15-x, fichas_fijas))
        #print("Estoy aqui ole")
        return parametros_validos



    def siguienteMovimiento(self, tablero_estado):

        #print("Estoy aqui 2")
        posiciones_validas = self.posicionesValidas(tablero_estado)

        Movimiento = namedtuple('movimiento', 'coordenadas dir palabra')

        movimientos_validos = []
        for valido in posiciones_validas:

            palabras_validas = self.encontrarPalabras(fichas_fijas=valido.fijas, longuitud_min=max(2,valido.min), longuitud_max=valido.max)
            movimientos_validos  += [Movimiento(valido.coordenadas, valido.dir, palabra) for palabra in palabras_validas]

        puntuacion_movimientos = [(movimiento, self.heuristicaMovimiento(movimiento,tablero_estado)) for movimiento in movimientos_validos]
        puntuacion_movimientos = sorted(puntuacion_movimientos, key=lambda x: x[1], reverse=True)

        if puntuacion_movimientos and puntuacion_movimientos[0][1] > 0:
            self.palabra_historial.append(puntuacion_movimientos[0][0].palabra)
            self.palabra_puntuacion.append(puntuacion_movimientos[0][1])
            return puntuacion_movimientos[0][0]
        else:
            return Movimiento((-1, -1), '', '')



    def heuristicaMovimiento(self, movimiento, tablero_estado):

        return self.reglas.puntuacionMovimiento(movimiento, tablero_estado)



