import "dotenv/config";
import { Bot } from "grammy";

const token = process.env.BOT_TOKEN;

console.log("TOKEN:", token ? "найден" : "НЕ НАЙДЕН");

if (!token) {
  throw new Error("BOT_TOKEN is not defined");
}

const bot = new Bot(token);

bot.command("start", async (ctx) => {
  console.log("Получена команда /start");

  await ctx.reply("👋 Бот работает!");
});

bot.catch((err) => {
  console.error("BOT ERROR:", err);
});

console.log("Запускаем бота...");

bot.start({
  onStart: () => {
    console.log("🤖 БОТ УСПЕШНО ЗАПУЩЕН");
  },
});