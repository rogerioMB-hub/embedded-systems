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
        self.dec=0
        self.norm_value=0.0
        self.err2 = 1.0
        self.ftns = 0.0
        
    def gera_individuo(self):    
        for pos_dna in range(self.size_dna):
            self.dna.append(rnd.randint(0, 1))
    
    def decode(self, pesos):
        for index in range(self.size_dna):
            self.dec=self.dec+(pesos[index]*self.dna[index])

    def show(self):
        print("Individuo[",self.id,"]=", self.dna,", decode= " ,self.dec,", nv= ",self.norm_value,", err2= ",self.err2,", ftns= " ,self.ftns)
    
class populacao(object):
    
    def __init__(self, gen_, sz_ind_, sz_pop_, norm_ref_):
        self.gen=gen_
        self.sz_ind=sz_ind_
        self.size_pop=sz_pop_
        self.norm_ref = norm_ref_
        self.best_ftns = 0
        self.pesos=list()
        self.pop=list()
        self.sumweight = (1<<self.sz_ind)-1
        self.conv_factor = 1.0 / self.sumweight
        self.emq = 0.0
        self.ftns_list=list()
        self.idx_best = 0

    def calc_pesos(self):
        for index in range(self.sz_ind):
            valor=1<<(self.sz_ind-index-1)
            self.pesos.append(valor)

    def show_pesos(self):
        print("Pesos=", self.pesos, "w/ sum =", self.sumweight)
    
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
            
    def get_decode(self, ind_):
        return self.pop[ind_].dec
    
    # valor normalizado é o quanto, de 0 a 1, corresponde o código em sua resolução - fenótipo)
    def calc_norm_value(self):
        for ind in self.pop:
            ind.norm_value = ind.dec * self.conv_factor

    def show(self):
        for ind in self.pop:
            ind.show()
        
    def calc_err2(self):
        for ind in self.pop:
            ind.err2 = ( self.norm_ref - ind.norm_value ) ** 2
        
    def calc_emq(self):
        for ind in self.pop:
            self.emq = self.emq + ind.err2
        self.emq = (self.emq / self.size_pop) ** (1/2)
    
    def calc_ftns(self):
        for ind in self.pop:
            ind.ftns = 1 - ind.err2
            self.ftns_list.append(ind.ftns)
            
    def sort_pop_by_ftns(self):
        # erro pois estou odenando os valores e não pegando os indices dos indovíduos
        self.sorted_list = sorted(self.ftns_list, reverse=True)
    
    def show_best(self):
        self.idx_best = self.sorted_list[0]
        # aqui tem um erro...não é o indice, mas o valor que está indo pra lista ordenada
        print("Best in population: ",self.idx_best)
        pop[self.idx_best].show()
               
    


leitura_adc = 32767
volts = leitura_adc * (3.3 / 65535)
norm_v = volts / 3.3

pop = populacao(0,12,10,norm_v)
pop.gera_pop()
pop.decode_pop()
pop.calc_norm_value()
pop.calc_err2()
pop.calc_emq()
pop.calc_ftns()
pop.show()
print("EMQ da pop = ", pop.emq)
pop.sort_pop_by_ftns()
pop.show_best()




