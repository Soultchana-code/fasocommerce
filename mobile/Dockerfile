# Utilisation d'une image légère avec Flutter installé
FROM cirrusci/flutter:stable

WORKDIR /app

# Copie des fichiers de configuration
COPY pubspec.yaml .

# Installation des dépendances
RUN flutter pub get

# Copie du reste du code
COPY . .

# On garde le conteneur ouvert pour le développement
CMD ["tail", "-f", "/dev/null"]
