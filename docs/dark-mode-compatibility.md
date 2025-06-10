# Compatibilité avec le Mode Nuit

## Introduction

Ce document détaille les modifications apportées au site web pour assurer la compatibilité avec le mode nuit (dark mode), améliorant ainsi l'accessibilité pour les utilisateurs sensibles à la luminosité.

## Implémentation du Mode Nuit

Le mode nuit est implémenté via Tailwind CSS avec la configuration `darkMode: 'class'`. Lorsque la classe `dark` est ajoutée à l'élément HTML racine, les styles du mode nuit sont appliqués à l'ensemble du site.

L'activation/désactivation du mode nuit est gérée par le fichier `static/js/accessibility.js` qui :
- Ajoute/supprime la classe `dark` à l'élément HTML
- Sauvegarde la préférence utilisateur dans le localStorage
- Permet à l'utilisateur de basculer entre les modes via un bouton dédié

## Pages Modifiées

### 1. Page des Élus (`home/templates/home/elus.html`)

Modifications apportées :
- Ajout des classes `dark:bg-gray-800` et `dark:bg-gray-900` pour les fonds
- Ajout des classes `dark:text-gray-200`, `dark:text-gray-300`, et `dark:text-gray-400` pour les textes
- Adaptation des ombres avec `dark:shadow-gray-900`
- Ajout de styles spécifiques pour les liens et boutons en mode nuit

Styles CSS ajoutés dans `static/css/elus.css` :
```css
/* Mode nuit pour les cartes des élus */
.dark .elu-role {
    color: #3b82f6; /* Couleur bleue plus claire pour le mode nuit */
}

.dark .elu-card:hover {
    box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
}

.dark .elu-card a {
    color: #60a5fa; /* Bleu clair pour les liens en mode nuit */
}

.dark .elu-card a svg {
    stroke: #60a5fa;
}
```

### 2. Page des Communes (`home/templates/home/commune.html`)

Modifications apportées :
- Ajout des classes `dark:bg-gray-800` pour les sections avec fond blanc
- Ajout des classes `dark:text-gray-200`, `dark:text-gray-300` pour les textes
- Adaptation des couleurs pour les icônes avec `dark:text-blue-400` et `dark:text-green-400`
- Modification des styles pour le bloc d'information avec `dark:bg-gray-700` et `dark:border-gray-600`
- Adaptation du bouton de téléchargement avec `dark:bg-blue-600` et `dark:hover:bg-blue-700`

### 3. Organigramme Interactif (`home/templates/home/equipe.html`)

Modifications apportées :
- Implémentation d'un système d'onglets avec styles adaptés au mode nuit
- Adaptation des couleurs de l'organigramme interactif pour le mode nuit

Styles CSS ajoutés dans `static/css/organigramme.css` :
```css
/* Dark mode */
.dark .org-box {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.dark .org-box.direction {
    background-color: #1d4ed8;
}

.dark .org-box.service {
    background-color: #2563eb;
}

.dark .org-box.sous-service {
    background-color: #3b82f6;
}

.dark .org-tooltip {
    background-color: #1e293b;
    color: #f1f5f9;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
}

.dark .org-tooltip-title {
    color: #60a5fa;
}

.dark .org-connector, .dark .org-horizontal-line {
    background-color: #64748b;
}
```

### 4. Nouvelles Pages de Services et Compétences

Toutes les nouvelles pages ajoutées au site (comptes-rendus, présentation, compétences, etc.) ont été développées avec une compatibilité complète avec le mode nuit, incluant :
- Fonds adaptés avec les classes `dark:bg-gray-800` et `dark:bg-gray-900`
- Textes lisibles avec les classes `dark:text-gray-200` et `dark:text-gray-300`
- Éléments interactifs (boutons, liens) avec des couleurs adaptées
- Images et graphiques avec des contrastes suffisants

## Bonnes Pratiques Appliquées

1. **Cohérence** : Utilisation cohérente des couleurs et des contrastes à travers les différentes pages
2. **Contraste** : Respect des ratios de contraste recommandés par les normes WCAG 2.1
3. **Préférences utilisateur** : Sauvegarde des préférences utilisateur dans le localStorage
4. **Isolation** : Modifications isolées aux pages spécifiques sans affecter le reste du site

## Prochaines Étapes Recommandées

1. Appliquer les mêmes modifications aux autres pages du site pour une expérience utilisateur cohérente
2. Ajouter un test automatisé pour vérifier la compatibilité du mode nuit sur toutes les pages
3. Considérer l'ajout d'une détection automatique des préférences système via `prefers-color-scheme`

## Références

- [Tailwind CSS Dark Mode](https://tailwindcss.com/docs/dark-mode)
- [WCAG 2.1 - Contraste](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [MDN Web Docs - prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)
