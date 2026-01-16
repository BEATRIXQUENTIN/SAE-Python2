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
    # Nos variables
    notre_position = joueur.get_pos(les_joueurs[ma_couleur])
    notre_reserve = joueur.get_reserve(les_joueurs[ma_couleur])
    dir_objet_proche, objet_proche = trouver_direction_objet(le_plateau, notre_position)
    bidon = trouver_direction_bidon(le_plateau, notre_position)
    objet_actuel = joueur.get_objet(les_joueurs[ma_couleur])

    # Si on a une reserve basse/négative
    if notre_reserve < 4:
        # S'il y a un bidon sur la carte, on va le chercher
        if bidon != None:
            return 'X' + bidon
        else:
            # Sinon on va sur notre couleur
            return 'X' + trouver_direction_recharge(le_plateau, notre_position, ma_couleur)
    
    # Si on a un objet :
    elif objet_actuel != const.AUCUN:
        # Si on a le pistolet :
        if objet_actuel == const.PISTOLET:
            # Et que sa durée est à plus de 1 :
            if joueur.get_duree(les_joueurs[ma_couleur]) > 1:
                # On essaie de trouver des murs à peindre
                peinture_possible = directions_murs(le_plateau, notre_position)
                # S'il n'y a pas de murs on peint
                if len(peinture_possible) == 0:
                    peinture = 'X'
                else:
                    # Sinon on peint un des murs autour de nous
                    peinture = random.choice(peinture_possible)
                
                # On regarde nos déplacement possibles
                deplacement_possible = plateau.directions_possibles(le_plateau, notre_position)
                deplacement = ""
                # Si la case est de notre couleur on l'ajoute à deplacement
                for dir in deplacement_possible:
                    if deplacement_possible[dir] == ma_couleur:
                        deplacement += dir

                # Si deplacement est vide il n'y a pas de case de notre couleur à côté donc on se dirige vers nos cases de couleurs plus loin
                if len(deplacement) == 0:
                    deplacement = trouver_direction_recharge(le_plateau, notre_position, ma_couleur)
                # Si c'est toujours vide, on est à 0 de surface donc on se déplace aléatoirement
                if len(deplacement) == 0:
                    deplacement = 'NSOE'
                deplacement = random.choice(deplacement)
                return peinture+deplacement
            else:
                # Si le pistolet à une durée de 1 tour
                direction = trouver_direction_autre_couleur(le_plateau, notre_position, ma_couleur)

                # On tire la où on se déplace (forcément, sauf si notre réserve est vide)
                peinture = tir_opti(direction, notre_position, ma_couleur, le_plateau)

                # Si tir_opti renvoi de ne pas tirer on tire quand même aléatoirement
                if peinture == 'X':
                    peinture = random.choice('NOSE')

                return peinture + direction

        else:
            # Pour les autres objet on attaque forécement
            direction = trouver_direction_autre_couleur(le_plateau, notre_position, ma_couleur)
            direction = random.choice(direction)
            return direction+direction
        
    elif (objet_proche == const.PISTOLET) or (dir_objet_proche != None and notre_reserve < 15):
        # S'il y a un objet et on a une bonne réserve on y va OU que l'objet c'est un pistolet alors on y va aussi
        direction = dir_objet_proche
        peinture = tir_opti(direction, notre_position, ma_couleur, le_plateau)
        return peinture+direction
    
    elif notre_reserve >= 4:
        # Si pas d'objet on attaque

        if carac_jeu["duree_actuelle"] > 50:
            # Si ça fait plus de 50 tours qui sont passé, alors on attaque celui qui a le plus de points (si c'est nous on attaque le 2ème)

            classement = joueur.classement_joueurs(list(les_joueurs.values()), "points")
            couleur_cible = None

            # Au cas où s'il y a moins de 2 joueurs (impossible)
            if len(classement) > 1:
                
                # On récupère la couleur de la cible
                if joueur.get_couleur(classement[0]) == ma_couleur:
                    couleur_cible = joueur.get_couleur(classement[1])
                else:
                    couleur_cible = joueur.get_couleur(classement[0])

                # On s'y dirige
                direction = trouver_direction_cible(le_plateau, notre_position, couleur_cible)

                if direction != None:
                    peinture = tir_opti(direction, notre_position, ma_couleur, le_plateau)
                    return peinture + direction
            
            # Au cas où si la personne n'a pas de surface
            direction = trouver_direction_autre_couleur(le_plateau, notre_position, ma_couleur)
            peinture = tir_opti(direction, notre_position, ma_couleur, le_plateau)
            return peinture+direction
        
        else:
            # Si ça fait moins de 50 tours qui sont passé, on peint tout ce qui est possible
            direction = trouver_direction_autre_couleur(le_plateau, notre_position, ma_couleur)
            peinture = tir_opti(direction, notre_position, ma_couleur, le_plateau)
            return peinture+direction

    else:
        # Si aucune condition n'est valide
        direction = trouver_direction_recharge(le_plateau, notre_position, ma_couleur)
        peinture = tir_opti(direction, notre_position, ma_couleur, le_plateau)
        return peinture+direction


