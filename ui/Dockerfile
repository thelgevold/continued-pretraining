FROM node:22-alpine

WORKDIR /app

COPY ui/package*.json ./
RUN npm install

COPY ui ./

EXPOSE 4200

CMD ["npm", "start", "--", "--host", "0.0.0.0", "--poll", "1000"]
