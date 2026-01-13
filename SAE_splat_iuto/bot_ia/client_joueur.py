# coding: utf-8
"""
Projet Splat'IUT'O

Licence pédagogique — usage académique uniquement                                                    
Copyright (c) 2026 Limet Sébastien / IUT'O, Université d'Orléans

Ce code est fourni exclusivement dans un cadre pédagogique.
Les étudiants sont autorisés à l’utiliser et le modifier uniquement
pour les besoins du projet évalué dans le cadre de la SAE1.02 du BUT Informatique d'Orléans.

Toute diffusion, publication ou réutilisation en dehors de ce cadre,
notamment sur des plateformes publiques, est interdite sans
autorisation écrite préalable de l’auteur.

Tous droits réservés.

Module contenant l'implémentation de l'IA et le programme principal du joueur
"""


import argparse
import random

from bot_ia  import client
from bot_ia  import const
from bot_ia  import plateau
from bot_ia  import case
from bot_ia  import joueur

def mon_IA(ma_couleur,carac_jeu, le_plateau, les_joueurs):
    """ Cette fonction permet de calculer les deux actions du joueur de couleur ma_couleur
        en fonction de l'état du jeu décrit par les paramètres. 
        Le premier caractère est parmi XSNOE X indique pas de peinture et les autres
        caractères indique la direction où peindre (Nord, Sud, Est ou Ouest)
        Le deuxième caractère est parmi SNOE indiquant la direction où se déplacer.

    Args:
        ma_couleur (str): un caractère en majuscule indiquant la couleur du joueur
        carac_jeu (dict)): un dictionnaire donnant les valeurs des caractéristiques du jeu:
             duree_actuelle, duree_totale, reserve_initiale, duree_obj, penalite, bonus_touche,
             bonus_recharge, bonus_objet et distance_max,
        le_plateau (dict): l'état du plateau actuel sous la forme décrite dans plateau.py
        les_joueurs (list[joueur]): la liste des joueurs avec leurs caractéristiques utilisant l'API
         joueur.py

    Returns:
        str: une chaine de deux caractères en majuscules indiquant la direction de peinture
            et la direction de déplacement
    """
    return random.choice("XNSOE")+random.choice("NSEO")
    # if joueur.get_reserve(les_joueurs[ma_couleur]) <= 0:
    #     cible = position_ma_couleur_proche(
    #         le_plateau,
    #         joueur.get_position(les_joueurs[ma_couleur]),
    #         (plateau.get_nb_lignes(le_plateau) + plateau.get_nb_colonnes(le_plateau)) // 4,
    #         ma_couleur
    #     )
    #     # Si aucune case de ma couleur n'est trouvée, bouger aléatoirement
    #     if cible is None:
    #         choice = 'X' + random.choice("NSEO")
    #     else:
    #         choice = 'X' + se_deplacer(le_plateau, joueur.get_position(les_joueurs[ma_couleur]), cible)
    # else:
    #     choice = random.choice("XNSOE") + random.choice("NSEO")

    # return choice





def se_deplacer(pos_dep, pos_arr, distance_max, ma_couleur):
    # Initialisation des variables
    res = dict()

    prochaines = [(pos, 0)]
    deja_visites = {pos}

    direction = [(1, 0, 'S'), (-1, 0, 'N'), (0, 1, 'E'), (0, -1, 'O')]

    # Tant qu'il y a des cases à regarder
    while len(prochaines) != 0:
        # On récupère la position de la case et la distance à la case de départ
        pos, nb = prochaines.pop(0)

        # Si la distance est en dessous de distance_max
        if nb < distance_max:
            # Pour chaque direction
            for ligne, colonne, lettre in direction:
                # On prend la prochaine position, on regarde si on ne l'a pas déjà regardé, si elle est sur le plateau et si ce n'est pas un mur: On l'ajoute à prochaines
                prochaine_pos = (pos[0] + ligne, pos[1] + colonne)
                if prochaine_pos not in deja_visites and 0 <= prochaine_pos[0] < plateau.get_nb_lignes(plateau) and 0 <= prochaine_pos[1] < plateau.get_nb_colonnes(plateau) and not case.est_mur(plateau.get_case(plateau, prochaine_pos)):
                    prochaines.append((prochaine_pos, nb + 1))
                    deja_visites.add(prochaine_pos)

            # On récupère la case de la position actuelle
            case_actuelle = plateau.get_case(plateau, pos)

            # On récupère les joueurs et les objets de la case
            couleur = case.get_couleur(case_actuelle)

            

            if couleur == ma_couleur:
                res[nb] = pos

    petit = (None, None)

    for distance, pos in res.items():
        if petit[0] == None or distance < petit[0]:
            petit = (distance, pos)
        
    return petit[1]


