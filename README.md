# Face Recognition API with Flask and Dlib

## Description
Ce projet implémente une API Flask pour la reconnaissance faciale en utilisant Dlib et OpenCV. Il permet de comparer des visages capturés dans des vidéos avec une base de données d'images d'utilisateurs stockées sur un serveur Spring Boot.

L'API prend en charge l'authentification via Face ID en récupérant des images d'utilisateurs depuis une API Spring Boot et en les comparant aux visages détectés dans une vidéo soumise.

## Fonctionnalités
- Détection et reconnaissance faciale à partir de vidéos uploadées.
- Comparaison avec des images d'utilisateurs stockées sur un serveur Spring Boot.
- Authentification automatique des utilisateurs reconnus via un appel API.
- Gestion des fichiers uploadés et des images de référence.

## Prérequis
Avant d'exécuter le projet, assurez-vous d'avoir installé les dépendances suivantes :

### Logiciels requis :
- Python 3.7+
- Flask
- OpenCV
- Dlib
- Numpy
- Requests

### Installation des dépendances :
```sh
pip install flask flask-cors opencv-python dlib numpy requests
```

## Structure du Projet
```
.
├── pretrained_model/                 # Modèles pré-entraînés Dlib
│   ├── shape_predictor_68_face_landmarks.dat
│   ├── dlib_face_recognition_resnet_model_v1.dat
├── uploads/                          # Vidéos uploadées (créé automatiquement)
├── known_faces/                      # Images des utilisateurs connus (créé automatiquement)
├── app.py                            # Code principal de l'API Flask
├── README.md                         # Documentation du projet
```

## Configuration
Les URLs des services Spring Boot doivent être mises à jour dans `app.py` si nécessaire :
```python
SPRING_BOOT_URL = "http://localhost:1010/admin/user-images"
SPRING_BOOT_LOGIN_URL = "http://localhost:1010/auth/login-faceid"
```

## Utilisation

### Lancer l'API Flask
```sh
python app.py
```
Par défaut, l'API tourne sur le port `5000`.

### Endpoints

#### 1. **Upload et reconnaissance faciale**
- **URL :** `/upload`
- **Méthode :** `POST`
- **Paramètre :** `video` (fichier vidéo en format `mp4` ou `avi`)
- **Retour :** JSON avec l'email de l'utilisateur reconnu et la réponse du service d'authentification.

**Exemple de requête avec `curl` :**
```sh
curl -X POST http://localhost:5000/upload -F "video=@chemin/vers/video.mp4"
```

### Résultat attendu
Si un visage est reconnu dans la vidéo :
```json
{
  "message": "User logged in successfully",
  "email": "utilisateur@example.com",
  "login_response": {...}
}
```
Si aucun visage n'est reconnu :
```json
{
  "message": "No recognized face found"
}
```

## Améliorations futures
- Ajout d'une interface web pour l'upload des vidéos.
- Optimisation du modèle de reconnaissance pour une meilleure précision.
- Support multi-utilisateur et gestion avancée des permissions.

## Auteurs
- **Mohamed Amine Hlel** - Développeur

## Licence
Ce projet est sous licence MIT.

