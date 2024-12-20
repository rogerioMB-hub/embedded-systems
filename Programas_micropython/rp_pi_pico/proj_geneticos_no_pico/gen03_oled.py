"""
Created on Thu Nov  4 17:45:18 2024

@author: rmbra
"""
import random as rnd
import time
# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-analog-inputs-micropython/
from machine import ADC, Pin, I2C #usa I2C hardwarev - pinos 9 e 8
from time import sleep
import ssd1306


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

    def show_me(self):
        print("Individuo[",self.id,"]=", self.dna,", decode= " ,self.dec,", nv= ",self.norm_value,", err2= ",self.err2,", ftns= " ,self.ftns)
    
class populacao(object):
    
    def __init__(self, gen_, sz_ind_, sz_pop_, norm_ref_, pclones_, pxovers_, tmut_):
        self.gen=gen_
        self.sz_ind=sz_ind_
        self.size_pop=sz_pop_
        self.norm_ref = norm_ref_
        self.pclones = pclones_
        self.pxovers = pxovers_
        self.best_ftns = 0
        self.pesos=list()
        self.pop=list()
        self.npop=list()
        self.sumweight = (1<<self.sz_ind)-1
        self.conv_factor = 1.0 / self.sumweight
        self.err2_min = 1000
        self.emq = 0.0
        self.ftns_list=list()
        self.int_ftns=list()
        self.ftns_total=0.0
        self.idx_best = 0
        self.ftns_dict={}
        self.sorted=list()
        self.nclones = 2
        self.nxovers = 2
        self.tmut = tmut_
        self.nrnds = self.size_pop - self.nclones - self.nxovers
        self.selected=list()
        self.hist=list()
                

    def calc_pesos(self):
        self.pesos=[]
        for index in range(self.sz_ind):
            valor=1<<(self.sz_ind-index-1)
            self.pesos.append(valor)

    def show_pesos(self):
        print("Pesos=", self.pesos, "- (", self.sz_ind, " bits), w/ sum =", self.sumweight)
    
    def gera_pop_rnd(self, n, kind):                 
        for i in range(n):
            ind = individuo(i,self.sz_ind)
            ind.gera_individuo()
            if kind==0:
                self.pop.append(ind)
            else:
                self.npop.append(ind)
            
    def decode_pop(self):
        if (len(self.pesos)<1):
            self.calc_pesos()
            self.show_pesos()
        
        for ind in self.pop:
            if (ind.dec==0):
                ind.decode(self.pesos)
            
    def get_decode(self, ind_):
        return self.pop[ind_].dec
    
    # valor normalizado é o quanto, de 0 a 1, corresponde o código em sua resolução - fenótipo)
    def calc_norm_value(self):
        for ind in self.pop:
            ind.norm_value = ind.dec * self.conv_factor

    def show(self):
        for ind in self.pop:
            ind.show_me()
    
    def show_npop(self):
        for ind in self.npop:
            ind.show_me()
        
    def calc_err2(self):
        for ind in self.pop:
            ind.err2 = ( self.norm_ref - ind.norm_value ) ** 2
            
    def calc_emq(self):
        self.emq = 0.0
        for ind in self.pop:
            self.emq = self.emq + ind.err2
            if ind.err2 < self.err2_min:
                self.err2_min = ind.err2
        self.emq = (self.emq / self.size_pop) ** (1/2)
    
    def calc_ftns(self):
        self.ftns_list=[]
        self.ftns_total = 0.0
        for ind in self.pop:
            ind.ftns = 1 - ind.err2
            self.ftns_list.append(ind.ftns)
            self.ftns_total = sum(self.ftns_list)
            
    def create_dict(self):
        self.ftns_dict={}
        for i in range(self.size_pop):
            self.ftns_dict[i]=self.pop[i].ftns
        
    def sort_dict(self):
        self.sorted=[]
        self.sorted = sorted(self.ftns_dict.items(), key=lambda item: item[1], reverse=True)
    
    def get_best(self):
        self.idx_best = self.sorted[0][0]
        #print("Best in population: ",self.idx_best, "w/ ftns=",self.sorted[0][1])
        #self.pop[self.idx_best].show_me()
        return self.pop[self.idx_best]
        
    def log_best(self):
        self.hist.append(self.pop[self.idx_best].ftns)
        
    def show_best(self):
        print("Best in population: ",self.idx_best, "w/ ftns=",self.sorted[0][1])
        self.pop[self.idx_best].show_me()
        #print(self.sorted)
    
    def integration_ftns(self):
        self.int_ftns=[]
        self.selected=[]
        
        a=0
        for i in range(len(self.pop)):
            a+=self.pop[i].ftns
            self.int_ftns.append(a)
            
    def roleta(self):
        while len(self.selected)<self.nxovers:
            sorteio=rnd.random()*self.ftns_total
            #print(sorteio)
            for idc in range(len(self.int_ftns)):
                if self.int_ftns[idc]>sorteio:
                    idc=idc-1
                    break
            if idc<0:
                idc=0

            self.selected.append(idc)
    
    def crossover_pares(self,idx_par):
        ip1=2*idx_par
        ip2=ip1+1
        
        f1 = individuo(99,self.sz_ind)
        f2 = individuo(99,self.sz_ind)
        
        corte=rnd.randint(1,self.sz_ind-2)
        
        #print("Corte ",corte)
        
        p1=self.pop[self.selected[ip1]]
        p2=self.pop[self.selected[ip2]]
        
        #print("Pais",p1.dna, p2.dna)
        
        idx=0
        for idx in range(corte):
            if (rnd.random()<self.tmut):
                f1.dna.append(rnd.randint(0, 1))
                f2.dna.append(rnd.randint(0, 1))
            else:
                f1.dna.append(p2.dna[idx])
                f2.dna.append(p1.dna[idx])
            
        idx=idx+1
        
        while len(f1.dna)<self.sz_ind:
            if (rnd.random()<self.tmut):
                f1.dna.append(rnd.randint(0, 1))
                f2.dna.append(rnd.randint(0, 1))
            else:
                f1.dna.append(p1.dna[idx])
                f2.dna.append(p2.dna[idx])
            idx=idx+1
                
        #print("Filhos", f1.dna, f2.dna)
        
        self.npop.append(f1)        
        self.npop.append(f2)  
        
    #def gen_rnd_list(self, n, sz):  
    #    x=range(n)
    #    rnd_set=set()
    #    while (len(rnd_lst)<sz)
    #       rnd_set.add(random.choice(x))
    #    return rnd_set

    def iniciate_new_pop(self):
        self.npop = []
        
        self.nclones = int(round(self.size_pop * self.pclones / 100))
        if (self.nclones<2):
            self.nclones=2
        
        self.nxovers = int(round(self.size_pop * self.pxovers / 100))
        if (self.nxovers<2):
            self.nxovers=2
                
        if ((self.nxovers % 2)==1):
            self.nxovers = self.nxovers + 1
                    
        if (self.nxovers > (self.size_pop - self.nclones)):
            self.nxovers = self.size_pop - self.nclones
            if ((self.nxovers % 2)==1):
                self.nxovers = self.nxovers - 1
        
        self.nrnds = self.size_pop - self.nclones - self.nxovers
        
        #print("Nclones =", self.nclones, "Nxovers =", self.nxovers, "Nrnds =", self.nrnds )
        
        # gera individuos clones, selecionando os melhores fitness
        #self.npop.append(self.pop[self.sorted[0][0]])
        for i,f in self.sorted[:self.nclones]:
            self.npop.append(self.pop[i])
            #print(i,"added")
        
        #gera o acumulado do fitness para depos realizar a roleta
        self.integration_ftns()
        #aplica a roleta para selecionar individuos para cruzamento
        self.roleta()
        #individuos guardados em self.selected (somente os indices de pop)              
        
        for s in range(len(self.selected)/2):
            self.crossover_pares(s)
        
        # gera indivíduos com formação aleatória    
        self.gera_pop_rnd(self.nrnds, 1)
        
    def transfer_npop2pop(self):
        self.pop=[]
        x=0
        for ind in self.npop:
            ind.id=x
            self.pop.append(ind)
            x=x+1
            
        self.npop=[]
        
        

