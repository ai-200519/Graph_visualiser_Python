# Format d'importation des matrices d'adjacence

## Structure du fichier TXT

Le fichier doit contenir une matrice d'adjacence carrée où :
- Chaque ligne représente un sommet
- Chaque colonne représente une connexion vers un autre sommet
- Les valeurs représentent les poids des arêtes

## Format supporté

### Valeurs autorisées :
- `0` ou `0.0` : Pas de connexion
- Nombres positifs : Poids de l'arête
- `inf`, `infinity`, ou `∞` : Distance infinie (pas de chemin direct)

### Exemples :

#### Graphe non orienté simple (5 sommets)
```
0 2 0 1 0
2 0 3 0 0
0 3 0 4 5
1 0 4 0 6
0 0 5 6 0
```

#### Graphe orienté
```
0 2 0 1 0
0 0 3 0 0
0 0 0 4 5
0 0 0 0 6
0 0 0 0 0
```

#### Graphe avec distances infinies
```
0 2 inf 1 0
2 0 3 inf 0
inf 3 0 4 5
1 inf 4 0 6
0 0 5 6 0
```

## Règles importantes

1. **Matrice carrée** : Le nombre de lignes doit égaler le nombre de colonnes
2. **Encodage** : Le fichier doit être en UTF-8
3. **Séparateurs** : Les valeurs sont séparées par des espaces ou des tabulations
4. **Lignes vides** : Les lignes vides sont ignorées
5. **Détection automatique** : 
   - Si la matrice est symétrique → graphe non orienté
   - Si la matrice n'est pas symétrique → graphe orienté

## Utilisation

1. Ouvrez l'application Graph Visualizer
2. Cliquez sur "SHOW MATRICES"
3. Cliquez sur "Import TXT File"
4. Sélectionnez votre fichier .txt
5. Le graphe sera automatiquement créé et affiché

## Notes

- Les sommets sont automatiquement nommés 1, 2, 3, etc.
- Les positions des sommets sont automatiquement calculées
- Seuls les poids différents de 1 sont affichés sur les arêtes
- Les boucles (connexions d'un sommet vers lui-même) ne sont pas supportées pour l'instant 