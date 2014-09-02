""" Fichier unique pour les tilitaires de modelisation et de simulation
    de flux. """

import math, decimal
from sbsim import *
from data import *

class Noeud(object):
    """ Traite du materiel des aretes et delivre sur une arete selon une 
        periode. 
            La periode de traitement est l'inverse du temps de cycle et dans
            l'unite de temps. 
            L'etat et la couleur du noeud sont obtenus dynamiquement via
            getEtat() et getCol().
            Par defaut: 
                * restart_meme_cycle est vrai et on essai de redemarrer un 
                  traitement dans le meme cycle qu'on evacue, sinon, on 
                  attends le prochain cycle.
                * il faut une unite de materiel sur chaque arete amont pour 
                  produire une unite sur la premiere arete aval disponible.
    """

    def __init__(self, id=-1, nom="no name", restart_meme_cycle=True):
        
        self.id = id     # id unique
        self.adr = id    # adresse logique (pas necessairement unique)
        self.nom = nom # pour l'affichage
        self.idnom = str(id) + " " + nom     # str formee de id et nom
        self.restart_meme_cycle = restart_meme_cycle    # restart ds le meme cycle de l'evacuation
        # dictionnaire des etats et leurs couleurs
        self.c = {"ARRET":'yellow', "MARCHE":'green', "BRIS":'red' }
        self.periode = 0    # doit etre fixe par setPeriode(p)
        self.bingo = None # doit etre cree via setPeriode(p)
        self.nbTraite = 0 # items traites par ce noeud        
        self.geom = GeomNoeud()
        self.ina = []     # aretes du voisinage amont        (voir classe Arete)
        self.outa = []    # aretes du voisinage aval         (voir classe Arete)
        self.h = None     # horaire d'operation du noeud (voir classe Horaire)
        # les variables d'etat d'operation
        self.ALTout = 0 # pour l'alternance des sorties
        self.ALTin = 0 # pour l'alternance des entrees
        self.TRAITEMENT_TERMINE = False
        self.EN_TRAITEMENT = False
        self.JUST_STARTED = True

    def setIdNom(self, id, nom):
        self.id = id
        self.nom = nom
        self.idnom = str(id) + "_" + nom

    def getEtat(self):
        """ Donne l'etat selon l'horaire. """
        self.etat = "MARCHE"    # etat par defaut si pas d'horaire
        if self.h:
            if not self.h.isActif:
                self.etat = "ARRET"
                if self.h.isBris:
                    self.etat = "BRIS"
        return self.etat
    
    def getCol(self):
        """ Donne la couleur de l'etat selon l'horaire. """
        return self.c[self.getEtat()]

    def setPeriode(self, p):
        """ Set la periode du bingo. """
        self.periode = p
        if p <= 0:
            self.bingo = None
        else:
            self.bingo = Bingo(p)

    def getMatAll(self, clear=False):
        """ Determine la disponibilite du materiel pour operer.
                Cas: on exige du materiel de chacune des aretes entrantes. 
                Mode clear=False: valide la presence du materiel.
                Mode clear=True: valide et retire le materiel. """
        ok = False
        if len(self.ina) > 0:
            ok = True
            for a in self.ina:
                if not a.nbTransit() > 0:
                    ok = False
            if ok and clear:
                for a in self.ina:
                    a.rm()
        return ok

    def getMatAlt(self, clear=False):
        """ Determine la disponibilite du materiel pour operer.
                Cas: on exige du materiel d'une seule arete entrante 
                et on alterne. 
                Mode clear=False: valide la presence du materiel.
                Mode clear=True: valide et retire le materiel. """
        ok = False
        if len(self.ina) > 0:
            ok = False
            for i in range(len(self.ina)):
                ix = (self.ALTin + i) % len(self.ina); a = self.ina[ix]
                if a.nbTransit() > 0:
                    ok = True
                    break
            if ok and clear:
                a = self.ina[ix]
                self.ALTin = (ix + 1) % len(self.ina)
                a.rm()
        return ok

    def putMatAlt(self, clear=True):
        """ Realise l'evacuation du materiel vers la premiere arete disponible, 
                partant de la suivante dans la liste outa pour alterner les 
                sorties.
                Cas: on evacue sur la premiere arete avec de la place.
                Mode clear=False: on ne retire pas de materiel.
                Mode clear=True: valide et retire le materiel. """
        ok = False
        for i in range(len(self.outa)):
            ix = (self.ALTout + i) % len(self.outa); a = self.outa[ix]
            if not a.full() and not ok:
                ctn = True
                if clear:     # on doit s'assure qu'il y a du materiel en amont et le retirer
                    ctn = self.getMatAll(clear)
                if ctn:
                    self.ALTout = (ix + 1) % len(self.outa)
                    a.add() # on assai d'ajouter
                    self.nbTraite += 1
                    ok = True
        return ok

    def putMatOne(self, clear=True):
        """ Realise l'evacuation du materiel vers la premiere arete disponible, 
                partant toujours de la premiere de la liste outa.
                Cas: on evacue sur la premiere arete avec de la place.
                Mode clear=False: on ne retire pas de materiel.
                Mode clear=True: valide et retire le materiel. """
        ok = False
        for a in self.outa:
            if not a.full() and not ok:
                ctn = True
                if clear:     # on doit s'assure qu'il y a du materiel en amont et le retirer
                    ctn = self.getMatAll(clear)
                if ctn:
                    a.add() # on assai d'ajouter
                    self.nbTraite += 1
                    ok = True
        return ok

    def putMatOneFromAlt(self, clear=True):
        """ Realise l'evacuation du materiel vers la premiere arete disponible, 
                partant toujours de la premiere de la liste outa.
                Cas: on evacue sur la premiere arete avec de la place.
                Mode clear=False: on ne retire pas de materiel.
                Mode clear=True: valide et retire le materiel. """
        ok = False
        for a in self.outa:
            if not a.full() and not ok:
                ctn = True
                if clear:     # on doit s'assure qu'il y a du materiel en amont et le retirer
                    ctn = self.getMatAlt(clear)
                if ctn:
                    a.add() # on assai d'ajouter
                    self.nbTraite += 1
                    ok = True
        return ok

    def evacuation(self):
        """ Evacuation du materiel si possible. """
        # Si le traitement est termine que qu'on arrive a evacuer le materiel, on procede.
        if self.TRAITEMENT_TERMINE and self.putMatOne(): 
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
            else: # on est pas en traitement, on essai d'en demarrer un
                if self.getMatAll(): # si on a du materiel en entree, on commence un traitement
                    self.EN_TRAITEMENT = True
                    self.JUST_STARTED = True

    def opere(self):
        """ Mise a jour du noeud a toute les unites de temps. """
        self.evacuation()
        self.traitement()
        self.evacuation()
        if self.restart_meme_cycle and self.JUST_STARTED:     # on essai de restarter ds le meme cycle
            self.traitement()
            self.JUST_STARTED = False

    def show(self):
        """ Methode de test de la classe. """
        print("Noeud", self.nom, self.id, self.nbTraite, self.EN_TRAITEMENT, self.TRAITEMENT_TERMINE, self.getCol())
