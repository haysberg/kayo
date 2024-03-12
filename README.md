# 🤖 KAY/O
![KAY/O from Valorant watering flowers](kayo.png)

*"If I'm powered down, restart me. You leave me for scrap, I'll kill you."*

KAY/O is a Discord bot that will send a message when a team / league is playing.

## Using the hosted version

If you want to invite KAY/O on your server, use [this link](https://discord.com/api/oauth2/authorize?client_id=1112803073094594601&permissions=18432&scope=bot).

## Roadmap

- [ ] Adding a dynamic `/help` command
- [ ] Responding to alerts with match results (marked as spoiler)
- [ ] Subscribing to leagues (*e.g* following VCT EMEA)
- [ ] A very simple website to explain what the bot does
- [ ] Filling up the `referential.json`file with more links to watch matches

## Deployment

Here is a `docker-compose` file for deploying KAY/O yourself.
Find the Riot API key in your browser when visiting the official Valorant pro schedule.

```yaml
version: '3'
services:
  kayo:
    container_name: kayo
    image: ghcr.io/haysberg/kayo:main
    restart: unless-stopped
    environment:
      - DISCORD_TOKEN=YOUR_TOKEN_HERE
      - VLR_GG_API=https://vlrggapi.vercel.app
      - DEPLOYED=PRODUCTION
    volumes:
      - /containers/kayo/data:/app/data:Z # NECESSARY TO SAVE YOUR ALERTS
```
