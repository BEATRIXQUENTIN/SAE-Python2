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


def mon_IA(ma_couleur, carac_jeu, le_plateau, les_joueurs):

    notre_position = joueur.get_pos(les_joueurs[ma_couleur])
    reserve = joueur.get_reserve(les_joueurs[ma_couleur])
    objet = joueur.get_objet(les_joueurs[ma_couleur])
    autour = plateau.directions_possibles(le_plateau, notre_position)
    objet_proche = trouver_direction_objet(le_plateau, notre_position)
    objet_actuel = joueur.get_objet(les_joueurs[ma_couleur])
    ma_case_proche = position_ma_case_plus_proche(le_plateau, notre_position, ma_couleur)

    if reserve < 2:

        bidon = trouver_direction_bidon(le_plateau, notre_position, 4)
        if bidon is not None:
            return 'X' + bidon

        if ma_case_proche is not None:
            directions_autour = plateau.directions_possibles(le_plateau, ma_case_proche)

            if ma_couleur in directions_autour.values():
                return 'X' + trouver_direction_recharge(le_plateau, notre_position, ma_couleur)

            bidon = trouver_direction_bidon(le_plateau, notre_position, 7)
            if bidon is not None:
                return 'X' + bidon

        if objet_proche is not None:
            return 'X' + objet_proche

        return 'X' + random.choice("NOES")
        
    elif reserve < 6:
        bidon = trouver_direction_bidon(le_plateau, notre_position, 2)
        if bidon is not None:
            return 'X' + bidon
        elif ma_case_proche is not None:
            directions_autour = plateau.directions_possibles(le_plateau, ma_case_proche)
            if ma_couleur in directions_autour.values():
                return 'X' + trouver_direction_recharge(le_plateau, notre_position, ma_couleur)
        else:
            directions_autour = plateau.directions_possibles(le_plateau, notre_position)
            choix = random.choice(directions_autour)
            return choix + choix
        
    elif objet_actuel != plateau.case.const.AUCUN:
        # Si on a le pistolet :
        if objet_actuel == plateau.case.const.PISTOLET:
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
                # Si le pistolet à une durer de 1 tour
                direction = trouver_direction_autre_couleur(le_plateau, notre_position, ma_couleur)

                # peinture_possible = plateau.directions_possibles(le_plateau, notre_position)
                # if len(peinture_possible) == 0:
                #     peinture = 'X'
                # else:
                #     peinture = ""
                #     for peint in peinture_possible:
                #         peinture += peint

                #     if len(peinture) == 0:
                #         peinture = "NOES"
                #     peinture = random.choice(peinture)


                # ligne, colonne = plateau.INC_DIRECTION[direction]
                # nouvelle_pos = (notre_position[0] + ligne, notre_position[1] + colonne)
                # if est_sur_plateau(nouvelle_pos) and case.get_couleur(plateau.get_case(le_plateau, nouvelle_pos)) != ma_couleur:
                #     peinture = direction

                # On tire la où on se déplace (forcément, sauf si notre réserve est vide)
                peinture = tir_opti(direction, notre_position, ma_couleur, le_plateau)

                if peinture == 'X':
                    peinture = random.choice('NOSE')

                return peinture + direction

        else:
            # Pour les autres objet on attaque forécement
            direction = trouver_direction_autre_couleur(le_plateau, notre_position, ma_couleur)
            direction = random.choice(direction)
            return direction+direction
    elif objet_proche == plateau.case.const.PISTOLET:
        # On vise les pistolets en priorité
        direction = objet_proche
        peinture = tir_opti(direction, notre_position, ma_couleur, le_plateau)
        return peinture+direction
    elif objet_proche != None and joueur.get_reserve(les_joueurs[ma_couleur]) < 15:
        # S'il y a un objet et on a une bonne réserve on y va
        direction = objet_proche
        peinture = tir_opti(direction, notre_position, ma_couleur, le_plateau)
        return peinture+direction
    elif joueur.get_reserve(les_joueurs[ma_couleur]) > 5:
        # Si pas d'objet on attaque
        direction = trouver_direction_autre_couleur(le_plateau, notre_position, ma_couleur)
        peinture = tir_opti(direction, notre_position, ma_couleur, le_plateau)
        return peinture+direction
    else:
        # Si aucune condition n'est valide
        direction = trouver_direction_recharge(le_plateau, notre_position, ma_couleur)
        peinture = tir_opti(direction, notre_position, ma_couleur, le_plateau)
        return peinture+direction



