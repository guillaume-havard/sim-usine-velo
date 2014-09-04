""" Utilitaires pour la modelisation et la simulation. 
      References:
        * http://python.org/
        * http://docs.python.org/tutorial/
        * http://docs.python.org/reference/
        * http://docs.python.org/library/
        * http://www.pythonware.com/library/tkinter/introduction/
"""

import math
import decimal
import gen

class Moment(object):
    """ Definit et gere l'etat des variables temporelles 
    dans une simulation avec des jours, semaines, quarts, etc. 
    Offre des triggers de temps cumule de simulation: minute, heure, quart, 24h. 
    Attention: c'est du cumul depuis le debut, pas les heures de l'horloge, 
    sauf Jtick qui trigger a 0h (minuit) exactement pour le changement de jour.
    """
    # list et dictionnaire des jours
    jFR=["Dimanche","Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"]
    jEN=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    j = jFR
    djFR={"Dimanche":0,"Lundi":1,"Mardi":2,"Mercredi":3,"Jeudi":4,"Vendredi":5,"Samedi":6 }
    djEN={"Sunday":0,"Monday":1,"Tuesday":2,"Wednesday":3,"Thursday":4,"Friday":5,"Saturday":6 }
    dj = djFR
    # list et dictionnaire des quarts
    qFR=["Jour","Soir","Nuit"]
    qEN=["Day","Evening","Night"]
    q = qFR
    dqFR={"Jour":0,"Soir":1,"Nuit":2}
    dqEN={"Day":0,"Evening":1,"Night":2}
    dq = dqFR
    # constantes utiles
    Jmin=1440   # nb de minutes dans une journee
    Smin=10080  # nb de minutes dans une semaine
    
    def __init__(self):
        # Parametres important a definir pour chaque modele (ne pas changer apres ca)
        self.Jdepart="Lundi"
        self.Qnb=3    # nb de Q par jour (doit etre coherent avec Moment.q)
        self.Qmj=self.convertHM2M(6.0) # debut du quart de jour (h.m)
        self.dt=1     # pas de temps en secondes (doit etre un diviseur de 60)
        self.Qnow=0   # no du quart de depart (toujours 0)
        self.TICKsetup=180  # TICKtick trigger a toutes les TICKsetup minutes
        # fin section des parametres
        self.Qmin=Moment.Jmin/self.Qnb # nb de min par quart
        self.Jno=Moment.dj[self.Jdepart]
        self.MINnow=self.Qmj+self.Qnow*self.Qmin # min actuelle de depart
        self.SECtot=0 # cumul des secondes
        self.MINtot=0 # cumul des minutes
        self.Qtot=0   # cumul des quarts
        self.Jtot=0   # cumul des jours (i.e. periodes de 24h)
        self.Jtick=False; self.Qtick=False; self.MINtick=False; 
        self.Htick=False; self.Q24tick=False; self.TICKtick=False;
      
    def update(self):
        """ Avance de dt dans le temps et update des variables associees. """
        self.Jtick=False; self.Qtick=False; self.MINtick=False; 
        self.Htick=False; self.Q24tick=False; self.TICKtick=False;
        self.SECtot+=self.dt
        if (self.SECtot%60 ==0): 
            # trigger: une minute de simulation est passe
            self.MINtot+=1; self.MINnow+=1; self.MINtick=True
            if (self.MINtot%self.TICKsetup ==0): 
                # trigger: TICKsetup de simulation sont passe
                self.TICKtick=True
            if (self.MINtot%60 ==0): 
                # trigger: une heure de simulation est passe
                self.Htick=True
            if (self.MINnow>=Moment.Jmin):
                # trigger: marque 0h (minuit) 
                self.MINnow=0; self.Jtick=True
                self.Jno+=1
                if (self.Jno>6): self.Jno=0
            if ((self.MINnow-self.Qmj)%self.Qmin ==0): 
                # trigger: un quart de simulation est passe
                self.Qnow+=1; self.Qtick=True
                if (self.Qnow>=self.Qnb): self.Qnow=0
                self.Qtot+=1
            if (self.MINtot%Moment.Jmin ==0):
                # trigger: une periode de 24h de simulation est passe
                self.Jtot+=1
                self.Q24tick=True

    def convertHM2M(self,x):
        """ Conversion h.m en minutes: h*60+m, exemple 5.15 (ie 5h15) donne 315. """
        xd=decimal.Decimal(str(x))
        xh=int(xd)
        xm=int((xd-xh)*100)
        return xh*60+xm
          
    def strHMSnow(self):
        return str( self.MINnow/60 )+"h"+str( self.MINnow%60 )+"m"+str( self.SECtot%60 )+"s"
          
    def strHMnow(self):
        return str( int(self.MINnow/60) )+"h"+str( int(self.MINnow%60) )
      
    def strNow(self):
        return Moment.j[self.Jno]+"("+str(self.Jtot)+") "+self.strHMnow()