# fin de la classe Noeud

class Arete(object):
    """ Arete simple entre 2 noeuds.
            Elle possede un poids actuel (w) et un poids max (wmax).
            Typiquement elle modelise un reservoir de capacite wmax.
            Si wmax est 999999, on considere dans contrainte. 
            Attention! Toujours utiliser nbItem() pour connaitre le poids w (et non w).
    """
    def __init__(self, noeudFr, noeudTo, w, wmax):
        self.nom = str(noeudFr.id) + "x" + str(noeudTo.id)    # nom est forme des id des noeuds
        self.id = 100 * noeudFr.id + noeudTo.id                         # id est forme des id des noeuds
        self.fr = noeudFr; self.to = noeudTo    # noeuds aux extremites de l'arete
        self.w = w; self.wmax = wmax    # poids de l'arete et son max
        self.wInf = 999999     # quantite considere infinie (pour l'affichage)
        self.postxt = VR2.pointInt(0.5, noeudFr.geom.cent, noeudTo.geom.cent)
        if w > wmax: print("Erreur! Arete avec w>wmax.")
    
    def empty(self):
        """ Vrai si le poids w est 0. """
        return (self.w == 0)
        
    def full(self):
        """ Vrai si full. """
        if self.w >= self.wmax: return True
        else: return False
        
    def fullQqt(self, qqt = 1):
        """ Vrai si full. """
        if self.w + qqt >= self.wmax: return True
        else: return False
    
    def nbItem(self):
        """ Retourne le poids. """
        return self.w

    def nbTransit(self):
        """ Dans le cas de base d'une arete reservoir (pool), c'est le poids. """
        return self.w

    def hasItem(self, x):
        """ Vrai si au moins x item sur l'arete. """
        if self.w >= x: 
            return True
        else: 
            return False

    def hasPlace(self, x):
        """ Vrai si au moins x places. """
        if (self.wmax - self.w) >= x : 
            return True
        else: 
            return False

    def add(self, x=1):
        """ Ajoute x items avec validation. """
        if self.hasPlace(x):
            self.w += x
            return True
        else:
            return False

    def rm(self, x=1):
        """ Remove x items avec validation. """
        if self.nbTransit() >= x:
            self.w -= x
            return True
        else:
            return False

    def update(self):
        """ Mise a jour des infos sur l'arete a toute les unite de temps. """
        None
                
    def strEtat(self):
        """ Methode de test de la classe. """
        s = self.nom + " " + str(self.nbItem())
        if self.wmax != self.wInf: 
            s += "/" + str(self.wmax)
        return s

    def show(self):
        """ Methode de test de la classe. """
        print("Arete", self.nom, self.fr.id, "a", self.to.id)
