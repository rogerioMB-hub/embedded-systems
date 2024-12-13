"""
Created on Thu Nov  4 17:45:18 2024

@author: rmbra
"""
import random as rnd

class individuo(object):
    
    def __init__(self, id_, sz_dna_):
        self.id=id_
        self.size_dna=sz_dna_
        self.dna=list()
        #self.pesos=list()
        self.fitness=0
        
    def gera_individuo(self):    
        for pos_dna in range(self.size_dna):
            self.dna.append(rnd.randint(0, 1))
    
    def decode(self, pesos):
        for index in range(self.size_dna):
            self.fitness=self.fitness+(pesos[index]*self.dna[index])

    def show(self):
        print("Individuo[",self.id,"]=", self.dna,", decode= " ,self.fitness)
    

class populacao(object):
    
    def __init__(self, gen_, sz_ind_, sz_pop_):
        self.gen=gen_
        self.sz_ind=sz_ind_
        self.size_pop=sz_pop_
        self.best_ftns = 0
        self.pesos=list()
        self.pop=list()
        self.sumweight = 0
    
    def calc_pesos(self):
        for index in range(self.sz_ind):
            valor=1<<(self.sz_ind-index-1)
            self.pesos.append(valor)
        self.sum_weight = sum(self.pesos)
            
    def show_pesos(self):
        print("Pesos=", self.pesos, "w/ sum =", self.sum_weight)
    
    def gera_pop(self):                 
        for i in range(self.size_pop):
            ind = individuo(i,self.sz_ind)
            ind.gera_individuo()
            self.pop.append(ind)
            
    def decode_pop(self):
        self.calc_pesos()
        self.show_pesos()
        
        for ind in self.pop:
            ind.decode(self.pesos)

    def show(self):
        for ind in self.pop:
            ind.show()
        
            
            
pop = populacao(0,4,8)
pop.gera_pop()
pop.decode_pop()
pop.show()