# fin de la classe Moment
  
  
class Horaire(object):
    """ Interface commune aux horaires. """
    def __init__(self,mom=None,id=-1,nom="no name"):
        self.nom=nom   # nom de l'horaire
        self.id=id     # id unique
        self.mom=mom   # une instance de Moment pout tracking du temps
        self.isActif=False         # etat courant d'activite
        self.isBris=False          # si inactif a cause d'un bris
        self.isActifAuDebut=False  # etat de reference au debut du jour (i.e. a Moment.Qmj)
        self.lastUpdated=-100      # ctrl pour eviter d'updater 2 fois dans la meme minute
# fin de la classe Horaire
  
  
class Journee(Horaire):
    """ Une journee. """
      
    def initTag(self,tag,isActifAuDebut):
        """ Initialisation du tuple avec les tag donnant les minutes de changement d'etat. 
        Chaque element du tuple est en h.min (avec min entre 0 et 59!!!). Notons que le 
        jour commence toujours avec un reset a isActifAuDebut a Moment.Qmj """
        self.tag=tag
        self.isActif=isActifAuDebut
        self.isActifAuDebut=isActifAuDebut
        self.nextIdx=0
        if (not len(self.tag)): 
          self.nextChg=-1
        else: 
          self.nextChg=self.mom.convertHM2M(self.tag[self.nextIdx])
          # test si AuDebut de l'horaire == mom.Qmj
          if (self.mom.MINnow==self.nextChg):
            self.nextIdx+=1
            if (self.nextIdx>=len(self.tag)): self.nextIdx=0
            self.nextChg=self.mom.convertHM2M(self.tag[self.nextIdx])
        self.lastUpdated=-100
  
    def update(self):
        """ Update de l'horaire a chaque minute. """
        #print self.lastUpdated,self.mom.MINtot,self.mom.Qmj,self.mom.MINnow,self.nextChg
        if (self.lastUpdated!=self.mom.MINtot):
            self.lastUpdated=self.mom.MINtot
            if (self.mom.MINnow==self.nextChg):
                self.isActif=not self.isActif
                self.nextIdx+=1
                if (self.nextIdx>=len(self.tag)): self.nextIdx=0
                self.nextChg=self.mom.convertHM2M(self.tag[self.nextIdx])
            if (self.mom.MINnow==self.mom.Qmj):
                self.isActif=self.isActifAuDebut
        #print "Horaire",self.nom,self.id,self.isActif
# fin de la classe Journee

class JourneePanne(Journee):
    """ Classe Journee avec gestion des pannes ajoutee pour l'usine de 
        cadre """
            
    gen01 = gen.GenU01MRG() # generateur de nombre aleatoire pour l'usine
    
    def setPannes(self, seuil, durees):
        """ Set la variable de declenchement de pannes et les durees des 
            pannes.
            Obligatoire pour l'update"""
        self.seuilBris = seuil # Valeur pour le declenchement d'une pann
        self.dureeBris = durees # duree des pannes.
    
    def update(self):
        Journee.update(self)
        
        # L'update est appele une fois par minute
        # Test si pas de bris.
        if self.isActif and not self.isBris:
            if self.gen01.suiv() <= self.seuilBris:
                print("BRIS BRIS")
                self.isBris = True
                self.dureeBrisSelect = self.dureeBris[int(self.gen01.suiv() * 
                                                      (len(self.dureeBris)-1))]
                print("reparation {}".format(self.dureeBrisSelect))
                return
                
        # Si bris, reparation (meme si usine fermee)
        if self.isBris:
            self.dureeBrisSelect -= 1            
            if self.dureeBrisSelect <= 0:
               self.isBris = False
               print("FIN")
            return        
