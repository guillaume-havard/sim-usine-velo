""" Modele pour simulation de l'usine d'assemblage de vélo. """

from flux import *
from fluxusinevelos import *
from data import *

class Modele(object):
    """ Modele pour simulation de l'usine de vélo
        Unites : materiel en T et temps en h. """
    
    def __init__(self, days):
        self.iteration = 0
        self.days = days # nb de jours a simuler
        
        
        self.mom = Moment()
                
        self.mom.dt = 1   # pas de temps = 1 sec
        self.maxiter = 3600 * 24 * days / self.mom.dt   # nb iterations a faire
        
        ### 0 - definition des horaires 
        self.lesHoraires = []        
        
        # Horraire usine
        h = Journee(self.mom, 1, "hUsine")
        h.initTag((8, 11, 13, 16), False)
        self.lesHoraires.append(h)
        hUsine = h
        # Horraire Assemblage
        h = Journee(self.mom, 1, "hAssemblage")
        #h.initTag((7, 16), False)
        h.initTag((), True)
        self.lesHoraires.append(h)
        hAssemblage = h
        # Arrivé kits
        h = Journee(self.mom, 1, "hArriveCamion")
        h.initTag((7, 11), False)
        self.lesHoraires.append(h)
        hArriveCamion = h
        
        ### 1 - definition des noeuds 
        delta = (100, 60)  # taille des noeuds 
        self.lesNoeuds = []
        
        # Arrivé de kits
        n = NoeudReceptionCamion(1, "Arrivée des kits", True, 360)
        n.geom.posPix = (90, 300);  n.geom.setDeltaPix(delta) # Pas de bingo.
        n.h = hArriveCamion
        self.lesNoeuds.append(n)
        nArr = n
        # Usine des cadres
        n = NoeudUsineCadre(2, "Usine de cadres")
        n.geom.posPix = (90, 100);  n.geom.setDeltaPix(delta)
        n.setPeriode(Da.periode_usine_cadre)
        n.h = hUsine
        self.lesNoeuds.append(n)
        nUsi = n
        # Assemblage
        n = Noeud(3, "Assemblage")
        n.geom.posPix = (350, 200);  n.geom.setDeltaPix(delta)
        n.setPeriode(Da.periode_assemblage) # À determiner.
        n.h = hAssemblage
        self.lesNoeuds.append(n)
        nAss = n
        self.nAss = nAss
        # Expedition
        n = NoeudEnvoiCamion(4, "expedition", True, 420)
        n.geom.posPix = (700, 200);  n.geom.setDeltaPix(delta)
        n.setPeriode(3600) # Temps mis pour représenter le temps de chargement des vélos.
        #n.h = hUsine
        self.lesNoeuds.append(n)
        nExp = n 
        
        ### 2 - definition des aretes et affectation aux noeuds 
        self.lesAretes = []
        
        # Chaine
        a = AreteTr(nUsi, nAss, 0, Da.taille_chaine, 600) 
        self.lesAretes.append(a)        
        nAss.ina.append(a)
        nUsi.outa.append(a)
        a.nom= "Chaine"
        # Entrepôt des kits
        a = Arete(nArr, nAss, 0, Da.t_entrepot_kits)
        self.lesAretes.append(a)        
        nAss.ina.append(a)
        nArr.outa.append(a)
        a.nom= "Entrepôt des kits"
        # Entrepôt des vélos
        a = Arete(nAss, nExp, 0, Da.arete_Inf)
        self.lesAretes.append(a)        
        nExp.ina.append(a)
        nAss.outa.append(a)
        a.nom= "Entrepôt des vélos"   
        
        ##### Autres setup 
        
        self.firstRendering = True  
        
        self.data = Datastore("Fabrique-velos", " a determiner")
        self.h_data = 0
        
    def update(self):
        """ Mise a jour du modele. """
        self.iteration += 1
        self.mom.update()
        if self.mom.MINtick:
            for h in self.lesHoraires: h.update()
            
        if self.mom.TICKtick:
            pass
            
        for n in self.lesNoeuds: 
            n.opere()
            
        for a in self.lesAretes:
            a.update()
            
        ok = self.iteration < self.maxiter
        if not ok:  # fin de la simulation
            self.data.dump()            

        return ok

    def renderNow(self, g):
        """ Rendering du modele. """
        sfont = ('times', 9, 'normal')
        nfont = ('times', 12, 'normal')
        bfont = ('times', 14, 'bold')
        x = 200
        y = 20
        g.create_text(x, y, text="Simulation (" + str(self.iteration) + \
                                 ")  " + self.mom.strNow(), font=bfont)
        
        ############ ajustement graphique du premier rendering
        if (self.firstRendering): 
            self.firstRendering = False
            for n in self.lesNoeuds:
                n.geom.bBox() # update de la box
                
        x = 110; y = 180; dy = 20
        
        for a in self.lesAretes: 
            g.create_line(a.fr.geom.cent, a.to.geom.cent, fill='gray')
            g.create_text(a.postxt, text=a.strEtat())
                            
        for n in self.lesNoeuds: 
            cc = n.getCol()
            g.create_rectangle(n.geom.bbox, width=1, fill=cc)
            g.create_text(n.geom.cl11, text=n.idnom, font=nfont)
            
            s = str(n.nbTraite)
            
            g.create_text(n.geom.cl22, text=s, font=nfont)
      
# fin de la classe Modele

