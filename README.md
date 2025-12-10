# Optimiseur de Tournées (Smart Route Optimizer)

Ce module optimise les itinéraires pour les techniciens d'intervention ou les livreurs, visant à minimiser le temps de trajet en utilisant un algorithme du "Plus Proche Voisin" (Nearest Neighbor). Il introduit un système complet de gestion de **Feuilles de Route**.

## Fonctionnalités

*   **Optimisation de Tournée** : Réorganise automatiquement les tâches pour minimiser la distance de voyage.
*   **Feuilles de Route** : Menu dédié pour gérer les tournées quotidiennes, assigner les chauffeurs et définir les heures de départ (intégrée à l'application **Services sur site**).
*   **Visibilité** : Affichage de la **Ville** de destination directement dans la liste des tâches.
*   **Gestion du Temps** : Calcule efficacement les **Durées de Trajet**, **Durées d'Intervention**, et les **Heures d'Arrivée/Retour Estimées**.
*   **Trajet Retour** : Prend automatiquement en compte le retour au point de départ.
*   **Intégration Google Maps** : Génération en un clic d'un itinéraire GPS complet pour mobile.
*   **Sélection Intelligente** : Outil pour ajouter facilement des tâches non assignées à une route.

## Configuration

### 1. Prérequis
*   Assurez-vous que les **Contacts** (Clients) ont des adresses valides.
*   Le module `base_geolocalize` d'Odoo gère le géocodage. Si les coordonnées manquent, utilisez le bouton "Compute based on address" sur la fiche du Partenaire.

### 2. Adresse de Départ du Technicien
Chaque technicien/chauffeur doit avoir une adresse de départ configurée (ex: Bureau ou Domicile).

1.  Allez dans **Configuration > Utilisateurs et Sociétés > Utilisateurs**.
2.  Ouvrez la fiche Utilisateur.
3.  Allez dans l'onglet **Préférences**.
4.  Localisez la section **Field Service Route**.
5.  Définissez l'**Adresse de Départ par Défaut** (Partenaire).

## Guide d'Utilisation

### 1. Créer une Feuille de Route
1.  Allez dans **Services sur site > Routes**.
2.  Cliquez sur **Nouveau**.
3.  Entrez un **Nom** (ex: "Tournée Lundi Matin").
4.  Sélectionnez le **Chauffeur** (par défaut vous-même).
5.  Définissez la **Date & Heure de Départ** (Crucial pour des estimations précises).

### 2. Ajouter des Tâches
Vous avez deux façons d'ajouter des tâches :
*   **Ajouter une ligne** : Sélectionnez ou créez manuellement des tâches dans la liste.
*   **Ajouter Tâches Non Assignées** (Recommandé) : Cliquez sur le bouton pour ouvrir un assistant affichant uniquement les tâches qui ne sont pas encore sur une route. Cochez plusieurs tâches et confirmez.

### 3. Optimiser la Route
1.  Une fois les tâches ajoutées, cliquez sur le bouton **Optimize Route** (Optimiser la Route) dans l'en-tête.
2.  Le système va :
    *   Valider que toutes les adresses ont des coordonnées GPS.
    *   Réorganiser les tâches pour trouver le chemin le plus court depuis l'adresse de départ de l'utilisateur.
    *   Calculer les temps de trajet entre chaque arrêt.
    *   Mettre à jour la **Séquence de Visite**, l'**Heure d'Arrivée Estimée**, et l'**Heure de Retour**.

### 4. Navigation (Mobile)
1.  Ouvrez la feuille de Route optimisée sur un mobile.
2.  Cliquez sur le bouton **Open in Google Maps**.
3.  Cela ouvre l'application Google Maps avec l'itinéraire complet pré-chargé (Départ -> Tâche 1 -> Tâche 2... -> Retour).

## Notes Techniques
*   **Algorithme** : Plus Proche Voisin (Nearest Neighbor / Simplified TSP).
*   **Distance** : Calculée via la formule de Haversine (Distance à vol d'oiseau sur sphère).
*   **Vitesse** : Suppose une vitesse moyenne de 50 km/h pour les estimations de durée.