# fin de la classe JourneePanne

class Semaine(Horaire):
    """ Une semaine comme assemblage de 7 instances de Journee. """
    def __init__(self,mom=None,id=-1,nom="no name"):
        Horaire.__init__(self,mom,id,nom)  

    def initSem(self,jour):
        """ Initialisation du tuple avec le meme jour 7x. """
        self.lesJours = [jour,jour,jour,jour,jour,jour,jour]
        self.isActif = jour.isActifAuDebut
        self.lastUpdated=-100
        self.jac=None

    def update(self):
        """ Update de l'horaire a chaque minute. """
        #print self.lastUpdated,self.mom.MINtot,self.mom.Qmj,self.mom.MINnow,self.nextChg
        if (self.lastUpdated!=self.mom.MINtot):
            self.lastUpdated=self.mom.MINtot
            if (not self.jac or ((self.mom.MINtot%Moment.Jmin)==0)):
                self.jac=self.lesJours[self.mom.Jno]
                self.jac.isActif=self.jac.isActifAuDebut
            self.jac.update()
            self.isActif=self.jac.isActif
# fin de la classe Semaine
  
  
class Iint(object):
    """ Calcul en arithmetique entiere sur un interval I. """
    def __init__(self,a,b):
        self.a=a
        self.b=b
        self.n=b-a+1
  
    def test(self):
        """ Methode de test de la classe. """
        print("Iint de ",self.a," a ",self.b)
    
    def pZn(self,x):
        """ Projection sur Zn. """
        z=(x-self.a)%self.n
        if (z<0): return z+self.n
        else: return z
  
    def qI(self,x):
        """ Projection inverse sur I. """
        return x+self.a
      
    def add(self,x,y):
        """ Addition de 2 entiers dans I. """
        return self.qI(self.pZn(x+y))
      
    def suiv(self,x):
        """ Suivant de x dans I. """
        return self.add(x,1)
      
    def prev(self,x):
        """ Precedent de x dans I. """
        return self.add(x,-1)
      
    def dist(self,x,y):
        """ Distance entre x et y dans I, direct ou via extremites. """
        xx=self.pZn(x)
        yy=self.pZn(y)
        if (yy<xx): xx,yy=yy,xx
        d=yy-xx  # ecart direct
        dd=xx+(self.n-yy)  # ecart par les extremites
        if (dd<d): return dd 
        else: return d