# fin de la classe Arete

class AreteTr(Arete):
    """ Arete avec transit entre 2 noeuds.
            Elle possede un poids actuel (w), un poids max (wmax) et un temps de transit.
            Typiquement elle modelise un convoyeur ou une chaine de capacite wmax.
            Attention! Toujours utiliser nbItem() pour connaitre le poids w (et non w).
    """
    def __init__(self, noeudFr, noeudTo, w, wmax, transit):
        Arete.__init__(self, noeudFr, noeudTo, w, wmax)
        self.transit = transit
        self.fifo = []
        # on cree les items deja present avec le transit termine
        for i in range(w):
            self.fifo.append(transit)

    def empty(self):
        """ Vrai si le poids w est 0. """
        return (len(self.fifo) == 0)
        
    def full(self):
        """ Vrai si full. """
        if len(self.fifo) >= self.wmax: 
            return True
        else: 
            return False
    
    def nbItem(self):
        """ Retourne le poids. """
        self.w = len(self.fifo)
        return self.w

    def nbTransit(self):
        """ Dans le cas d'une arete avec transit (fifo), c'est le nb d'item ayant fini le transit. """
        n = 0
        for item in self.fifo:
            if item >= self.transit: n += 1
        return n

    def hasItem(self, x):
        """ Vrai si au moins x item sur l'arete. """
        self.w = len(self.fifo)
        if self.w >= x: 
            return True
        else: 
            return False

    def hasPlace(self, x):
        """ Vrai si au moins x places. """
        self.w = len(self.fifo)
        if (self.wmax - self.w) >= x: 
            return True
        else: 
            return False

    def add(self, x=1):
        """ Ajoute x items avec validation. """
        if self.hasPlace(x):
            for i in range(x):
                self.fifo.append(0)
            return True
        else:
            return False

    def rm(self, x=1):
        """ Remove x items avec validation. """
        if self.nbTransit() >= x:
            for i in range(x):
                self.fifo.pop(0)
            return True
        else:
            return False

    def update(self):
        """ Mise a jour des infos sur l'arete a toute les unite de temps. """
        for i in range(len(self.fifo)):
            self.fifo[i] += 1

    def show(self):
        """ Methode de test de la classe. """
        print("AreteTr", self.nom, self.fr.id, "a", self.to.id)
# fin de la classe AreteTr

    
bingo_pInf = 20000000.0        # constante pour init de la periode
    