ADC0 = ADC(Pin(26))
ADC1 = ADC(Pin(27))
conv_factor = 3.3 / 65535

# usando I2C hardware com pinos originais 9 e 8
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)

oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
oled.text('Conv_ADC', 0, 0)



inicio = time.ticks_us()

sz_ind = 12
sz_pop = 10
pclones = 10
pxovers = 50
tmut = 0.1 / 100.0

leitura_adc = ADC0.read_u16()
#leitura_adc = 32767
volts = leitura_adc * conv_factor
norm_v = volts / 3.3



i_best = individuo(0,sz_ind)
gen=0
erro = 1
#min_erro = 1.0 / 65535
min_erro = 0.01/100.0
while ((gen<200) and (erro>min_erro)):
    #print ("Gen=", gen)

    if (gen==0):
        pop = populacao(0,sz_ind,sz_pop,norm_v,pclones,pxovers,tmut)
        pop.gera_pop_rnd(sz_pop, 0)
    else:   
        pop.iniciate_new_pop()
        #pop.show_npop()
        #pop.show_pesos()
        pop.gen = gen
        pop.transfer_npop2pop()
        
    pop.decode_pop()
    pop.calc_norm_value()
    pop.calc_err2()
    pop.calc_emq()
    pop.calc_ftns()
    #pop.show()
    #print("EMQ da pop = ", pop.emq)
    pop.create_dict()
    pop.sort_dict()
    i_best = pop.get_best()
    #pop.show_best()
    pop.log_best()
    erro = abs((pop.norm_ref - i_best.norm_value)/pop.norm_ref)
    gen+=1
    if ((gen>0) and ((gen%50)==0)):
        pop.tmut = pop.tmut*2
    
    if ((gen%50)==0):
        print("Erro% = ", abs((volts-(i_best.norm_value * 3.3))/volts), "% - ", min_erro)
    
    
fim = time.ticks_us()

pop.show_best()
print("Last gen = ", gen-1)
print("Best norm  value:", i_best.norm_value)
print("Predict volt = ", i_best.norm_value * 3.3, "/ Read volt = ", volts)
print("Erro% = ", abs((volts-(i_best.norm_value * 3.3))/volts), "% - ", min_erro)
print(pop.hist)
print((fim -inicio)/1000.0,"ms")

# Clear the oled display in case it has junk on it.
oled.fill(0)
# Add some text
oled.text("ADC0: ",5,8)
oled.text(str(round(volts,2)),45,8)
# Add some text
oled.text("ADC1: ",5,18)
oled.text(str(round(i_best.norm_value * 3.3,2)),45,18)
# Finally update the oled display so the image & text is displayed
oled.show()
#sleep(0.1)