# fin de la classe Iint
  
  
class Inter2d(object):
    """ Interpolation (bi-)lineaire 2d sur grille reguliere. """
    def __init__(self,x0,hx,nx,y0,hy,ny,A):
        """ Parametres:
          * x0,y0: coordonnees du coin inferieur gauche
          * hx,hy: pas de la grille en x et en y (peut-etre negatif)
          * nx,ny: nb d'intervalles en x et en y (i.e. nb points -1)
          * A: matrice nx+1 par ny+1 des valeurs aux points de la grille.
          Coor en xi: x0+i*hx, avec i=0 a nx.
          Coor en yj: y0+j*hy, avec j=0 a ny.
          Si f() est la fct dont la grille est dans A, on a:
            f(xi,yj)=A(ny-j,i)
        """
        self.x0=x0; self.y0=y0; 
        self.hx=hx; self.hy=hy; 
        self.nx=nx; self.ny=ny; 
        self.A=A;
      
    def f(self,i,j):
        """ Valeur de la fonction en xi,yj. """
        a=self.ny-j; b=i
        # projection des indices pour l'interpolation au bord
        if (a<0): a=0 
        if (a>self.ny): a=self.ny
        if (b<0): b=0
        if (b>self.nx): b=self.nx
        return self.A[a][b]
   
    def projection_x(self,x):
        """ Projection en x sur le domaine. """
        xmin=self.x0
        xmax=self.x0+self.nx*self.hx
        if (xmin>xmax): xmin,xmax=xmax,xmin
        if (x<xmin): x=xmin
        elif (x>xmax): x=xmax
        return x
  
    def projection_y(self,y):
        """ Projection en y sur le domaine. """
        ymin=self.y0
        ymax=self.y0+self.ny*self.hy
        if (ymin>ymax): ymin,ymax=ymax,ymin
        if (y<ymin): y=ymin
        elif (y>ymax): y=ymax
        return y
      
    def carre(self,x,y):
        """ Determine dans quel rectangle est un point apres projection sur le domaine. """
        # on calcule les indices: (x,y) est ds le rectangle de coins 
        # (x0+ix*hx,y0+iy*hy) - (x0+(ix+1)*hx,y0+(iy+1)*hy)
        self.i=int(math.floor( (x-self.x0)/self.hx ))
        self.j=int(math.floor( (y-self.y0)/self.hy ))
  
    def bilin(self,x,y):
        """ Interpolation bilineaire. """
        # projection et calcul du rectangle de point
        xx=self.projection_x(x); yy=self.projection_y(y);
        self.carre(xx,yy)
        # coor du coin
        cx=self.x0+self.i*self.hx; cy=self.y0+self.j*self.hy; 
        # proportion en x et en y
        px=(xx-cx)/self.hx; py=(yy-cy)/self.hy;
        # interpolation 1D sur les 2 bords en x
        print("i,j: ",self.i," ",self.j)
        vx1=(1.-px)*self.f(self.i,self.j)+px*self.f(self.i+1,self.j)
        vx2=(1.-px)*self.f(self.i,self.j+1)+px*self.f(self.i+1,self.j+1)
        return (1.-py)*vx1+py*vx2
    
    def bary(self,x,y):
        """ Interpolation barycentrique via triangles. On numerote en sens anti-horaire:
          3---------2
           | T2  /  |
           |    / T1|
           0--------1
        """
        # projection et calcul du rectangle de point
        xx=self.projection_x(x); yy=self.projection_y(y);
        self.carre(xx,yy)
        # coor du coin
        cx=self.x0+self.i*self.hx; cy=self.y0+self.j*self.hy;
        # si on est proche du coin, on termine
        dx=cx-x; dy=cy-y
        if ( (dx*dx+dy*dy)<0.00001): return self.f(self.i,self.j)
        # autrement on continu
        # on recupere la valeur de x,y,f sur T1
        ff=[self.f(self.i,self.j),self.f(self.i+1,self.j),self.f(self.i+1,self.j+1)]
        xt=[cx,cx+self.hx,cx+self.hx]
        yt=[cy,cy,cy+self.hy]
        rT1=self.interpolationT(xt,yt,x,y,ff)
        # on recupere la valeur de x,y,f sur T2
        ff=[self.f(self.i,self.j),self.f(self.i+1,self.j+1),self.f(self.i,self.j+1)]
        xt=[cx,cx+self.hx,cx]
        yt=[cy,cy+self.hy,cy+self.hy]
        rT2=self.interpolationT(xt,yt,x,y,ff)
        # on choisit l'interpolation avec tous les aires positifs (en fait max)
        if (rT1[0]>rT2[0]): return rT1[1]
        else: return rT2[1]
        
    def interpolationT(self,xt,yt,x,y,ff):
        """ Interpolation lineaire (Lagrange) dans un triangle via coor barycentrique. """
        aire2Ti=1.0/self.pv(xt[0],yt[0],xt[1],yt[1],xt[2],yt[2])
        p0=self.pv(x,y,xt[1],yt[1],xt[2],yt[2])*aire2Ti
        pmin=p0
        p1=self.pv(xt[0],yt[0],x,y,xt[2],yt[2])*aire2Ti
        if (p1<pmin): pmin=p1
        p2=self.pv(xt[0],yt[0],xt[1],yt[1],x,y)*aire2Ti
        if (p2<pmin): pmin=p2
        val=p0*ff[0]+p1*ff[1]+p2*ff[2]
        return [pmin,val]
    
    def pv(self,ax,ay,bx,by,cx,cy):
        """ Produit vectoriel ab X ac = 2 x aire du triangle a-b-c. """
        return ax*(by-cy)+ay*(cx-bx)+bx*cy-by*cx
        
    def test(self,x,y):
        """ Methode de test de la classe. """
        print("Dernier point en ",self.x0+self.nx*self.hx," ",self.y0+self.ny*self.hy)
        print("Projection: ",self.projection_x(x)," ",self.projection_y(y))
        print("Interpolation 2D bilineaire et bary: ",self.bilin(x,y)," ",self.bary(x,y))
        print("Int 2D sur un T: ",self.interpolationT([0.,1.,1.],[0.,0.,1.],0.6666,0.3333,[0.,1.,1.]))
