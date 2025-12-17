FROM node:20-slim AS build
WORKDIR /usr/src/app
COPY package.json tsconfig*.json vite.config.ts ./
COPY src ./src
COPY index.html ./
RUN npm install && npm run build

FROM node:20-slim
WORKDIR /usr/src/app
COPY --from=build /usr/src/app/dist ./dist
RUN npm install -g serve
EXPOSE 4173
CMD ["serve", "-s", "dist", "-l", "4173"]
