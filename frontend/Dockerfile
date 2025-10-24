FROM guergeiro/pnpm:22-10

WORKDIR /app

COPY package*.json pnpm-lock.yaml* ./

RUN pnpm install

COPY . .

EXPOSE 3000

CMD ["pnpm", "start"]