# fin de la classe Inter2d
  
  
class VR2(object):
    """ Operations sur les vecteurs de R2, i.e. sur les couples de RxR, sous forme de tuple (). 
          Note: le conversion entre list et tuple est  li=list(tu), et l'inverse tu=tuple(li).
    """
    @staticmethod
    def add(a,b):
        """ Somme a+b. """
        return (a[0]+b[0],a[1]+b[1])
  
    @staticmethod
    def diff(a,b):
        """ Difference a-b. """
        return (a[0]-b[0],a[1]-b[1])
      
    @staticmethod
    def pointInt(k,a,b):
        """ Point a distance k de a sur le segment a-b avec coordonnees entieres (pixel). """
        v=VR2.diff(b,a)
        return (int((a[0]+k*v[0])),int((a[1]+k*v[1])))
  
    @staticmethod
    def milieuInt(a,b):
        """ Milieu du segment a-b avec coordonnees entieres (pixel). """
        return (int((a[0]+b[0])/2),int((a[1]+b[1])/2))
  
    @staticmethod
    def mult(a,b):
        """ Mult a*b terme a terme. """
        return (a[0]*b[0],a[1]*b[1])
  
    @staticmethod
    def multscal(k,a):
        """ Mult a par un scalaire k. """
        return (k*a[0],k*a[1])
          
    @staticmethod
    def ps(a,b):
        """ Produit scalaire entre a et b. """
        return a[0]*b[0]+a[1]*b[1]
        
    @staticmethod
    def pv(a,b):
        """ Produit vectoriel entre a et b. """
        return a[0]*b[1]-a[1]*b[0]
      
    @staticmethod
    def pv(a,b,c):
        """ Produit vectoriel entre ab et ac. """
        return a[0]*(b[1]-c[1])+a[1]*(c[0]-b[0])+b[0]*c[1]-b[1]*c[0]
      
    @staticmethod
    def norme2(a):
        """ Norme euclidienne de a. """
        return math.sqrt(VR2.ps(a,a))
        
    @staticmethod
    def dist(a,b):
        """ Distance euclidienne entre a et b. """
        return VR2.norme2(VR2.diff(a,b))
      
    @staticmethod
    def test():
        """ Methode de test de la classe. """
        print("Somme ",VR2.add((1.,2.),(3.,4.)))
        print("Dist ",VR2.dist((1.,2.),(2.,3.)))
# fin de la classe VR2
  
  
class VRn:
    """ Operations sur les vecteurs de Rn sous forme de list []. 
    Note: le conversion entre list et tuple est  li=list(tu), et l'inverse tu=tuple(li). """
    @staticmethod
    def add(a,b):
        """ Somme a+b. """
        return [a[i]+b[i] for i in range(0,len(a))]
        #total = sum([num * num for num in range(1, 101)])
  
    @staticmethod
    def diff(a,b):
        """ Difference a-b. """
        return [a[i]-b[i] for i in range(0,len(a))]
  
    @staticmethod
    def ps(a,b):
        """ Produit scalaire entre a et b. """
        return sum([a[i]*b[i] for i in range(0,len(a))])
        
    @staticmethod
    def norme2(a):
        """ Norme euclidienne de a. """
        return math.sqrt(VRn.ps(a,a))
  
    @staticmethod
    def normeInf(a):
        """ Norme infinie de a. """
        v=a[0]
        if (v<0.): v=-v
        for i in range(1,len(a)):
            w=a[i]
            if (w<0.): w=-w
            if (w>v): v=w
        return v
              
    @staticmethod
    def dist(a,b):
        """ Distance euclidienne entre a et b. """
        return VRn.norme2(VRn.diff(a,b))
      
    @staticmethod
    def test():
        """ Methode de test de la classe. """
        print("Somme ",VRn.add([1.,2.,3.],[4.,5.,6.]))
        print("Pscal ",VRn.ps([1.,2.,3.],[4.,5.,6.]))
        print("Dist  ",VRn.dist([1.,2.,3.],[4.,5.,6.]))
        print("NormeInf ",VRn.normeInf([1.,2.,3.]),VRn.normeInf([4.,-5.,-6.]))
