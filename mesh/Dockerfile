FROM node:21-slim

WORKDIR /app
RUN apt-get update && apt-get install -y curl

COPY package.json yarn.lock ./
RUN yarn install

COPY . .

CMD ["/bin/sh", "-c", "yarn run start"]