def est_sur_plateau(le_plateau, pos):
    """Vérifie si pos est sur le_plateau

    Args:
        le_plateau (dict): Le plateau actuel
        pos (tuple): Une position

    Returns:
        bool: True si la position est sur le plateau, False sinon
    """
    # Variable pour le nombre de ligne et le nombre de colonnne du plateau
    nb_lignes = plateau.get_nb_lignes(le_plateau)
    nb_colonnes = plateau.get_nb_colonnes(le_plateau)

    return 0 <= pos[0] < nb_lignes and 0 <= pos[1] < nb_colonnes
    # Complexité O(1)


def tir_opti(direction, notre_position, ma_couleur, le_plateau):
    """Permet de donner une direction pour tirer de façon optimal

    Args:
        direction (str): La direction dans laquelle on va
        notre_position (tuple): Notre position actuelle
        ma_couleur (str): Notre couleur
        le_plateau (dict): Le plateau actuel

    Returns:
        str: La direction de la peinture
    """
    # Initialisation des variables
    peinture = 'X'
    ligne, colonne = plateau.INC_DIRECTION[direction]
    nouvelle_pos = (notre_position[0] + ligne, notre_position[1] + colonne)

    # On regarde si la nouvelle position est sur le plateau et si la couleur est différente de la notre
    if est_sur_plateau(le_plateau, nouvelle_pos) and case.get_couleur(plateau.get_case(le_plateau, nouvelle_pos)) != ma_couleur:
        peinture = direction
    return peinture
    # Complexité O(1)


def directions_murs(le_plateau,pos):
    """Permet de savoir la direction où il y a des murs

    Args:
        le_plateau (dict): Le plateau actuel
        pos (tuple): La position de départ

    Returns:
        str: Les directions où il y a des murs
    """
    # Initialisation des variables
    direction_possibles = ""
    ligne, colonne = pos

    # Pour chaque direction
    for direction, (dirl, dirc) in plateau.INC_DIRECTION.items():

        if direction != 'X': # Si ce n'est pas le X (ne pas bouger)
        
            # On prend la nouvelle position
            nouvelle_pos = (ligne + dirl, colonne + dirc)

            # On vérifie si elle est dans le plateau pour récupérer la case
            if est_sur_plateau(le_plateau, nouvelle_pos):
                la_case = plateau.get_case(le_plateau, nouvelle_pos)

                if case.est_mur(la_case):
                    direction_possibles+=direction

    return direction_possibles


def trouver_direction_objet(le_plateau, pos_depart):
    """Permet de trouver le plus court chemin vers objet à partir de pos_depart

    Args:
        le_plateau (dict): Le plateau actuel
        pos_depart (tuple): La position de départ

    Returns:
        tuple: Un tuple de str, int représentant la direction à prendre et l'objet vers lequel on va
    """
    # Initialisation des variables
    file_attente = [pos_depart]
    predecesseurs = {pos_depart: (None, 0)}

    # Tant que la file d'attente n'est pas vide, on prend les voisins et on recommence,
    # On vérifie si la case contient un objet si c'est le cas on donne la direction du chemin à prendre pour y aller
    while len(file_attente) != 0:
        pos_courante = file_attente.pop(0)
        la_case = plateau.get_case(le_plateau, pos_courante)
        objet = case.get_objet(la_case)

        # S'il y a un objet on fait le chemin inverse pour trouver le plus court chemin pour y parvenir
        if pos_courante != pos_depart and objet != const.AUCUN:

            curr = pos_courante
            while predecesseurs[curr] != pos_depart:
                curr = predecesseurs[curr]

            delta_lig = curr[0] - pos_depart[0]
            delta_col = curr[1] - pos_depart[1]

            if delta_lig == -1: return 'N',objet
            if delta_lig == 1:  return 'S',objet
            if delta_col == 1:  return 'E',objet
            if delta_col == -1: return 'O',objet

        # Sinon met les voisins de la case dans la file d'attente (sans revenir en arrière)
        for d_l, d_c in plateau.INC_DIRECTION.values():
            voisin = (pos_courante[0] + d_l, pos_courante[1] + d_c)

            if (est_sur_plateau(le_plateau, voisin) and 
                voisin not in predecesseurs):

                case_voisine = plateau.get_case(le_plateau, voisin)
                if not case.est_mur(case_voisine):
                    predecesseurs[voisin] = pos_courante
                    file_attente.append(voisin)

    return None, None # Si aucun objet sur la carte
    # Complexité O(N) car on fait toute la carte au maximum je pense

