""" Modele de data pour simulation de l'usine. """

class Da(object):
    """ espace de nomage pour la configuration du modele. """
      
    # Pour arete infinie
    arete_Inf = 999999
    
    # Periode usine de cadre : 2 cadres par minute, donc T = 3600 / 120 = 30
    periode_usine_cadre = 30
    
    # Taille de la chaine cadres -> assemblage.
    taille_chaine =  88
    # Periode d'assemblage pour les vélos
    periode_assemblage = 37.2
    # taille de l'entrepot d'arrive des kits.
    t_entrepot_kits = arete_Inf
    
# fin de la classe Da








