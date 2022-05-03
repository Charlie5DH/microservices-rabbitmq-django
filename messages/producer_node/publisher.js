import express from "express";
import bodyParser from "body-parser";
import cors from "cors";
import amqp from "amqplib";

const app = express();

app.use(bodyParser.json({ limit: "30mb", extended: true }));
app.use(bodyParser.urlencoded({ limit: "30mb", extended: true }));
app.use(cors());

app.listen(5000, () => {
  console.log("Server started on port 5000");
});

app.get("", (req, res) => {
  res.send(`<h3>Hello. This is a rabbitmq testing</h3>`);
});

app.enable("trust proxy");

const port = process.env.PORT || 5672;

const message = {
  number: 1,
  user: "admin",
  password: "admin",
  host: "localhost",
};
const message2 = {
  number: process.argv[2],
  user: "root",
  password: "root",
  host: "localhost",
  port: 5000,
};

connect();

async function connect(params) {
  try {
    // create a connection to the RabbitMQ server
    //`amqp://localhost:5672`
    const connection = await amqp
      .connect(`amqp://root:root@localhost:5672`)
      .catch((err) => {
        console.log(err);
      });
    // create a channel
    const channel = await connection.createChannel();
    // see if queue jobs exists
    const result = await channel.assertQueue("jobs");
    // if queue jobs exists, publish a message.
    channel.sendToQueue("jobs", Buffer.from(JSON.stringify(message2)));
    console.log("Message sent to queue jobs");
  } catch (error) {
    console.error(error);
  }
}
