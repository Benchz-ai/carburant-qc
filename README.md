# Carte du carburant — Québec

App web personnelle (PWA) : carte interactive des prix d'essence/super/diesel
au Québec, mise à jour automatiquement chaque jour.

## Ce que contient ce dossier

```
carburant-app/
├── fetch_stations.py        # télécharge et transforme les données du jour
├── .github/workflows/update.yml   # automatisation quotidienne (GitHub Actions)
└── docs/
    ├── index.html            # la carte (Leaflet)
    ├── manifest.json          # pour l'installer comme app sur iPhone
    ├── icon-180.png / 192 / 512  # icônes
    └── stations.json          # données du jour (regénéré chaque nuit)
```

## Déploiement (15 minutes, une seule fois)

1. **Créer un dépôt GitHub**
   Va sur github.com → New repository → nomme-le par ex. `carburant-qc`
   → coche "Public" (nécessaire pour GitHub Pages gratuit) → Create.

2. **Envoyer ces fichiers dans le dépôt**
   Le plus simple : sur la page du dépôt vide, clique sur
   "uploading an existing file" et glisse tout le contenu de ce dossier
   (en conservant la structure `.github/workflows/update.yml` et `docs/`).

   Si tu préfères en ligne de commande :
   ```bash
   cd carburant-app
   git init
   git add .
   git commit -m "Première version"
   git branch -M main
   git remote add origin https://github.com/TON-PSEUDO/carburant-qc.git
   git push -u origin main
   ```

3. **Activer GitHub Pages**
   Dans le dépôt : Settings → Pages → sous "Build and deployment",
   choisis Source = "Deploy from a branch", Branch = `main`, dossier = `/docs`
   → Save.
   Après ~1 minute, ton site est en ligne à :
   `https://TON-PSEUDO.github.io/carburant-qc/`

4. **Vérifier que l'automatisation quotidienne fonctionne**
   Onglet "Actions" du dépôt → clique sur le workflow
   "Mise à jour quotidienne des prix" → "Run workflow" (bouton à droite)
   pour le lancer manuellement une première fois. Il tourne ensuite tout
   seul chaque jour à 6h (heure du Québec) — modifiable dans
   `.github/workflows/update.yml` (ligne `cron`).

5. **Installer sur ton iPhone**
   Ouvre `https://TON-PSEUDO.github.io/carburant-qc/` dans **Safari**
   (important : pas Chrome, le "Ajouter à l'écran d'accueil" avec mode
   plein écran ne fonctionne bien que dans Safari sur iOS) → bouton
   Partager (carré avec flèche) → "Sur l'écran d'accueil" → Ajouter.

   Tu as maintenant une icône qui ouvre la carte en plein écran, sans
   barre d'adresse, comme une vraie app.

## Maintenance

- Rien à faire au quotidien : GitHub Actions s'occupe de tout.
- Si `regieessencequebec.ca` change son URL ou la structure de son
  fichier, le workflow échouera silencieusement (garde-fou : si moins de
  1000 stations sont trouvées, l'ancien fichier n'est pas écrasé). Va voir
  l'onglet "Actions" de temps en temps si tu remarques que les prix ne
  bougent plus.
- Pour changer l'heure de mise à jour, modifie la ligne `cron: "0 10 * * *"`
  dans `.github/workflows/update.yml` (format UTC).
