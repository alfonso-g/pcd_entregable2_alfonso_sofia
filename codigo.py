from abc import ABC, abstractmethod
from functools import reduce
import math
import random
import time
from datetime import datetime

### Usamos el patrón Singleton para cumplir el requisito 1.
class Gestor:
    '''
    Descripción: Patrón Singleton para asegurarnos de tener solo una instancia de la clase Gestor.
    Métodos: 
        obtener_instancia: devuelve la instancia del Gestor.
        iniciar_proceso: inicia todo el proceso solicitado por el enunciado.
    '''
    _unicaInstancia = None
    def __init__(self):
        pass

    @classmethod
    def obtener_instancia(cls):
        if not cls._unicaInstancia:
            cls._unicaInstancia = cls
        return cls._unicaInstancia
    
    def iniciar_proceso():
        sensor = Sensor('Invernadero')
        observer = Operator('Observer')
        sensor.register_observer(observer)
        crecimiento = Crecimiento()
        umbral = Umbral(crecimiento)
        estadistico = Estadisticos(umbral)
        simular_sensor(sensor)
        
### Usamos el patrón Observer para cumplir el requisito 2.
class Observable:
    '''
    Descripción: clase de la que heredan los distintos observables del patrón Observer.
    Métodos:
        register_observer(observer: Observer): añade a la lista de observers un observer nuevo.
        remove_observer (observer: Observer): elimina un observer de la lista de observers.
        notify_observers(data): recorre toda la lista de observers notificándolas con los nuevos datos.
    '''
    def __init__(self):
        self._observers = []

    def register_observer(self, observer):
        if  isinstance(observer, Observer):
            self._observers.append(observer)
        else:
            raise Exception('No se puede registrar un objeto que no es un Observer.')

    def remove_observer(self, observer):
        if  isinstance(observer, Observer):
            self._observers.remove(observer)
        else:
            raise Exception('No se puede eliminar un objeto que no es un Observer.')

    def notify_observers(self, data):
        for observer in self._observers:
            observer.update(data)

class Observer(ABC):
    '''
    Descripción: clase de la que heredan los distintos observers del patrón Observer.
    Métodos:
        update(data)
    '''
    @abstractmethod
    def update(self, data):
        pass

class Sensor(Observable):
    '''
    Descripción: clase que simulará el envío de datos del sensor.
    Atributos: 
        name(str): nombre del sensor.
    Métodos:
        set_value(value): notifica a la lista de observers con el nuevo valor.
    '''
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.value = 0

    def set_value(self, value):
        self.value = value
        self.notify_observers(self.value)

class Operator(Observer):
    '''
    Descripción: clase que recibe los datos enviados por el sensor y se encarga de su procesamiento.
    Atributos:
        name(str): nombre del operador.
    Métodos:
        update(data): cuando el sensor envía datos, se encarga de procesarlos.
    '''
    def __init__(self, name):
        self.name = name
        self.historico = []
        self._crecimiento = Crecimiento()
        self._umbral = Umbral(self._crecimiento)
        self._estadistico = Estadisticos(self._umbral)

    def update(self, data):
        self.historico.append(data)
        temperaturas = list(map(lambda x: x[1], self.historico))
        self._estadistico.handle_request(temperaturas)
        
### Usamos el patrón Chain of responsability para cumplir el requisito 3.
class Handler:
    '''
    Descripción: clase de la que heredan los distintos Handler de la cadena de responsabilidad.
    Atributos:
        successor(Handler): por defector None, establece el siguiente Handler en la cadena de responsabilidad.
    Métodos:
        handler_request
    '''
    def __init__(self, succesor=None):
        if isinstance(succesor, Handler) or not succesor:
            self.succesor=succesor
        else:
            raise Exception('El siguiente elemento en la cadena de de responsabilidad debe de ser un Handler')
    def handle_request(self,request):
        pass
    
class Estadisticos(Handler):
    '''
    Descripción: Handler que se encarga del primer punto del requisito 3.
    Métodos: 
        handle_request(request): imprime la media y la desviacion estándar y llama al siguiente Handler de la cadena de responsabilidad.
    '''
    def handle_request(self,request):
        if len(request) < 12:
            data = request
        else:
            data = request[-12:]
        contexto = ContextoCalculoEstadisticos(data)
        media = Media('media')
        mediana = Mediana('mediana')
        maximo = Maximo('maximo')
        contexto.establecerEstrategia(media)
        media, de = contexto.calculoEstadisticos()
        print(f"La temperatura media de los ultimos 60 segundos es: {media}\nLa desviación estandar es: {de}")
        if self.succesor:
            self.succesor.handle_request(request)