def tir_opti(direction, notre_position, ma_couleur, le_plateau):
    peinture = 'X'
    ligne, colonne = plateau.INC_DIRECTION[direction]
    nouvelle_pos = (notre_position[0] + ligne, notre_position[1] + colonne)
    if est_sur_plateau(le_plateau, nouvelle_pos) and case.get_couleur(plateau.get_case(le_plateau, nouvelle_pos)) != ma_couleur:
        peinture = direction
    return peinture


def directions_murs(le_plateau,pos):
    # Initialisation des variables
    direction_possibles = ""
    ligne, colonne = pos
    nb_lignes = plateau.get_nb_lignes(le_plateau)
    nb_colonnes = plateau.get_nb_colonnes(le_plateau)

    # Pour chaque direction
    for direction, (dirl, dirc) in plateau.INC_DIRECTION.items():

        if direction != 'X': # Si ce n'est pas le X (ne pas bouger)
        
            # On prend la nouvelle position
            nouvelle_pos = (ligne + dirl, colonne + dirc)

            # On vérifie si elle est dans le plateau pour récupérer la case
            if 0 <= nouvelle_pos[0] < nb_lignes and 0 <= nouvelle_pos[1] < nb_colonnes:
                la_case = plateau.get_case(le_plateau, nouvelle_pos)

                if case.est_mur(la_case):
                    direction_possibles+=direction

    return direction_possibles



def est_sur_plateau(le_plateau, pos):
    try:
        plateau.get_case(le_plateau, pos)
        return True
    except:
        return False


def trouver_direction_objet(le_plateau, pos_depart):
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

            if (0 <= voisin[0] < nb_lignes and 0 <= voisin[1] < nb_cols and voisin not in predecesseurs):

                case_voisine = plateau.get_case(le_plateau, voisin)
                if not case.est_mur(case_voisine):
                    predecesseurs[voisin] = pos_courante
                    file_attente.append(voisin)

    return None

def trouver_direction_bidon(le_plateau, pos_depart, portee_max):
    file_attente = [(pos_depart, 0)]
    predecesseurs = {pos_depart: None}

    nb_lignes = plateau.get_nb_lignes(le_plateau)
    nb_cols = plateau.get_nb_colonnes(le_plateau)

    while len(file_attente) != 0:
        pos_courante, dist = file_attente.pop(0)

        if dist > portee_max:
            continue

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

            if (0 <= voisin[0] < nb_lignes and 0 <= voisin[1] < nb_cols and voisin not in predecesseurs):

                case_voisine = plateau.get_case(le_plateau, voisin)
                if not case.est_mur(case_voisine):
                    predecesseurs[voisin] = pos_courante
                    file_attente.append((voisin, dist + 1))

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

#def position_ma_case_plus_proche(plateau, position_depart, couleur):
    #return

def position_ma_case_plus_proche(le_plateau, position_depart, ma_couleur):
    file_attente = [position_depart]
    predecesseurs = {position_depart: None}

    nb_lignes = plateau.get_nb_lignes(le_plateau)
    nb_cols = plateau.get_nb_colonnes(le_plateau)

    while len(file_attente) != 0:
        pos_courante = file_attente.pop(0)
        la_case = plateau.get_case(le_plateau, pos_courante)

        # On cherche une case de NOTRE couleur (sauf la case de départ)
        if pos_courante != position_depart and case.get_couleur(la_case) == ma_couleur:
            return pos_courante   # <-- ON RENVOIE DIRECTEMENT LA POSITION

        # Explorer les voisins
        for d_l, d_c in plateau.INC_DIRECTION.values():
            voisin = (pos_courante[0] + d_l, pos_courante[1] + d_c)

            if (0 <= voisin[0] < nb_lignes and
                0 <= voisin[1] < nb_cols and
                voisin not in predecesseurs):

                case_voisine = plateau.get_case(le_plateau, voisin)

                if not case.est_mur(case_voisine):
                    predecesseurs[voisin] = pos_courante
                    file_attente.append(voisin)

    # Si aucune case à nous n'est trouvée
    return None


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
