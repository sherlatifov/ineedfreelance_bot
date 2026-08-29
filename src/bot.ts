import "dotenv/config";

import express from "express";
import { Bot, webhookCallback } from "grammy";

const token = process.env.BOT_TOKEN;

if (!token) {
  throw new Error("BOT_TOKEN is not defined");
}

const bot = new Bot(token);

bot.command("start", async (ctx) => {
  console.log("Получена команда /start");

  await ctx.reply(
    "👋 Бот работает!\n\n" +
    "Добро пожаловать в FreelanceHub."
  );
});

bot.command("test", async (ctx) => {
  await ctx.reply("✅ Связь с сервером работает!");
});

bot.catch((err) => {
  console.error("BOT ERROR:", err);
});

const app = express();

app.use(express.json());

app.get("/", (_req, res) => {
  res.send("FreelanceHub Bot is running 🚀");
});

app.post("/webhook", webhookCallback(bot, "express"));

const PORT = Number(process.env.PORT) || 10000;

app.listen(PORT, "0.0.0.0", async () => {
  console.log(`🚀 Server started on port ${PORT}`);

  const webhookUrl = process.env.RENDER_EXTERNAL_URL;

  if (webhookUrl) {
    const url = `${webhookUrl}/webhook`;

    await bot.api.setWebhook(url);

    console.log(`🤖 Telegram webhook set: ${url}`);
  } else {
    console.log("⚠️ RENDER_EXTERNAL_URL not found");
  }
});