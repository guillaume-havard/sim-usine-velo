""" Utilitaires pour la generation de nombres pseudo-aleatoires. """

import random

class Gen(object): 
  """ Interface commune aux generateurs. """

  racine=11171   # racine par defaut

  def __init__(self,rac=0):
    # si rac<0, on prends la racine par defaut
    # si rac=0, on genere une racine aleatoire
    # si rac>0, c'est notre nouvelle racine
    if rac==0:
      rnd=random.Random()
      Gen.racine = rnd.randint(1,331513)
    elif rac>0:
      Gen.racine = rac

  def suiv(self):
    None

  def setRacine(self,r):
    if r<0:
      r=-r
    if r>0:
      Gen.racine=r

  def getRacine(self):
    return Gen.racine
# fin de la classe Gen


class GenCL(Gen):
  """ Generateur CL, voir articles de Pierre L'ecuyer. """

  a = 29223    # multiplicateur par defaut
  m = 131071   # module par defaut
  m1 = 1.0 / float(m)

  def setParam(self,a,m):
    GenCL.a=a
    GenCL.m=m
    GenCL.m1 = 1.0 / float(GenCL.m)

  def suiv(self):
    r = ( GenCL.a * Gen.racine ) % GenCL.m
    Gen.racine=r
    return r
# fin de la classe GenCL


class GenU01CL(GenCL):
  """ Generateur U01 base sur CL. """
  def suiv(self):
    r = GenCL.suiv(self)
    u = GenCL.m1 * float(r) 
    return u
# fin de la classe GenU01CL


class GenMRG(Gen):
  """ Generateur MRG, voir articles de Pierre L'ecuyer. """

  a1= 29223   # premier multiplicateur par defaut
  a2= 76704   # second multiplicateur par defaut
  m = 131071  # module par defaut
  m1 = 1.0 / float(m)

  def setParam(self,a1,a2,m):
    GenMRG.a1=a1
    GenMRG.a2=a2
    GenMRG.m=m
    GenCL.m1 = 1.0 / float(GenCL.m)

  def __init__(self,rac=0):
    Gen.__init__(self,rac)
    self.racine_prev=0   # on conserve la racine precedente pour la recurrence

  def suiv(self):
    r = ( GenMRG.a1 * Gen.racine + GenMRG.a2 * self.racine_prev ) % GenMRG.m
    self.racine_prev=Gen.racine
    Gen.racine=r
    return r
# fin de la classe GenMRG


class GenU01MRG(GenMRG):
  """ Generateur U01 base sur MRG. """

  def suiv(self):
    r = GenMRG.suiv(self)
    u = GenMRG.m1 * float(r)
    return u
# fin de la classe GenU01MRG


class GenU01R():
  """ Generateur U01 base sur random de Python. """

  def suiv(self):
    return random.random()
# fin de la classe GenU01R


class GenDe(GenU01MRG):
  """ Generateur d'un de a n faces. """

  def __init__(self,n,rac=0):
    GenU01MRG.__init__(self,rac)
    self.n=n
    self.eps= 1.0 / float(self.n)

  def suiv(self):
    u=GenU01MRG.suiv(self)
    alpha = self.eps
    ifinal = 0
    for i in range(self.n):
      if (u<alpha):
        ifinal = i+1
        break
      else :
         alpha+=self.eps
    return ifinal
# fin de la classe GenDe




