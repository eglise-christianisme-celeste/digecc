# Module de recensement des paroisses — Bénin

## Production

`scripts/deploy.sh` (lancé par le CD sur `main`) sauvegarde la base, reconstruit le portail et redémarre
`personal` et `portal`. Le proxy partagé `ecc-shield` (CST, DIGECC, SEME), ses certificats et leur
renouvellement appartiennent à `ecc-infrastructure` (projet Compose `ecc-edge`) : un déploiement de DIGECC
ne les touche plus. Le réseau `ecc2026_ecc_network` et les volumes `ecc2026_*` gardent leur nom grâce à
`name: ecc2026` ; ne jamais renommer le projet Compose sans migrer ces ressources.
