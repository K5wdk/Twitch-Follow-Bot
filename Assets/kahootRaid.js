const Kahoot = require("kahoot.js-latest");
const fs = require("fs");

const pin = process.argv[2];
const bot_count = 30;
const kahoots = [];

function makeid(length) {
  let result = '';
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

for (let i = 0; i < bot_count; i++) {
  kahoots[i] = new Kahoot();
  kahoots[i].join(pin, makeid(5)).then(() => {
    console.log(`Bot ${i + 1} joined!`);
  }).catch(err => {
    console.log(`Bot ${i + 1} failed: ${err.message}`);
  });

  kahoots[i].on("QuestionStart", (question) => {
    question.answer(Math.floor(Math.random() * question.quizQuestionAnswers[question.questionIndex]));
  });

  kahoots[i].on("Disconnect", (reason) => {
    console.log(`Bot ${i + 1} disconnected: ${reason}`);
  });
}