def position_ma_couleur_proche(plateau, pos, distance_max, ma_couleur):
    """calcul les distances entre la position pos entre une case de ma couleur du plateau en se limitant à la distance max.

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): une paire d'entiers indiquant la postion de calcul des distances
        distance_max (int): un entier indiquant la distance limite de la recherche
        ma_couleur (str) : un caractere indiquant la couleur de notre equipe
    Returns:
        dict: un dictionnaire dont les clés sont des distances et les valeurs sont des ensembles
            contenant des couleurs.
    """
    # Initialisation des variables
    res = dict()

    prochaines = [(pos, 0)]
    deja_visites = {pos}

    direction = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    # Tant qu'il y a des cases à regarder
    while len(prochaines) != 0:
        # On récupère la position de la case et la distance à la case de départ
        pos, nb = prochaines.pop(0)

        # Si la distance est en dessous de distance_max
        if nb < distance_max:
            # Pour chaque direction
            for ligne, colonne in direction:
                # On prend la prochaine position, on regarde si on ne l'a pas déjà regardé, si elle est sur le plateau et si ce n'est pas un mur: On l'ajoute à prochaines
                prochaine_pos = (pos[0] + ligne, pos[1] + colonne)
                if prochaine_pos not in deja_visites and 0 <= prochaine_pos[0] < plateau.get_nb_lignes(plateau) and 0 <= prochaine_pos[1] < plateau.get_nb_colonnes(plateau) and not case.est_mur(plateau.get_case(plateau, prochaine_pos)):
                    prochaines.append((prochaine_pos, nb + 1))
                    deja_visites.add(prochaine_pos)

            # On récupère la case de la position actuelle
            case_actuelle = plateau.get_case(plateau, pos)

            # On récupère les joueurs et les objets de la case
            couleur = case.get_couleur(case_actuelle)

            

            if couleur == ma_couleur:
                res[nb] = pos

    petit = (None, None)

    for distance, pos in res.items():
        if petit[0] == None or distance < petit[0]:
            petit = (distance, pos)
        
    return petit[1]

#     print(les_joueurs[ma_couleur])
#     print("\n\n")

# {'A': {'couleur': 'A', 'nom': 'joueur2', 'reserve': 4, 'surface': 9, 'points': 78, 'position': (5, 9), 'objet': 0, 'duree': 0}, 'B': {'couleur': 'B', 'nom': 'joueur3', 'reserve': 11, 'surface': 4, 'points': 25, 'position': (2, 3), 'objet': 0, 'duree': 0}, 'C': {'couleur': 'C', 'nom': 'joueur1', 'reserve': -1, 'surface': 13, 'points': 111, 'position': (8, 7), 'objet': 0, 'duree': 0}, 'D': {'couleur': 'D', 'nom': 'joueur4', 'reserve': 6, 'surface': 11, 'points': 79, 'position': (7, 13), 'objet': 0, 'duree': 0}}

    # IA complètement aléatoire
    # return random.choice("XNSOE")+random.choice("NSEO")

if __name__=="__main__":
    noms_caracteristiques=["duree_actuelle","duree_totale","reserve_initiale","duree_obj","penalite","bonus_touche",
            "bonus_recharge","bonus_objet","distance_max"]
    parser = argparse.ArgumentParser()  
    parser.add_argument("--equipe", dest="nom_equipe", help="nom de l'équipe", type=str, default='Non fournie')
    parser.add_argument("--serveur", dest="serveur", help="serveur de jeu", type=str, default='localhost')
    parser.add_argument("--port", dest="port", help="port de connexion", type=int, default=1111)
    
    args = parser.parse_args()
    le_client=client.ClientCyber()
    le_client.creer_socket(args.serveur,args.port)
    le_client.enregistrement(args.nom_equipe,"joueur")
    ok=True
    while ok:
        ok,id_joueur,le_jeu=le_client.prochaine_commande()
        if ok:
            val_carac_jeu,etat_plateau,les_joueurs=le_jeu.split("--------------------\n")
            joueurs={}
            for ligne in les_joueurs[:-1].split('\n'):
                lejoueur=joueur.joueur_from_str(ligne)
                joueurs[joueur.get_couleur(lejoueur)]=lejoueur
            le_plateau=plateau.Plateau(etat_plateau)
            val_carac=val_carac_jeu.split(";")
            carac_jeu={}
            for i in range(len(noms_caracteristiques)):
                carac_jeu[noms_caracteristiques[i]]=int(val_carac[i])
    
            actions_joueur=mon_IA(id_joueur,carac_jeu,le_plateau,joueurs)
            le_client.envoyer_commande_client(actions_joueur)
            # le_client.afficher_msg("sa reponse  envoyée "+str(id_joueur)+args.nom_equipe)
    le_client.afficher_msg("terminé")