class Umbral(Handler):
    '''
    Descripción: Handler que se encarga del segundo punto del requisito 3.
    Métodos: 
        handle_request(request): alerta en caso de que el dato sea mayor que 32 (nuestro umbral) y llama al siguiente Handler de la cadena de responsabilidad.
    '''    
    def handle_request(self, request):
        if request[-1] > 32:
            print('¡ALERTA! La temperatura ha sobrepasado los 32 grados. ¡ALERTA!')
        if self.succesor:
            self.succesor.handle_request(request)


class Crecimiento(Handler):
    '''
    Descripción: Handler que se encarga del tercer punto del requisito 3.
    Métodos: 
        handle_request(request): alerta en caso de que la temperatura haya ascendido más de diez grados en los últimos 30 segundos y llama al siguiente Handler de la cadena de responsabilidad.
    '''    
    def handle_request(self, request):
        if len(request) >= 6:
            if request[-1] - request[-6] >= 10:
                print('¡ALERTA! La temperatura ha ascendido más de diez grados en los últimos 30 segundos. ¡ALERTA!')
        if self.succesor:
            self.succesor.handle_request(request)

### Usamos el patrón Strategy para cumplir el requisito 4.
class ContextoCalculoEstadisticos:
    '''
    Descripción: clase a través de la que calculamos estadísticos y establecemos con que estrategia calcularlos.
    Atributos:
        datos(List of int): datos de los que calcularemos los estadísticos
        estrategia(Estrategia): por defecto None, estrategia con la que calcularemos los estadísticos.
    Métodos:
        establecerEstrategia(estrategiaNueva: Estrategia): establece la estrategia con la que calcularemos los estadísticos.
        calculosEstadisticos(): calcula los estadísticos con la estrategia establecida.
    '''
    def __init__(self, datos, estrategia = None):
        self.datos = datos
        self.estrategia = estrategia

    def establecerEstrategia(self, estrategiaNueva):
        if isinstance(estrategiaNueva, Estrategia):
            self.estrategia = estrategiaNueva
        else: 
            raise Exception('La estrategia nueva debe de ser un objeto Estrategia')

    def calculoEstadisticos(self):
        return self.estrategia.calculo(self.datos)

class Estrategia(ABC):
    '''
    Descripción: clase de la que heredan las distintas estrategias.
    Métodos:
        calculo(datos)
    '''
    @abstractmethod
    def calculo(datos):
        pass


class Media(Estrategia):
    '''
    Descripción: estrategia que calcula la media y la desviación estándar.
    Atributos:
        nombre(str): nombre de la estrategia.
    Métodos:
        calculo(datos: List of int): devuelve la media y la desviación estándar redondeados a dos decimales.
    '''
    def __init__(self, nombre):
        self.nombre = nombre

    def calculo(self, datos):
        media = reduce(lambda x, y: x + y, datos) / len(datos)
        desviaciones = list(map(lambda x: (x - media) ** 2, datos))
        # Calcular la suma de los cuadrados de las desviaciones
        suma_cuadrados_desviaciones = reduce(lambda x, y: x + y, desviaciones)
        # Calcular la desviación estándar
        desviacion_estandar = math.sqrt(suma_cuadrados_desviaciones / len(datos))
        return round(media, 2), round(desviacion_estandar, 2)

class Mediana(Estrategia):
    '''
    Descripción: estrategia que calcula la mediana.
    Atributos:
        nombre(str): nombre de la estrategia.
    Métodos:
        calculo(datos: List of int): devuelve la mediana.    
    
    '''
    def __init__(self, nombre):
        self.nombre = nombre
    
    def calculo(self, datos):
        lista_ordenada = sorted(datos)
        longitud = len(lista_ordenada)
    
        if longitud % 2 == 0:
            # Si la longitud de la lista es par, calcular el promedio de los dos valores centrales
            medio_1, medio_2 = list(map(lambda x: lista_ordenada[x], [(longitud // 2) - 1, (longitud // 2)]))
            return (medio_1 + medio_2) / 2
        else:
            # Si la longitud de la lista es impar, la mediana es el valor central
            return lista_ordenada[longitud // 2]

class Maximo(Estrategia):
    '''
    Descripción: estrategia que calcula el máximo y el mínimo.
    Atributos:
        nombre(str): nombre de la estrategia.
    Métodos:
        calculo(datos: List of int): devuelve el máximo y el mínimo.
    '''
    def __init__(self, nombre):
        self.nombre = nombre
    
    def calculo(self, datos):
        maximo = max(datos)
        minimo = min(datos)
        return maximo, minimo


def simular_sensor(sensor):
    while True:
        temperatura = round(random.uniform(10, 35), 2)
        tiempo = datetime.now()
        sensor.set_value((tiempo, temperatura))
        time.sleep(5)


if __name__ == '__main__':
    g = Gestor.obtener_instancia()
    Gestor.iniciar_proceso()