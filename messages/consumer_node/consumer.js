import express from "express";
import bodyParser from "body-parser";
import cors from "cors";
import amqp from "amqplib";

const app = express();

app.use(bodyParser.json({ limit: "30mb", extended: true }));
app.use(bodyParser.urlencoded({ limit: "30mb", extended: true }));
app.use(cors());

app.listen(5001, () => {
  console.log("Server started on port 5001");
});

app.get("", (req, res) => {
  res.send(
    `<h3>Hello. This is a rabbitmq testing. This is the Consumer APP</h3>`
  );
});

app.enable("trust proxy");

const port = process.env.PORT || 5672;

connect();

async function connect(params) {
  try {
    // create a connection to the RabbitMQ server
    const connection = await amqp.connect(
      //`amqp://${params.user}:${params.password}@${params.host}:${port}`
      `amqp://root:root@localhost:5672`
    );
    // create a channel
    const channel = await connection.createChannel();
    // see if queue jobs exists
    const result = await channel.assertQueue("jobs");
    // in this case, we are consuming the queue jobs
    // the consumer will receive the message and print it to the console. We want to keep it alive

    channel.consume("jobs", (msg) => {
      console.log(JSON.parse(msg.content.toString()));
      //console.log(msg);
      // if we don't acknowledge the message, we will keep receiving it forever, i.e
      // the message won't be removed from the queue
      // let's say we just want to process number 7 for some reason:
      // "7" == 7 true,
      if (JSON.parse(msg.content.toString()).number == 8) {
        console.log(
          `Message ${msg.content.toString()} received and removed from queue jobs`
        );
        channel.ack(msg);
        // this means that the message will be removed from the queue
        // this is normlly done by the consumer, after the required message is stored or processed
      }
    });
  } catch (error) {
    console.error(error);
  }
}
