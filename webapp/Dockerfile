# Stage 1 : build the app for production
FROM node:latest as build
WORKDIR /app
COPY . .
RUN npm install --save --force
RUN npm run build --prod
# Stage 2 : deploy the app
FROM nginx:alpine
COPY --from=build /app/dist/webapp /usr/share/nginx/html

