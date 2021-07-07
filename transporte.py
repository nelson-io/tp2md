import numpy as np
import cplex
import math
import sys
import string

BIG_NUMBER = 1e6
TOLERANCE = 1e-6

class TransportationData:
    def __init__(self):
        # Tiene la informacion general del problema de transporte:
        # - m = numero de proveedores
        # - n = numero de clientes
        # - production = lista de produccion, i-esima posicion produccion del prov. i.
        # - demands = lista de demandas, j-esima posicion demanda del cliente j.
        # - costs = matriz (list(list(float))) que contieje el costo de enviar una unidad del
        # proveedor i al cliente j. BIGNUMBER es un numero excesivamente grande, usado para modelar
        # la no factibilidad de envio entre un par proveedor-cliente.
        # - var_idx = estructura utilizada para guardar los indices de las variables. En este caso,
        # es un diccionario que tiene como clave una tuple(int,int) y significado int.
        self.m = 3
        self.n = 5 
        self.production = [135.0, 56.0, 93.0]
        self.demands = [62.0, 83.0, 39.0, 91.0, 9.0]
        self.costs = [[132.0, BIG_NUMBER, 97.0, 103.0, 0.0],
                [85.0, 91.0, BIG_NUMBER, BIG_NUMBER, 0.0],
                [106.0, 89.0, 100.0, 98.0, 0.0]]
        self.var_idx = {}


    def __repr__(self):
        pass

def add_demand_constraints(instance,myprob):
    
    # Agregamos una a una las restricciones de demanda.
    # Nos movemos por los clientes (ya que es la restriccion de demanda).
    for j in range(instance.n):
        # Generamos los indices (que al final tambien va a tener m posiciones).
        ind = []
        vals = [1]*instance.m
        # Agregamos en cada caso el indice de la variable que representa al arco (i,j), guardado en var_idx.
        for i in range(instance.m):
            ind.append(instance.var_idx[(i,j)])

        # Igual que en los casos anteriores, con los ind y vals generamos la representacion de la fila y la agregamos.
        # Notar que se hace dentro del "for", porque queremos agregar una restriccion por cada cliente.
        row = [ind,vals]
        myprob.linear_constraints.add(lin_expr = [row], senses = ['E'], rhs = [instance.demands[j]])


def add_production_constraints(instance,myprob):

    # Agregamos una a una las restricciones de produccion.
    for i in range(instance.m):
        ind = []
        vals = [1]*instance.n
        for j in range(instance.n):
            ind.append(instance.var_idx[(i,j)])

        row = [ind,vals]
        myprob.linear_constraints.add(lin_expr = [row], senses = ['E'], rhs = [instance.production[i]])

def add_constraint_matrix(instance,myprob):

    # Agregamos las restricciones de demanda.
    add_demand_constraints(instance, myprob)

    # Agregamos las restricciones de produccion.
    add_production_constraints(instance, myprob)

def generate_variables(instance,myprob):

    # Generamos la estructura que mapea (i,j) ---> indice de variable.
    n_vars_tot = instance.n*instance.m
    obj = [0]*n_vars_tot
    lb = [0]*n_vars_tot
    names = []

    # var_cnt va a ser el valor que va llevando la cuenta de cuantas variables agregamos hasta el momento.
    var_cnt = 0
    # Generamos los indices.
    for i in range(instance.m):
        for j in range(instance.n):
            # Tenemos los dos for anidados porque necesitamos las combinaciones de (i,j), i = 1,...,m y j = 1,...,n.
            # Definimos el valor para (i,j). 
            instance.var_idx[(i,j)] = var_cnt
            # Obtenemos el costo.
            obj[var_cnt] = instance.costs[i][j]
            names.append('x_' + str(i) + str(j))
            # Incrementamos el proximo indice no usado..
            var_cnt += 1

    # Agregamos las variables al modelo.
    myprob.variables.add(obj = obj, lb = lb, names = names)

def populate_by_row(instance,myprob):

    # Generamos y agregamos las variables.
    generate_variables(instance, myprob)

    # Seteamos el problema de minimizacion.
    myprob.objective.set_sense(myprob.objective.sense.minimize)

    # Agregamos la matrix de restricciones.
    add_constraint_matrix(instance, myprob)

    # Escribimos el LP (debug)
    myprob.write('test_transportation.lp')

def solve_lp(instance, myprob):

    # Resolvemos el LP.
    myprob.solve()

    # Obtenemos la info de la solucion.
    x = myprob.solution.get_values()
    f_obj = myprob.solution.get_objective_value()

    print('Funcion objetivo: ', f_obj)
    print('x: ', x)

    # Imprimimos variables usadas.
    for i in range(instance.m):
        for j in range(instance.n):
            val = x[instance.var_idx[(i,j)]]
            if val > TOLERANCE:
                print('x_' + str(i) + '_' + str(j) + ': ', val)


def main():

    # Obtenemos la informacion de la instancia.
    instance = TransportationData()

    # Definimos el problema de cplex.
    prob_lp = cplex.Cplex()

    # Armamos el modelo.
    populate_by_row(instance,prob_lp)

    # Resolvemos el modelo.
    solve_lp(instance,prob_lp)

if __name__ == '__main__':
    main()
    


