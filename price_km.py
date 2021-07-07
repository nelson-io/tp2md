# -*- coding: utf-8 -*-
import cplex
import numpy as np
import pandas as pd
from Instance import Instance
TOLERANCE = 0.001



# from Instance import Instance
# import cplex

EPS = 1e-6
def solve_instance_greedy(inst):
    available = [*range(inst.n)]
    assigned = []

    for pasx in range(inst.n):

        pas_dists = [*enumerate([inst.dist_matrix[i][pasx] for i in range(inst.n)])]
        filter_dists = [(i ,j) for i,j in pas_dists if i in available]
        match = min(filter_dists, key = lambda t: t[1])
        assigned.append(match)
        available.remove(match[0])
        
        tot_dist = sum([j for i,j in assigned])
        tuple_selected = [(j,i) for i,j in enumerate([j for j,i in assigned])]
       

    return [tot_dist, tuple_selected]
################## Solucion FCFS greedy ######################


###############################################################

################## Solucion LP ################################
def generate_variables_pr(inst, myprob):
    n_vars_tot = inst.n**2
    obj = [0]*n_vars_tot
    lb = [0]*n_vars_tot
    names = []
    
        # var_cnt va a ser el valor que va llevando la cuenta de cuantas variables agregamos hasta el momento.
    var_cnt = 0
    # Generamos los indices.
    for i in range(inst.n):
        for j in range(inst.n):
            # Tenemos los dos for anidados porque necesitamos las combinaciones de (i,j), i = 1,...,m y j = 1,...,n.
            # Definimos el valor para (i,j). 
            inst.var_idx[(i,j)] = var_cnt
            # Obtenemos el costo.
            obj[var_cnt] = inst.paxs_tot_fare[j]/(inst.dist_matrix[i][j] + inst.paxs_trip_dist[j] + .01)
            names.append('x_' + str(i) + str(j))
            # Incrementamos el proximo indice no usado..
            var_cnt += 1

    # Agregamos las variables al modelo.
    myprob.variables.add(obj = obj, lb = lb, names = names)
    
    
    
# 	''' Genera la matriz de restricciones sobre myprob. Reemplazar pass por el codigo correspondiente.'''
# 	pass
			

def generate_constraints_pr(inst, myprob):
	    
    # Agregamos una a una las restricciones de demanda.
    # Nos movemos por los clientes (ya que es la restriccion de demanda).
    for j in range(inst.n):
        # Generamos los indices (que al final tambien va a tener m posiciones).
        ind = []
        taxi = []
        vals = [1]*inst.n
        # Agregamos en cada caso el indice de la variable que representa al arco (i,j), guardado en var_idx.
        for i in range(inst.n):
            ind.append(inst.var_idx[(i,j)])
            taxi.append(inst.var_idx[(j,i)])

        # Igual que en los casos anteriores, con los ind y vals generamos la representacion de la fila y la agregamos.
        # Notar que se hace dentro del "for", porque queremos agregar una restriccion por cada cliente.
        row = [ind,vals]
        row2 = [taxi, vals]
        myprob.linear_constraints.add(lin_expr = [row], senses = ['E'], rhs = [1])
        myprob.linear_constraints.add(lin_expr = [row2], senses = ['E'], rhs = [1])
	

def populate_by_row_pr(inst, myprob):
    generate_variables_pr(inst, myprob)
    generate_constraints_pr(inst, myprob)
    myprob.objective.set_sense(myprob.objective.sense.maximize)
    myprob.write('out/test_taxis_price.lp')

def solve_lp_pr(inst):

    # Resolvemos el LP.
    myprob = cplex.Cplex()
    populate_by_row_pr(inst,myprob)
    myprob.solve()

    # Obtenemos la info de la solucion.
    x = myprob.solution.get_values()
    f_obj = myprob.solution.get_objective_value()


    # get optimal  i,j 
    opt_i_j = np.reshape(np.array(myprob.solution.get_values()),(inst.n,inst.n))
    # get distances made
    d_made = sum(np.array(inst.dist_matrix) * opt_i_j)
    # get total dist
    total_dist = sum(d_made)
    
    return total_dist
    
###############################################################

#### Implementar funciones auxiliares necesarias para analizar resultados y proponer mejoras.

def main():
    results = []
    inst_types = ['small','medium','large','xl']
    n_inst = ['0','1','2','3','4','5','6','7','8','9']
    for t in inst_types:

#Esquema para ejecutar las soluciones directamente sobre las 40 instancias.
    
        for n in n_inst:
            inst_file = 'input/' + t + '_' + n + '.csv'
            inst = Instance(inst_file)
            f_greedy, x_greedy= solve_instance_greedy(inst)
            f_lp = solve_lp_pr(inst)
            
            results.append([inst_file,f_greedy, f_lp])
                   
    pd.DataFrame(results).to_csv('out/results_price_km.csv')
            
            
			 

# Modificar para ajustar el formato segun la conveninencia del grupo, agregando
# o quitando informacion.
         

if __name__ == '__main__':
	main()