# fin de la classe VR2
  
  
FSMError = 'Invalid input to finite state machine'
class FSM(object):
    """Finite state machine, featuring transition actions.
    The class stores a dictionary of (state, input) keys,
    and (state, action) values.
    When a (state, input) search is performed:
      * an exact match is checked first,
      * (state, None) is checked next.
    The action is of the following form:
      * function(current_state, input)
    """

    def __init__(self):
        self.states = {}
        self.state = None
        self.dbg = None

    def add(self, state, input, newstate, action):
        """Add a transition to the FSM."""
        self.states[(state, input)] = (newstate, action)

    def execute(self, input):
        """Perform a transition and execute action."""
        #print "Execute",input,"from state",self.state
        si = (self.state, input)
        sn = (self.state, None)
        # exact state match?
        if si in self.states:
            newstate, action = self.states[si]
        # no, how about a None (catch-all) match?
        elif sn in self.states:
            newstate, action = self.states[sn]
        if self.dbg != None:
            self.dbg.write('State: %s / Input: %s /'
                           'Next State: %s / Action: %s\n' %
                           (self.state, input, newstate, action))
        action(self.state, input)
        self.state = newstate
        #print "Fin execute",input,"now in state",self.state

    def start(self, state):
        """Define the start state. Actually, this just resets the current state. """
        self.state = state

    def debug(self, out):
        """Assign a writable file to log transitions."""
        self.dbg = out
        
    def test(self):
        """Print dict to log file."""
        if self.dbg != None:
            self.dbg.write(str(self.states))
# end class FSM


class StatVA(object):
    """ Statistiques descriptives d'une variable aleatoire a valeur dans R. """
    def __init__(self,nom="no name"):
        self.nom=nom # de la v.a.
        self.last=None
        self.min=None
        self.max=None
        self.sum=0
        self.nb=0

    def add(self, x):
        """Add une valeur."""
        self.sum+=x
        self.last=x
        self.nb+=1
        if (self.nb==1):
            self.min=x; self.max=x
        else:
            if (x<self.min): self.min=x
            elif (x>self.max): self.max=x
        
    def moy(self):
        """ Moyenne. """
        if (self.nb):
            return self.sum/self.nb
        else: 
            return None

    def et(self):
        """ Etendue. """
        if (self.nb):
            return self.max-self.min
        else: 
            return None
            
    def strVA(self):
        """ Retourne une string avec les resultats. """
        s = self.nom+" ---"
        if (self.nb>0):
            s = self.nom+" n/moy/rng/minmax: "+str(self.nb)+" "+str(self.moy())
            s+= " "+str(self.et()) +" "+str(self.min)+" "+str(self.max)
        return s

    def strVAHM(self):
        """ Retourne une string avec les resultats, apres conversion de minutes en heures et minutes. """
        s = self.nom+" ---"
        if (self.nb>0):
            m = int(self.moy()) 
            e = self.et()
            s = self.nom+" n/moy/rng/minmax: "+str(self.nb)+" "+str(m/60)+"h"+str(m%60)+" "+str(e/60)+"h"+str(e%60)
            s += " "+str( self.min/60 )+"h"+str( self.min%60 )+" "+str( self.max/60 )+"h"+str( self.max%60 )
        return s                    
# fin class StatVA


class Datastore(object):
    """ Conserve des donnes sous forme de string et les sauve dans un fichier. """
    def __init__(self,nom="no_name",entete=""):
        self.nom=nom # du fichier
        self.store=[]
        if len(entete)>0:
            self.store.append(entete)

    def add(self,s):
        """Add une ligne (string) de donnees."""
        self.store.append(s)
        
    def dump(self,s=""):
        """ Sauve les donnees dans le fichier s, sinon on utilise nom.csv """
        if len(s)==0: s=self.nom+".csv"
        f = open(s,'w')
        for li in self.store:
            f.write(li+"\n")
        f.close()
# fin class Datastore
