# Guide de la collecte des déchets (UI et JS)

## Dernière mise à jour : mai 2025

### 1. Modernisation de l’interface
- Le widget de collecte (sélecteur de ville, recherche de rue, affichage des résultats) a été entièrement modernisé.
- Utilisation de Tailwind CSS pour toute la présentation : cartes, champs, boutons, résultats.
- Les résultats sont affichés dans une carte blanche, arrondie, ombrée, avec sections colorées (ordures, verre) et listes à puces.

### 2. Génération dynamique du HTML (JS)
- Le code JS génère dynamiquement le HTML des résultats avec les classes Tailwind.
- Les icônes SVG ont été retirées du rendu dynamique pour simplifier le code (elles peuvent rester dans le HTML statique si besoin).
- Le CSS custom devient optionnel, tout peut être géré par Tailwind.

### 3. Conseils d’intégration
- Pour toute nouvelle fonctionnalité ou évolution, privilégier l’ajout de classes Tailwind directement dans le JS ou le HTML.
- Tester le rendu sur mobile et desktop pour garantir la responsivité.

### 4. Historique des modifications
- **Mai 2025** : refonte complète du widget collecte, harmonisation visuelle, suppression des SVG dynamiques, documentation mise à jour.

---

Pour toute question ou contribution, contacter l’équipe technique CCSA.
