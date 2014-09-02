
from modele import *

class Sim:
    """ Interface de simulation en batch d'un modele. 
        On suppose que tous les parametres de simulation sont interne au modele. 
        Contraintes:
          * la classe Modele est dans modele.py 
          * le seul parametre de Modele.init est un int de duree de la 
            simulation
          * la simulation se fait par une boucle sur Modele.update()
          * la boucle de simulation termine lorsque Modele.update() retourne 
            false
    """
  
    def __init__(self):
        self.days = 5
        self.modele = Modele(self.days) 
        
    def run(self):
        ok=True
        
        while (ok): 
            ok = self.modele.update() 
        
        print("Fin de la simulation")
   
mySim = Sim()
mySim.run()
