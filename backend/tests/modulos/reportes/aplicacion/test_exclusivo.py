"""El candado del registro editable: las operaciones van de a una y una puede llamar a otra."""

import threading
import time

from modulos.reportes.aplicacion.exclusivo import exclusivo


def test_las_operaciones_no_se_pisan():
    dentro, maximo = [0], [0]

    @exclusivo
    def operacion():
        dentro[0] += 1
        maximo[0] = max(maximo[0], dentro[0])
        time.sleep(0.02)
        dentro[0] -= 1

    hilos = [threading.Thread(target=operacion) for _ in range(6)]
    [h.start() for h in hilos]
    [h.join() for h in hilos]
    assert maximo[0] == 1


def test_una_operacion_puede_llamar_a_otra():
    @exclusivo
    def interna():
        return 1

    @exclusivo
    def externa():
        return interna() + 1

    assert externa() == 2