def trouver_direction_bidon(le_plateau, pos_depart):
    """Permet de trouver le plus court chemin vers un bidon à partir de pos_depart

    Args:
        le_plateau (dict): Le plateau actuel
        pos_depart (tuple): La position de départ

    Returns:
        str: La direction du plus court chemin vers un bidon, ou None s'il n'y en a pas
    """
    # Initialisation des variables
    file_attente = [pos_depart]
    predecesseurs = {pos_depart: None}

    # Tant que la file d'attente n'est pas vide, on prend les voisins et on recommence,
    # On vérifie si la case contient un bidon si c'est le cas on donne la direction du chemin à prendre pour y aller
    while len(file_attente) != 0:
        pos_courante = file_attente.pop(0)
        la_case = plateau.get_case(le_plateau, pos_courante)

        # S'il y a un bidon on fait le chemin inverse pour trouver le plus court chemin pour y parvenir
        if pos_courante != pos_depart and case.get_objet(la_case) == const.BIDON:

            curr = pos_courante
            while predecesseurs[curr] != pos_depart:
                curr = predecesseurs[curr]

            delta_lig = curr[0] - pos_depart[0]
            delta_col = curr[1] - pos_depart[1]

            if delta_lig == -1: return 'N'
            if delta_lig == 1:  return 'S'
            if delta_col == 1:  return 'E'
            if delta_col == -1: return 'O'

        # Sinon met les voisins de la case dans la file d'attente (sans revenir en arrière)
        for d_l, d_c in plateau.INC_DIRECTION.values():
            voisin = (pos_courante[0] + d_l, pos_courante[1] + d_c)

            if (est_sur_plateau(le_plateau, voisin) and 
                voisin not in predecesseurs):

                case_voisine = plateau.get_case(le_plateau, voisin)
                if not case.est_mur(case_voisine):
                    predecesseurs[voisin] = pos_courante
                    file_attente.append(voisin)

    return None # Si aucun objet sur la carte
    # Complexité O(N) comme les autres


def trouver_direction_recharge(le_plateau, pos_depart, ma_couleur):
    """Permet de trouver le plus court chemin vers un bidon à partir de pos_depart

    Args:
        le_plateau (dict): Le plateau actuel
        pos_depart (tuple): La position de départ
        ma_couleur (str): Notre couleur

    Returns:
        str: La direction du plus court chemin vers un bidon, ou une direction random au cas où
    """
    # Initialisation des variables
    file_attente = [pos_depart]
    predecesseurs = {pos_depart: None}
    chemin_secours = None 

    # Tant que la file d'attente n'est pas vide, on prend les voisins et on recommence,
    # On vérifie si la case contient notre couleur si c'est le cas, on vérifie s'il un voisin contient aussi notre couleur -> on donne la direction du chemin à prendre pour y aller si c'est vrai (Si on ne trouve pas au moins 2 cases on donne le plus court chemin vers une case seule)
    while len(file_attente) != 0:
        pos_courante = file_attente.pop(0)
        la_case = plateau.get_case(le_plateau, pos_courante)

        # S'il y a notre couleur on fait le chemin inverse pour trouver le plus court chemin pour y parvenir
        if pos_courante != pos_depart and case.get_couleur(la_case) == ma_couleur:
            curr = pos_courante
            while predecesseurs[curr] != pos_depart:
                curr = predecesseurs[curr]
            
            delta_lig = curr[0] - pos_depart[0]
            delta_col = curr[1] - pos_depart[1]
            if delta_lig == -1: dir_secours = 'N'
            elif delta_lig == 1:  dir_secours = 'S'
            elif delta_col == 1:  dir_secours = 'E'
            elif delta_col == -1: dir_secours = 'O'
            
            # On garde en mémoire le chemin de secours vers la case seule
            if chemin_secours is None:
                chemin_secours = dir_secours

            a_un_voisin_ami = False
            for lig, col in plateau.INC_DIRECTION.values():
                if (lig, col) != (0,0):
                    voisin_test = (pos_courante[0] + lig, pos_courante[1] + col)
                    if est_sur_plateau(le_plateau, voisin_test) and case.get_couleur(plateau.get_case(le_plateau, voisin_test)) == ma_couleur:
                        a_un_voisin_ami = True
            
            # Si deux cases côte à côte en va vers celles-ci
            if a_un_voisin_ami:
                return dir_secours

        # Sinon met les voisins de la case dans la file d'attente (sans revenir en arrière)
        for d_l, d_c in plateau.INC_DIRECTION.values():
                voisin = (pos_courante[0] + d_l, pos_courante[1] + d_c)

                if (est_sur_plateau(le_plateau, voisin) and 
                    voisin not in predecesseurs):

                    case_voisine = plateau.get_case(le_plateau, voisin)
                    if not case.est_mur(case_voisine):
                        predecesseurs[voisin] = pos_courante
                        file_attente.append(voisin)

    # Si pas 2 cases côte à côte en prend le chemin de secours (case seule)
    if chemin_secours:
        return chemin_secours
        
    return random.choice("NSEO") # Au cas où (normalement on y va jamais)
    # Complexité O(N) car je pense au maximum on fait toutes les cases du plateau

