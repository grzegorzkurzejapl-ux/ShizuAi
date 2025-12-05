# ShizuAi

Assistant Python en ligne de commande, capable de répondre à tes questions et d'utiliser DuckDuckGo pour un résumé rapide si Internet est disponible.
Il fonctionne intégralement en console : tu peux le lancer directement ou générer un exécutable `.exe` avec PyInstaller.
L'affichage utilise des nuances de gris et de rouge en dégradé dans le terminal (désactivables via `--no-color`).

## Installation rapide
1. (Optionnel) crée un environnement virtuel Python.
2. Installe les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation
- Session interactive (par défaut, la recherche web est activée, couleurs gris/rouge actives) :
  ```bash
  python app.py
  ```
- Poser une question directement :
  ```bash
  python app.py "Quelle est la capitale du Japon ?"
  ```
- Forcer le mode hors ligne :
  ```bash
  python app.py --no-web "Présente-toi"
  ```
- Désactiver les couleurs gris/rouge (utile pour certains terminaux ou la génération `.exe`) :
  ```bash
  python app.py --no-color "Explique le rôle de Python"
  ```
- Ajuster le délai réseau (par défaut 4s) pour la récupération web :
  ```bash
  python app.py --timeout 6.5 "Résume la mission de l'ESA"
  ```
  (une valeur minimale de 0,1s est imposée pour éviter les conflits de paramètres)

## Générer un exécutable Windows (.exe)
1. Installe PyInstaller :
   ```bash
   pip install pyinstaller
   ```
2. Crée l'exécutable :
   ```bash
   pyinstaller --onefile --name ShizuAi app.py
   ```
3. L'exécutable sera disponible dans le dossier `dist/` (par exemple `dist/ShizuAi.exe`).

## Notes
- Sans accès Internet, ShizuAi fonctionne en mode hors ligne avec des réponses prêtes à l'emploi.
- La recherche web repose sur l'API publique de DuckDuckGo et ne nécessite pas de clé API.