class Bingo(object):
    """ Generateur d'un evenement selon une periode fixe.    
    La periode est un nombre reel par rapport a une unite de temps. 
    Le temps incremente de une unite a chaque appel de Bingo.run. 
    On suppose que la periode est bien plus grande que l'unite de temps 
    (au moins 3x l'unite de temps). On cumule les fractions de periodes 
    en unite avec une precision au millieme. On supporte le changement de 
    periode, sans reset du reste et du cumul.
    """
    def __init__(self, periode=bingo_pInf):
        self.M = 1000 # precision du reste
        self.setPeriode(periode)
        self.cumulReste = 0
        self.cumulUnite = 0
    
    def setPeriode(self, periode):
        """ Reset le bingo avec une nouvelle periode. """
        self.periode = decimal.Decimal(str(periode))
        p = int(self.periode * self.M)
        self.periodeInt = (p / self.M)
        pr = p % self.M
        if pr > 0:
            self.periodeReste = self.M - pr
            self.periodeInt += 1
        else:
            self.periodeReste = 0

    def run(self):
        """ Avance d'une unite de temps et genere un evenement selon le periode. """
        self.cumulUnite += 1
        trigger = False
        if (self.cumulUnite >= self.periodeInt):
            trigger = True
            self.cumulUnite -= self.periodeInt
            self.cumulReste += self.periodeReste
        elif (self.cumulReste >= self.M):
            self.cumulUnite += 1
            self.cumulReste -= self.M
        return trigger
        
    def strEtat(self):
        """ Methode de test de la classe. """
        return str(self.cumulUnite) + "r" + str(self.cumulReste)

    def show(self):
        """ Methode de test de la classe. """
        print("Periodes:", self.periode, self.periodeInt, self.periodeReste, self.strEtat())
# fin de la classe Bingo

    
class GeomNoeud(object):
    """ Caracteristiques geometriques des noeuds avec dx,dy des nb pairs de pixels. 
    La position du noeud est posPix, mais peut etre fixe via une adresse posAdr, 
    relative a une position de reference origineAdr et un deplacement deltaAdr.
    La taille du noeud est deltaPix. """
    def __init__(self, pos=(20, 20)):
        self.posPix = pos     # position du noeud en pixel
        self.setDeltaPix((16, 48))     # taille de la boite en pixel
        self.origineAdr = (0, 60)    # pixel de reference de l'adresse (0,0)
        self.posAdrX = 0 # adresse par defaut en X
        self.posAdrY = 0 # adresse par defaut en Y
        self.deltaAdr = self.deltaPix     # variation entre les unites d'adresse
        self.bBox()
            
    def setDeltaPix(self, delta):
        """ Definie le delta et demi-delta de la boite. """
        self.deltaPix = delta    # taille de la boite dx,dy
        self.demideltaPix = (delta[0] / 2, delta[1] / 2) # demi du delta        
        self.bBox()
             
    def bBox(self):
        """ Caracteristique de la boite graphique du noeud et son centre. """
        self.bbox = (self.posPix + VR2.add(self.posPix, self.deltaPix)) # boite du noeud (+ = concatenate)
        self.cNW = (self.bbox[0], self.bbox[1]); self.cSE = (self.bbox[2], self.bbox[3])
        self.cNE = (self.bbox[2], self.bbox[1]); self.cSW = (self.bbox[0], self.bbox[3])
        self.cent = VR2.add(self.posPix, self.demideltaPix) # centre de la boite
        self.above = (self.cent[0], self.bbox[1] - 7)
        self.below = (self.cent[0], self.bbox[3] + 7)
        self.cl1 = VR2.add((0, -7), self.cent) # centre de la premiere ligne de texte
        self.cl2 = VR2.add((0, 5), self.cent) # centre de la seconde ligne de texte
        self.cl11 = VR2.add((0, -15), self.cent) # centre alt de la premiere ligne de texte
        self.cl22 = VR2.add((0, 14), self.cent) # centre alt de la seconde ligne de texte
            
    def setAdr(self, adrX, adrY): 
        """ Positionne le noeud selon une adresse x,y vers est et sud, mais ne recalcule 
        pas ses caracteristiques internes. Il faut donc appeler bBox avec l'affichage. """
        self.posAdrX = adrX
        self.posAdrY = adrY
        self.posPix = VR2.add(self.origineAdr, VR2.mult((adrX, adrY), self.deltaAdr))
        
    def setAdrX(self, adrX): 
        """ Positionne le noeud selon une adresse x vers est, mais ne recalcule 
        pas ses caracteristiques internes. Il faut donc appeler bBox avec l'affichage. """
        self.posAdrX = adrX
        self.posPix = VR2.add(self.origineAdr, VR2.mult((adrX, self.posAdrY), self.deltaAdr))
            
    def moveX(self, n): 
        """ Move de n adresses: positif vers la droite (est), negatif vers la gauche (ouest). """
        self.setAdr(self.posAdrX + n, self.posAdrY)

    def show(self):
        """ Methode de test de la classe. """
        print("Position:", self.posPix)                 
# fin de la classe GeomNoeud
    
