import string, sys, _thread
from tkinter import *
from time import sleep
from modele import *

class GUI:
    """ Interface de simulation graphique d'un modele. 
        On suppose que tous les parametres de simulation sont interne au
        modele. 
        Contraintes:
          * la classe Modele est dans modele.py 
          * le seul parametre de Modele.init est un int de duree de la 
            simulation
          * la simulation se fait par une boucle sur Modele.update()
          * la boucle de simulation termine lorsque Modele.update() retourne 
            false
          * il faut Modele.renderNow(g) qui render le modele dans le canvas g
          * le parametre rendering_step determiner la frequence d'affichage
        Cree un frame dans la fenetre master (aka root), dans lequel 
        on place verticalement (TOP) deux autres frames:
         * bframe: pour les boutons de controle GUI
         * gframe: pour le canvas avec le graphe
    """
  
    def __init__(self, master):
        self.days=2 # nb de jours de la simulation
        #self.rendering_step=600 # nb de pas entre 2 rendering
        self.rendering_step=3600 # nb de pas entre 2 rendering

        self.first=True # controle de demarrage du thread au debut de la simulation
        self.ok=True # controle de fin de l'execution de la boucle de simulation/rendering    
        
        self.frame = Frame(master)
        self.frame.pack()
        
        self.bframe=Frame(self.frame)
        self.bframe.pack(side=TOP)
        
        self.gframe=Frame(self.frame,bd=2,relief=RAISED)
        self.g=Canvas(self.gframe,bg='white',width=900,height=430) # best 900x450
        self.g.pack()
        self.gframe.pack(side=TOP)
    
        self.buttonPrint = Button(self.bframe, text="Print", fg="black", 
                                  command=self.prt)
        self.buttonPrint.pack(side=LEFT, padx=5)
        
        self.w1 = Label(self.bframe, text="Rendering (steps):")
        self.w1.pack(side=LEFT)
        self.e1 = Entry(self.bframe,width=8)
        self.e1.pack(side=LEFT, padx=5)
        self.e1.delete(0, END)
        self.e1.insert(0, str(self.rendering_step))
        
        self.w2 = Label(self.bframe, text="Refresh:")
        self.w2.pack(side=LEFT)
        self.sc = Scale(self.bframe, from_=-10, to=10, orient=HORIZONTAL)
        self.sc.pack(side=LEFT, padx=5)
    
        self.w3 = Label(self.bframe, text="Days:")
        self.w3.pack(side=LEFT)
        self.e2 = Entry(self.bframe,width=8)
        self.e2.pack(side=LEFT, padx=5)
        self.e2.delete(0, END)
        self.e2.insert(0, str(self.days))
        
        self.buttonQuit = Button(self.bframe, text="Quit", fg="red",
                                 command=self.bframe.quit)
        self.buttonQuit.pack(side=LEFT, padx=5)
    
        # etat: 0-non loaded, 1-en pause, 2-running
        self.etat=0
        self.buttonRun = Button(self.bframe, text="Load")
        self.buttonRun.pack(side=LEFT)  
        self.buttonRun.config(command=self.runit)
  
    def prt(self):
        L,T,R,B=self.g.bbox(ALL); R+=20
        self.g.postscript(file="sim.ps",height=B,width=R,pageheight=B,
                          pagewidth=R,x=0,y=0)
  
    def runit(self):
        # transition de l'etat pause(1) vers l'etat running(2)
        if (self.etat == 1):
            refr = int(self.sc.get())
            if refr<0: self.refresh=0.5+refr*0.05
            else: self.refresh=0.5+refr*0.2
            self.rendering_step=int(self.e1.get())
            print("running",self.rendering_step,self.refresh)
            self.buttonRun.config(text="Pause")
            self.etat=2
            # au premier click sur le bouton "run" on cree le thread du modele
            # il va s'updater et s'afficher jusqu'a la fin, et reagir a l'etat 
            # des boutons
            if (self.first):
                self.first=False
                _thread.start_new_thread(self.rendering,())
        # transition de l'etat running(2) vers l'etat pause(1)
        elif (self.etat == 2):
            print("en pause")
            self.buttonRun.config(text="Run", fg="DarkGreen")
            self.etat=1
        # transition de l'etat initial de loading (0) vers l'etat pause(1)
        else:
            self.days=int(self.e2.get())
            print("loading")
            self.buttonRun.config(text="Run", fg="DarkGreen")
            self.etat=1
            self.modele=Modele(self.days) # initialisation (load) du modele
            self.modele.renderNow(self.g) # premier affichage du modele (etat initial)
            self.g.update()
        
    def rendering(self):
        # boucle infinie de rendering
        while (self.ok): 
            i=0
            while (self.ok and i<self.rendering_step):
                i+=1
                self.ok=self.modele.update() # mise a jour du modele
            self.g.delete(ALL) # clean du canvas
            self.modele.renderNow(self.g) # affichage des resultats
            self.g.update()  # affiche le canvas
            sleep(self.refresh) # attente pour le plaisir de l'utilisateur
            while (self.etat != 2): sleep(1) # lorsque le bouton pause est utilise
   
root = Tk()
root.title("Simulation - Cas dégénéré")
  
app = GUI(root)
  
root.mainloop()
