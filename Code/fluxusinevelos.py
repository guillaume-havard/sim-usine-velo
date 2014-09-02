""" COntient les classes specifique pour l'usine de velo. """

#import math, decimal
from flux import *
#from data import *

class NoeudReceptionCamion(Noeud):
    """
    Noeud qui se désactive aussitôt qu'il a fait une action.
    Correspond à une arrivé ponctuel de beaucoup de materiel.
    """
    
    def __init__(self, id= -1, nom="no name", restart_meme_cycle=True, tailleLot=1):
        """
        
        """
        Noeud.__init__(self, id, nom, restart_meme_cycle)                
        self.tailleLot = tailleLot
        
    def putMatOneLot(self):
        """
        Envoie un lot de materiel d'un coup.                
        Si l'entrepot est plein, on ne decharge pas jusqu'a la prochaine 
        livraison.
        Si la prochaine livraison arrive, la marchandise est perdue 
        (laissee par terre).
        """
        ok = False
        for a in self.outa:
            if not a.fullQqt(self.tailleLot) and not ok: 
                a.add(self.tailleLot) 
                self.nbTraite += self.tailleLot
                ok = True
                        
        return ok
    
    def evacuation(self):
        """
        Évacue le materiel si possible et desactive le noeud.
        """        
        if self.h.isActif and self.putMatOneLot() :
            self.h.isActif = False
        
    # Pas de traitement
    def opere(self):
        """
        Mise à jour du noeud.
        """
        self.evacuation()
                
class NoeudUsineCadre(Noeud):
    """
    
    """
            
    def putMatNew(self):
        """
        Envoie un nouveau materiel.
        Pas besoin d'entré.
        """
        ok = False
        for a in self.outa:
            if not a.full() and not ok:                
                a.add() # on assai d'ajouter
                self.nbTraite += 1
                ok = True
                                
        return ok
            
    def evacuation(self):
        """
        Évacue le materiel si possible .
        """                 
        # Si le traitement est termine que qu'on arrive a evacuer le materiel, on procede.
        if self.TRAITEMENT_TERMINE and self.putMatNew(): 
            self.TRAITEMENT_TERMINE = False
            
    def traitement(self):
        """ Traitement du materiel par le noeud. """
        # Si le noeud marche et n'as pas termine de traitement, on procede.
        if self.getEtat() == "MARCHE" and not self.TRAITEMENT_TERMINE:
            if self.EN_TRAITEMENT: # on continu un traitement deja amorce
                ok = True
                if self.bingo: # on a un bingo disponible
                    ok = self.bingo.run() # c'est le bingo qui determine la fin du traitement
                    if ok: # on a donc termine un traitement
                        self.EN_TRAITEMENT = False
                        self.TRAITEMENT_TERMINE = True
            else: # on est pas en traitement, on essai d'en demarrer un.                         
                self.EN_TRAITEMENT = True
                self.JUST_STARTED = True                 
        
# Fin de la classe NoeudUsineCadre    
        
# Fin de la classe NoeudReceptionCamion
class NoeudEnvoiCamion(Noeud):
    """
    Noeud qui fait une action quand la quantité sur les arêtes entrantes atteignent un certains niveau.
    """
    
    def __init__(self, id= -1, nom="no name", restart_meme_cycle=True, tailleLot=1):
        """
        
        """
        Noeud.__init__(self, id, nom, restart_meme_cycle)                
        self.tailleLot = tailleLot
    
    def getMatLot(self, clear=False):
        """
        Test s'il y a au moins 'qqt' materiel et recupère si clear à True.
        Met à jour 'nbTraite'.
        """
        ok = False
        if len(self.ina) > 0:
            ok = True
            for a in self.ina:
                if not a.nbTransit() > self.tailleLot:
                    ok = False
            if ok and clear:
                for a in self.ina:
                    a.rm(self.tailleLot)
                    self.nbTraite += self.tailleLot
        return ok
    
    def evacuation(self):
        """
        Évacue le materiel si possible .
        """                 
        # Si le traitement est termine que qu'on arrive a evacuer le materiel, on procede.
        if self.TRAITEMENT_TERMINE and self.getMatLot(True): 
            self.TRAITEMENT_TERMINE = False
    
    def traitement(self):
        """
        Ne fait que récupérer du materiel, en fonction de 'Lots'.                
        """
        if self.getEtat() == "MARCHE" and not self.TRAITEMENT_TERMINE:
            if self.EN_TRAITEMENT: # on continu un traitement deja amorce
                ok = True
                if self.bingo: # on a un bingo disponible
                    ok = self.bingo.run() # c'est le bingo qui determine la fin du traitement
                    if ok: # on a donc termine un traitement
                        self.EN_TRAITEMENT = False
                        self.TRAITEMENT_TERMINE = True
            else: # on est pas en traitement, on essai d'en demarrer un.    
                if self.getMatLot():                    
                    self.EN_TRAITEMENT = True
                    self.JUST_STARTED = True

# Fin de la classe NoeudEnvoiCamion
    
