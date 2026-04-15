# Étape 1 : Build de l'application React
FROM node:20-alpine AS build

WORKDIR /app

# Copier package.json et installer les dépendances
COPY package.json package-lock.json ./
RUN npm install

# Copier le code source
COPY . .

# Construire l'application
RUN npm run build

# Étape 2 : Serveur de production
FROM node:20-alpine

WORKDIR /app

# Installer 'serve' pour servir les fichiers statiques
RUN npm install -g serve

# Copier le build depuis l'étape précédente
COPY --from=build /app/build ./build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