def trouver_direction_cible(le_plateau, pos_depart, couleur_cible):
    """Permet de trouver le plus court chemin vers un bidon à partir de pos_depart

    Args:
        le_plateau (dict): Le plateau actuel
        pos_depart (tuple): La position de départ
        couleur_cible (str): La couleur qui est ciblé

    Returns:
        str: La direction du plus court chemin vers un bidon, ou None s'il n'y en a pas
    """
    # Initialisation des variables
    file_attente = [pos_depart]
    predecesseurs = {pos_depart: None}

    # Tant que la file d'attente n'est pas vide, on prend les voisins et on recommence,
    # On vérifie si la case contient couleur_cible si c'est le cas on donne la direction du chemin à prendre pour y aller
    while len(file_attente) != 0:
        pos_courante = file_attente.pop(0)
        la_case = plateau.get_case(le_plateau, pos_courante)

        # S'il y a couleur_cible sur la case on fait le chemin inverse pour trouver le plus court chemin pour y parvenir
        if pos_courante != pos_depart and case.get_couleur(la_case) == couleur_cible:
            curr = pos_courante
            while predecesseurs[curr] != pos_depart:
                curr = predecesseurs[curr]
            
            delta_lig = curr[0] - pos_depart[0]
            delta_col = curr[1] - pos_depart[1]

            if delta_lig == -1: return 'N'
            if delta_lig == 1:  return 'S'
            if delta_col == 1:  return 'E'
            if delta_col == -1: return 'O'

        # Sinon met les voisins de la case dans la file d'attente (sans revenir en arrière)
        for d_l, d_c in plateau.INC_DIRECTION.values():
            voisin = (pos_courante[0] + d_l, pos_courante[1] + d_c)
            if (est_sur_plateau(le_plateau, voisin) and 
                voisin not in predecesseurs):
                
                case_voisine = plateau.get_case(le_plateau, voisin)
                if not case.est_mur(case_voisine):
                    predecesseurs[voisin] = pos_courante
                    file_attente.append(voisin)
    return None # Si aucune couleur de la personne sur la carte on renvoie None
    # Complexité O(N) comme les autres


def trouver_direction_autre_couleur(le_plateau, pos_depart, ma_couleur):
    """Permet de trouver le plus court chemin vers un bidon à partir de pos_depart

    Args:
        le_plateau (dict): Le plateau actuel
        pos_depart (tuple): La position de départ
        ma_couleur (str): Notre couleur (celle à ne pas viser)

    Returns:
        str: La direction du plus court chemin vers un bidon
    """
    # Initialisation des variables
    file_attente = [pos_depart]
    predecesseurs = {pos_depart: None}

    # Tant que la file d'attente n'est pas vide, on prend les voisins et on recommence,
    # On vérifie si la case contient une autre couleur que la notre si c'est le cas on donne la direction du chemin à prendre pour y aller
    while len(file_attente) != 0:
        pos_courante = file_attente.pop(0)
        la_case = plateau.get_case(le_plateau, pos_courante)

        # S'il y a couleur_cible sur la case on fait le chemin inverse pour trouver le plus court chemin pour y parvenir
        if pos_courante != pos_depart and case.get_couleur(la_case) != ma_couleur:

            curr = pos_courante
            while predecesseurs[curr] != pos_depart:
                curr = predecesseurs[curr]

            delta_lig = curr[0] - pos_depart[0]
            delta_col = curr[1] - pos_depart[1]

            if delta_lig == -1: return 'N'
            if delta_lig == 1:  return 'S'
            if delta_col == 1:  return 'E'
            if delta_col == -1: return 'O'

        # Sinon met les voisins de la case dans la file d'attente (sans revenir en arrière)
        for d_l, d_c in plateau.INC_DIRECTION.values():
            voisin = (pos_courante[0] + d_l, pos_courante[1] + d_c)

            if (est_sur_plateau(le_plateau, voisin) and 
                voisin not in predecesseurs):

                case_voisine = plateau.get_case(le_plateau, voisin)
                if not case.est_mur(case_voisine):
                    predecesseurs[voisin] = pos_courante
                    file_attente.append(voisin)

    return random.choice("NSEO") # Si aucune couleur de la personne sur la carte on renvoi une direction random (ça veut dire on a peint tout le plateau)
    # Complexité O(N) comme les autres

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
