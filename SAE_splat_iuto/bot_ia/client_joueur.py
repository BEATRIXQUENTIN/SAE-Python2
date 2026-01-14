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
    notre_position = joueur.get_pos(les_joueurs[ma_couleur])
    direction_peinture = plateau.directions_possibles(le_plateau, notre_position)
    choice_peinture = ""
    for dir, couleur in direction_peinture.items():
        if couleur != ma_couleur:
            choice_peinture  += dir


    if len(choice_peinture) == 0:
        choice_peinture = "X"


    objet_proche = trouver_direction_objet(le_plateau, notre_position)
    bidon = trouver_direction_bidon(le_plateau, notre_position)

    # if bidon != None and joueur.get_reserve(les_joueurs[ma_couleur]) < 5:
    #     return 'X' + bidon
    if joueur.get_reserve(les_joueurs[ma_couleur]) <= 0:
        return 'X' + trouver_direction_recharge(le_plateau, notre_position, ma_couleur)
    elif objet_proche != None and joueur.get_reserve(les_joueurs[ma_couleur]) < 15:
        direction = objet_proche
        peinture = 'X'
        ligne, colonne = plateau.INC_DIRECTION[direction]
        nouvelle_pos = (notre_position[0] + ligne, notre_position[1] + colonne)
        if est_sur_plateau(nouvelle_pos) and case.get_couleur(plateau.get_case(le_plateau, nouvelle_pos)) != ma_couleur:
            peinture = direction
        return peinture+direction
    elif joueur.get_reserve(les_joueurs[ma_couleur]) > 10:
        direction = trouver_direction_autre_couleur(le_plateau, notre_position, ma_couleur)
        peinture = 'X'
        ligne, colonne = plateau.INC_DIRECTION[direction]
        nouvelle_pos = (notre_position[0] + ligne, notre_position[1] + colonne)
        if est_sur_plateau(nouvelle_pos) and case.get_couleur(plateau.get_case(le_plateau, nouvelle_pos)) != ma_couleur:
            peinture = direction
        return peinture+direction
    else:
        return random.choice(choice_peinture)+random.choice("NOES")




def est_sur_plateau(pos):
    try:
        plateau.get_case(le_plateau, pos)
        return True
    except:
        return False


def trouver_direction_objet(le_plateau, pos_depart, portee_max=7):
    file_attente = [pos_depart]

    predecesseurs = {pos_depart: (None, 0)}

    nb_lignes = plateau.get_nb_lignes(le_plateau)
    nb_cols = plateau.get_nb_colonnes(le_plateau)

    while len(file_attente) != 0:
        pos_courante = file_attente.pop(0)
        la_case = plateau.get_case(le_plateau, pos_courante)

        if pos_courante != pos_depart and case.get_objet(la_case) != plateau.case.const.AUCUN:

            curr = pos_courante
            while predecesseurs[curr] != pos_depart:
                curr = predecesseurs[curr]

            delta_lig = curr[0] - pos_depart[0]
            delta_col = curr[1] - pos_depart[1]

            if delta_lig == -1: return 'N'
            if delta_lig == 1:  return 'S'
            if delta_col == 1:  return 'E'
            if delta_col == -1: return 'O'

        for d_l, d_c in plateau.INC_DIRECTION.values():
            voisin = (pos_courante[0] + d_l, pos_courante[1] + d_c)

            if (0 <= voisin[0] < nb_lignes and 
                0 <= voisin[1] < nb_cols and 
                voisin not in predecesseurs):

                case_voisine = plateau.get_case(le_plateau, voisin)
                if not case.est_mur(case_voisine):
                    predecesseurs[voisin] = pos_courante
                    file_attente.append(voisin)

    return None

def trouver_direction_bidon(le_plateau, pos_depart):
    file_attente = [pos_depart]

    predecesseurs = {pos_depart: None}

    nb_lignes = plateau.get_nb_lignes(le_plateau)
    nb_cols = plateau.get_nb_colonnes(le_plateau)

    while len(file_attente) != 0:
        pos_courante = file_attente.pop(0)
        la_case = plateau.get_case(le_plateau, pos_courante)

        if pos_courante != pos_depart and case.get_objet(la_case) == plateau.case.const.BIDON:

            curr = pos_courante
            while predecesseurs[curr] != pos_depart:
                curr = predecesseurs[curr]

            delta_lig = curr[0] - pos_depart[0]
            delta_col = curr[1] - pos_depart[1]

            if delta_lig == -1: return 'N'
            if delta_lig == 1:  return 'S'
            if delta_col == 1:  return 'E'
            if delta_col == -1: return 'O'

        for d_l, d_c in plateau.INC_DIRECTION.values():
            voisin = (pos_courante[0] + d_l, pos_courante[1] + d_c)

            if (0 <= voisin[0] < nb_lignes and 
                0 <= voisin[1] < nb_cols and 
                voisin not in predecesseurs):

                case_voisine = plateau.get_case(le_plateau, voisin)
                if not case.est_mur(case_voisine):
                    predecesseurs[voisin] = pos_courante
                    file_attente.append(voisin)

    return None


def trouver_direction_recharge(le_plateau, pos_depart, ma_couleur):
    file_attente = [pos_depart]

    predecesseurs = {pos_depart: None}

    nb_lignes = plateau.get_nb_lignes(le_plateau)
    nb_cols = plateau.get_nb_colonnes(le_plateau)

    while len(file_attente) != 0:
        pos_courante = file_attente.pop(0)
        la_case = plateau.get_case(le_plateau, pos_courante)

        if pos_courante != pos_depart and case.get_couleur(la_case) == ma_couleur:

            curr = pos_courante
            while predecesseurs[curr] != pos_depart:
                curr = predecesseurs[curr]

            delta_lig = curr[0] - pos_depart[0]
            delta_col = curr[1] - pos_depart[1]

            if delta_lig == -1: return 'N'
            if delta_lig == 1:  return 'S'
            if delta_col == 1:  return 'E'
            if delta_col == -1: return 'O'

        for d_l, d_c in plateau.INC_DIRECTION.values():
            voisin = (pos_courante[0] + d_l, pos_courante[1] + d_c)

            if (0 <= voisin[0] < nb_lignes and 
                0 <= voisin[1] < nb_cols and 
                voisin not in predecesseurs):

                case_voisine = plateau.get_case(le_plateau, voisin)
                if not case.est_mur(case_voisine):
                    predecesseurs[voisin] = pos_courante
                    file_attente.append(voisin)

    return random.choice("NSEO")

def trouver_direction_autre_couleur(le_plateau, pos_depart, ma_couleur):
    file_attente = [pos_depart]

    predecesseurs = {pos_depart: None}

    nb_lignes = plateau.get_nb_lignes(le_plateau)
    nb_cols = plateau.get_nb_colonnes(le_plateau)

    while len(file_attente) != 0:
        pos_courante = file_attente.pop(0)
        la_case = plateau.get_case(le_plateau, pos_courante)

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

        for d_l, d_c in plateau.INC_DIRECTION.values():
            voisin = (pos_courante[0] + d_l, pos_courante[1] + d_c)

            if (0 <= voisin[0] < nb_lignes and 
                0 <= voisin[1] < nb_cols and 
                voisin not in predecesseurs):

                case_voisine = plateau.get_case(le_plateau, voisin)
                if not case.est_mur(case_voisine):
                    predecesseurs[voisin] = pos_courante
                    file_attente.append(voisin)

    return random.choice("NSEO")


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
