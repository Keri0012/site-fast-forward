# Synchro automatique Instagram → page News

Une fois en place, chaque nouveau post Instagram apparaît tout seul sur la page News, le lendemain matin au plus tard. Il est présenté comme une fiche de réalisation : photo, date, titre, texte et fiche technique. Ce texte est lisible par Google, contrairement aux anciens encadrés Instagram.

La mise en place ne se fait qu'une seule fois.

---

## Étape 1 : passer le compte Instagram en compte professionnel

Si ton compte est déjà « Entreprise » ou « Créateur », passe à l'étape 2.

Dans l'appli Instagram : **Paramètres → Type de compte et outils → Passer à un compte professionnel**. C'est gratuit et ça ne change rien pour tes abonnés.

## Étape 2 : obtenir le jeton d'accès Instagram (déjà fait ✅)

Pour mémoire, voici le chemin dans developers.facebook.com, sur l'app « site Fast Forward » :
**Cas d'utilisation → Personnaliser → API Instagram → API setup with Unified login**
1. Associer le portefeuille business Fast Forward.
2. Bloc **1. Configurez votre application** : **Créer une nouvelle configuration** (token utilisateur système, compte Instagram Fast Forward).
3. Bloc **2. Générez des tokens d'accès** : **Générer un token**.

Ce token commence par « EAA » et **n'expire jamais**. Si un jour tu le régénères, il suffira de remplacer le secret `IG_TOKEN` (étape 3).

## Étape 3 : enregistrer le jeton dans GitHub

Dans ton dépôt GitHub :

**Settings → Secrets and variables → Actions → New repository secret**
- Name : `IG_TOKEN`
- Secret : colle le jeton
- Clique sur **Add secret**

Le jeton reste caché : il n'apparaît ni sur le site ni dans le code. L'identifiant du compte Instagram (17841424357554228) est déjà renseigné dans la synchro. Il est public, pas besoin de le cacher.

## Étape 4 : rien à faire

Ton jeton n'expire pas, donc aucun renouvellement automatique n'est nécessaire.

## Étape 5 : envoyer les fichiers et lancer la première synchro

1. Envoie le contenu du zip dans le dépôt (Add file → Upload files, ou `git push`), **y compris le dossier caché `.github`**. Sur le site GitHub, le plus simple est de glisser tout le dossier d'un coup.
   - Sur Mac, les dossiers qui commencent par un point sont cachés dans le Finder. Appuie sur **Cmd + Maj + .** pour les afficher.
2. Va dans l'onglet **Actions**, puis **Synchro Instagram → page News**, et clique sur **Run workflow**.
3. Après environ 1 minute, la coche doit passer au vert. Ton site se met à jour 1 à 2 minutes plus tard.

Ensuite, la synchro tourne toute seule chaque matin.

Si l'onglet Actions affiche une erreur de permission au moment de « Publier les changements », va dans **Settings → Actions → General → Workflow permissions** et coche **Read and write permissions**.

---

## Ajouter les détails techniques d'une prestation

### Méthode simple : dans la légende Instagram

Ajoute un bloc « Fiche technique » à la fin de ta légende, avant les hashtags :

```
Livestream de la convention annuelle d'un grand groupe
Une journée de conférences diffusée en direct pour 1 500 collaborateurs.

Fiche technique
Caméras : 4 dont 1 PTZ
Régie : ATEM Constellation HD
Diffusion : Microsoft Teams
Public : 300 en salle, 1 200 en ligne

#livestream #captationvideo
```

Ou en version courte, sur une seule ligne :

```
Technique : 4 caméras · ATEM Constellation · Web Presenter · diffusion YouTube
```

Sur le site :
- la **1re ligne** de la légende devient le **titre** de la fiche ;
- le texte qui suit devient la description ;
- le bloc technique s'affiche dans un encadré ;
- les hashtags sont retirés.

**Conseil référencement :** écris une 1re ligne descriptive (« Captation d'une conférence hybride à Paris ») plutôt qu'un simple emoji ou « Super journée ! ».

### Méthode alternative : le fichier `data/details-projets.json`

C'est utile pour les **anciens posts**, ou pour ajouter des infos sans les montrer sur Instagram. Le mode d'emploi et un exemple sont dans le fichier. Le code d'un post se trouve dans son adresse : instagram.com/p/**CODE**/. Dès que tu modifies ce fichier sur GitHub, la page se régénère automatiquement.
