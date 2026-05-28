<!-- Merci de votre contribution. Remplir les sections ci-dessous facilite la revue. -->

## Résumé

<!-- Décrire le changement en 1-3 phrases. Pourquoi est-il nécessaire ? -->

## Type de changement

- [ ] 🐛 Bug fix (changement non cassant qui résout un bug)
- [ ] ✨ Nouvelle fonctionnalité (changement non cassant qui ajoute du comportement)
- [ ] 🔄 Refactor (pas de changement comportemental)
- [ ] 📚 Documentation
- [ ] 🧪 Tests / CI
- [ ] 💥 Breaking change (changement qui casse l'API publique ; nécessite un bump majeur)

## Issues liées

<!-- Closes #N — utiliser ce format pour fermer automatiquement à la merge -->

Closes #

## Vérifications

- [ ] Les tests offline passent localement (`make test` ou `pytest -m "not integration"`)
- [ ] Le code passe `ruff check src tests` sans erreur
- [ ] Le code passe `ruff format --check src tests` sans erreur
- [ ] Le code passe `mypy src` (strict) sans erreur
- [ ] La couverture de test est maintenue ou améliorée
- [ ] La documentation pertinente est mise à jour (README, CHANGELOG, docstrings)
- [ ] Pour un breaking change : un shim de rétro-compat est en place OU un avertissement explicite dans CHANGELOG.md

## Comment vérifier ce changement ?

<!-- Étapes pour reproduire manuellement le bug fixé / valider la nouvelle feature.
     Pour un refactor : décrire la stratégie de validation (caractérisation,
     comparaison avant/après, etc.). -->

```bash
# Ex:
pytest tests/test_legifrance_client.py -v
```

## Notes pour le reviewer

<!-- Optionnel : points à regarder en priorité, décisions de design,
     compromis assumés. -->
