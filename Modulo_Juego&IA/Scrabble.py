
from Scrabble_Elementos import Tablero, Reglas, Atril
from Scrabble_Jugadores import Humano, Robot
from random import shuffle
import sys

class Scrabble(object):

        """
        Esta clase controla el flujo principal de toda la ejecución: el cambio de turnos
        entre jugadores, las puntuaciones, reglas, etc.
        """

        def __init__(self):

            #Creamos las piezas del juego

            self.reglas = Reglas()
            self.tablero = None
            self.fichas = None
            self.jugadores = []
            self.puntuacion_jugadores = []
            self.humano = 1
            self.robot = 1

        def reiniciarJuego(self):

            #Reinicamos el tablero y los atriles
            self.tablero = Tablero()
            self.fichas = Atril()
            self.jugadores = []




            for i in range(self.humano):
                self.jugadores.append(Humano(id=i+1, atril= self.fichas.grab(7), reglas=self.reglas))

            for i in range(self.robot):
                self.jugadores.append(Robot(id=1 + self.humano + i, atril=self.fichas.grab(7),
                                    reglas= self.reglas, nombre="ScrabbMaster"))





            self.puntuacion_jugadores = [0 for _ in range(len(self.jugadores))]



        def jugarScrabble(self, verbose=False):

            #Bucle principal del juego

            self.reiniciarJuego()

            n_saltos_turno = 0  # Hay que mantener el conteo de turnos consecutivos que se salta

            #shuffle(self.jugadores)

            jugador_ganador = None

            #mientras no se salten 2 turnos seguidos y los jugadores tengan fichas en sus atriles
            while n_saltos_turno < 2 and min([len(jugador.atril) for jugador in self.jugadores]) > 0:

                for j, jugador in enumerate(self.jugadores):

                    if isinstance(jugador, Humano):
                        self.mostrarPuntuacion()
                        print(self.tablero)


                    movimiento = jugador.mostrarMovimiento(self.tablero.estado)
                    #print("Hemos pasado")
                    if movimiento.coordenadas == (-1, -1):
                        n_saltos_turno += 1
                    elif movimiento.coordenadas == (-2, -2):
                        print("El jugador intercambia {} fichas.".format(len(movimiento.palabra)))
                        jugador.cogerFichas(self.fichas.grab(len(movimiento.palabra)))
                    elif movimiento.coordenadas == (-3, -3):
                         print("El jugador {} finaliza el juego.".format(jugador.nombre))
                         exit(0)
                    else:
                        n_saltos_turno = 0

                        self.puntuacion_jugadores[j] += self.reglas.puntuacionMovimiento(movimiento, self.tablero.estado)

                        #Actualizamos el tablero con el movimiento realizado
                        self.tablero.actualizarMovimiento(movimiento)
                        print(self.tablero)
                        n_fichas_coger = 7 - len(jugador.atril)
                        jugador.cogerFichas(self.fichas.grab(n_fichas_coger))

                        if len(jugador.atril) == 0:
                            jugador_ganador = jugador.id
                            if verbose:
                                print("El jugador {} ha utilizado todas sus fichas".format (jugador.nombre))
                            break

            for i, jugador in enumerate (self.jugadores):
                if jugador.id != jugador_ganador:
                    penalizacion = self.reglas.calcularPenalizacion(jugador.atril)
                    if verbose:
                        print("{} pierde {} puntos por mantener las fichas {} en su atril".format(jugador.nombre,penalizacion,','.join(jugador.atril)))		



            if verbose:
                print(self.tablero)
                self.mostrarPuntuacion()


        def mostrarPuntuacion(self):

            #Muestra la puntuación de todos los jugadores

            for i, oponente in enumerate (self.jugadores):
                print("{}: {} puntos".format(oponente.nombre, self.puntuacion_jugadores[i]))

            return None


if __name__ == '__main__':

    if len(sys.argv) ==1:
        juego = Scrabble ()
        juego.jugarScrabble(True)








