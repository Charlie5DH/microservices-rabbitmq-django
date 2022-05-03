## RabbitMQ server setup

### RabbitMQ

RabbitMQ is a message broker, this is, an instance that accepts and forwards messages. You can think of it as a post office: when you put the mail that you want posting in a post box, you can be sure that the letter carrier will eventually deliver the mail to your recipient. In this analogy, RabbitMQ is a post box, a post office, and a letter carrier.

The major difference between RabbitMQ and the post office is that it doesn't deal with paper, instead it accepts, stores, and forwards binary blobs of data ‒ messages.
Note that the producer, consumer, and broker do not have to reside on the same host; indeed in most applications they don't. An application can be both a producer and consumer, too.

- **Producing** means nothing more than sending. A program that sends messages is a producer. The publisher stablishes a TCP connection with the RabbitMQ server, using the AMQP protocol (can use others also).
- **Consuming** means nothing more than receiving. A program that receives messages is a consumer. The consumer stablishes a TCP connection with the RabbitMQ server also. The server pushes messages to the consumer when they are ready.
- **The broker** is the middleman. It is responsible for routing messages between the producer and the consumer.
- **A queue** is the name for a post box which lives inside RabbitMQ. Although messages flow through RabbitMQ and your applications, they can only be stored inside a queue. A queue is only bound by the host's memory & disk limits, it's essentially a large message buffer. Many producers can send messages that go to one queue, and many consumers can try to receive data from one queue.
- Rabbit is designed to delete the data once processed (no persistency).
- RabbitMQ listen to port 5672.
- **A channel** is the logical connection between a consumer/publisher with the RabbitMQ server. This allows instead of having 3 consumers sharing 3 TCP connection, having 1 consumer with 3 channels in the same TCP connection (Multiplexing).

With RabbitMQ, a producer writes to an exchange which pushes the events into queues on a single host for specific consumers. Consumers reading from a queue are competing consumers. The exchange is then responsible to filter data based on logic rules and write to queues. A set of consumer containers connect to a queue and remove events from the queues once completed. The consumers are competing consumers — whichever container completes the work first gets the next unit of work. Because RabbitMQ consumers are `competing consumers`, event processing can be completed out of order if one event takes more time to complete than the next one.

It’s possible to set up a consumer so it `doesn’t mark work as completed`. This is generally the preferred method for events when the consumer just needs to know something happened vs treating the event as a unit of work that needs to be processed at most once.
RabbitMQ traditionally stores events in memory which can be a limiting factor. There are certainly ways around this. Setting up RabbitMQ for replication and high availability is an added task.

## Queues (FIFO)

Queues are the main way to communicate between the producer and the consumer. Before a queue can be used it has to be declared. Declaring a queue will cause it to be created if it does not already exist (like `use db` in Mongo). The declaration will have no effect if the queue does already exist and its attributes are the same as those in the declaration. When the existing queue attributes are not the same as those in the declaration a channel-level exception with code `406 (PRECONDITION_FAILED)` will be raised. They have the following propierties:

- Durable: The queue will survive a server restart. In AMQP 0-9-1, queues can be declared as durable or transient. Metadata of a durable queue is stored on disk, while metadata of a transient queue is stored in memory when possible.
- Exclusive: Only the current connection can access the queue and the queue will be deleted when that connection closes.
- Auto-delete: The queue will be deleted when the last consumer disconnects.
- Name: The queue name. If the queue name is empty, the server will generate a unique name. The generated name will be returned to the client with queue declaration response. Queue names starting with "amq." are reserved for internal use by the broker. Attempts to declare a queue with a name that violates this rule will result in a channel-level exception with reply code `403 (ACCESS_REFUSED)`.
- Arguments: Additional parameters for the queue.

### Possible Queue Usage Examples

There are main event types; Queue events and Pub/Sub events:

- Queue events:
- - Producer has a new unit of work which must be processed (generally only once)
- - Consumer processes work, tells the queueing system and it’s removed from the queue.
- - Ingress Buffering: Receive an event, get it persisted as quickly as possible and send an acknowledgement back to the sender. This is great for microbursts of work. Consumers can process the events asynchronously

- Pub/Sub events:
- - Publisher emits potentially interesting events
- - Consumer(s) selectively listens to what it chooses as interesting

## What is AMQP 0-9-1

`AMQP 0-9-1 (Advanced Message Queuing Protocol)` is a messaging protocol that enables conforming client applications to communicate with conforming messaging middleware brokers.

#### Brokers and Their Role

Messaging brokers receive messages from publishers (applications that publish them, also known as producers) and route them to consumers (applications that process them). Since it is a network protocol, the publishers, consumers and the broker can all reside on different machines.

The AMQP 0-9-1 Model has the following view of the world:

- Messages are published to exchanges, which are often compared to post offices or mailboxes.
- Exchanges then distribute message copies to queues using rules called bindings.
- Then the broker either deliver messages to consumers subscribed to queues, or consumers fetch/pull messages from queues on demand.

<img src="../assets/AMQP.png">

When publishing a message, publishers may specify various message attributes `(message meta-data)`. Some of this `meta-data` may be used by the broker, however, `the rest of it is completely opaque to the broker` and is only used by applications that receive the message.
Networks are unreliable and applications may fail to process messages therefore the AMQP 0-9-1 model has a notion of message acknowledgements:

When a message is delivered to a consumer the consumer notifies the broker, either automatically or as soon as the application developer chooses to do so. When message acknowledgements are in use, a broker will only completely remove a message from a queue when it receives a notification for that message (or group of messages).

### Exchanges and Exchange Types

Exchanges are AMQP 0-9-1 entities where messages are sent to. Exchanges take a message and route it into zero or more queues. `The routing algorithm used depends on the exchange type and rules called bindings`. AMQP 0-9-1 brokers provide four exchange types:

- **Direct Exchange:** A direct exchange delivers messages to queues based on the message routing key. A direct exchange is ideal for the unicast routing of messages (although they can be used for multicast routing as well).

- **Topic Exchange:** Topic exchanges route messages to one or many queues `based on matching between a message routing key and the pattern that was used to bind a queue to an exchange`. The topic exchange type is often used to implement various publish/subscribe pattern variations. Topic exchanges are commonly used for the multicast routing of messages. Topic exchanges have a very broad set of use cases. Whenever a problem involves multiple consumers/applications that selectively choose which type of messages they want to receive, the use of topic exchanges should be considered.
- - Example uses:
- - - A message is published to a topic exchange with a routing key of `"*.info"`. This message will be delivered to all queues that have a binding with a pattern of `"*.info"`.
- - - Distributing data relevant to specific geographic location, for example, points of sale.
- - - News updates that involve categorization or tagging (for example, only for a particular sport or team)

- **Fanout Exchange:** A fanout exchange routes messages to all of the queues that are bound to it and the routing key is ignored. If N queues are bound to a fanout exchange, when a new message is published to that exchange a copy of the message is delivered to all N queues. Fanout exchanges are ideal for the broadcast routing of messages. Here are some use cases:
- Massively multi-player online (MMO) games can use it for leaderboard updates or other global events
- Sport news sites can use fanout exchanges for distributing score updates to mobile clients in near real-time
- Distributed systems can broadcast various state and configuration updates
- Group chats can distribute messages between participants using a fanout exchange (although AMQP does not have a built-in concept of presence, so XMPP may be a better choice).

- **Default Exchange:** The default exchange is used when no exchange is specified. The default exchange is a direct exchange with no name (empty string) pre-declared by the broker. It has one special property that makes it very useful for simple applications: every queue that is created is automatically bound to it with a routing key which is the same as the queue name. For example, when you declare a queue with the name of `"search-indexing-online"`, the AMQP 0-9-1 broker will bind it to the default exchange using `"search-indexing-online"` as the routing key (in this context sometimes referred to as the binding key). Therefore, `a message published to the default exchange with the routing key "search-indexing-online" will be routed to the queue "search-indexing-online"`. In other words, the default exchange makes it seem like it is possible to deliver messages directly to queues, even though that is not technically what is happening.

## RabbitMQ with Docker

We can find the RabbitMQ docker image in [here](https://hub.docker.com/_/rabbitmq). One of the important things to note about RabbitMQ is that it stores data based on what it calls the "Node Name", which defaults to the hostname. What this means for usage in Docker is that we should specify `-h/--hostname` explicitly for each daemon so that we don't get a random hostname and can keep track of our data:

`$ docker run -d --hostname my-rabbit --name some-rabbit rabbitmq:3`

`docker run --hostname my-rabbitmq --name my-rabbitmq -p 5672:5672 rabbitmq`

This will start a RabbitMQ container listening on the default port of `5672`. If you give that a minute, then do docker logs some-rabbit, you'll see in the output a block similar to:

```bash
===========INFO REPORT==== 6-Jul-2015::20:47:02 ==========
node           : rabbit@my-rabbit
home dir       : /var/lib/rabbitmq
config file(s) : /etc/rabbitmq/rabbitmq.config
cookie hash    : UoNOcDhfxW9uoZ92wh6BjA==
log            : tty
sasl log       : tty
database dir   : /var/lib/rabbitmq/mnesia/rabbit@my-rabbit
```

**Note** the `database dir` there, especially that it has my "Node Name" appended to the end for the file storage. This image makes all of `/var/lib/rabbitmq` a volume by default.

`messages` contains the producer and consumers in node and python. All communicate with the rabbitmq server running in the cintainer.

`messages/consumer_node/` contains the consumer in node.
`messages/producer_node/` contains the producer in node.

### RabbitMQ with Docker-Compose

This is a compose example for RabbitMQ. In this case, we are using the `rabbitmq` image from alpine with the `management` plugin enabled. This is usefull to access the rabbitmq management api. The default port for AMQP protocol is `5672`, however we are also using port `15672` for the management api (http). The management api is useful for monitoring and managing the rabbitmq server (go to localhost:15672 in your browser). We are also setting up some volumes to see the information in our computer and the logs and a username and password. The network configuration is usefull for when the application runs in the same network as the rabbitmq server, so if we setup the application in a container in a conteiner, we can assign the same network to the application and the rabbitmq server (in this case we are running the app outside the container, i.e, only the rabbitmq server is in a container).

```yml
version: "3.9"

services:
  rabbitmq:
    image: "rabbitmq:3.8-management-alpine"
    container_name: "rabbitmq_container"
    environment:
      - RABBITMQ_DEFAULT_USER=root
      - RABBITMQ_DEFAULT_PASS=root
      - RABBITMQ_USERNAME=admin
      - RABBITMQ_PASSWORD=admin
    ports:
      - 5672:5672
      - 15672:15672
    volumes:
      - ./docker-conf/rabbitmq/data/:/var/lib/rabbitmq/
      - ./docker-conf/rabbitmq/log/:/var/log/rabbitmq
    #networks:
    #  - rabbitmq_network
#networks:
#  rabbitmq_network:
#    driver: bridge
```

## Creating producer with Python using the Pika library

There are a number of clients for RabbitMQ in many different languages. We're going to use Pika 1.2.0, which is the Python client recommended by the RabbitMQ team. To install it you can use the pip package management tool:

`python -m pip install pika --upgrade`

The producer in python is in the `admin` folder in the consumers file.

## Setup

The `admin` folder contains the producer. The producer is activate (events are sent to a queue) by calling the `publish_message` function inside a `create_product` view, so every time a product is created, a message is sent to the queue with the product information. The message is then consumed for the service application. In the service app, the consumer must be activated by calling `python consumer.py`. This consumer is constantly listening for messages on the queue and will store the product information in its databse, with the corresponding information.

Navigate to the service folder and run the following commands (assuming the service is running outside a container, i.e, only rabbit is in a container):

```yml
RUN docker-compose -f docker-compose.yml up -d \
&& python manage.py runserver localhost:8001 \
&& python consumer.py
```

Then, go to admin app and run the following commands:

```yml
RUN docker-compose -f docker-compose.yml up -d \
&& python manage.py runserver localhost:8000 \
```

## How do containers communicate?

First, a quick overview! Although containers have a level of isolation from the environment around them, they often need to communicate with each other, and the outside world. Two containers can talk to each other in one of two ways, usually:

- `Communicating through networking`: Containers are designed to be isolated. But they can send and receive requests to other applications, using networking. For example: a web server container might expose a port, so that it can receive requests on port 80. Or an application container might make a connection to a database container.

- `Sharing files on disk`: Some applications communicate by reading and writing files. These kinds of applications can communicate by writing their files into a volume, which can also be shared with other containers. For example: a data processing application might write a file to a shared volume which contains customer data, which is then read by another application. Or, two identical containers might even share the same files.

### Communication between containers with networking

Most container-based applications talk to each other using networking. This basically means that an application running in one container will create a network connection to a port on another container.

Containers are ideal for applications or processes which expose some sort of network service. The most well-known examples of these kinds of applications are:

- Web servers - e.g. Nginx, Apache
- Backend applications and APIs - e.g. Node, Python, JBoss, Wildfly, Spring Boot
- Databases and data stores - e.g. MongoDB, PostgreSQL

With Docker, container-to-container communication is usually done using a virtual network. Docker creates virtual networks which let your containers talk to each other. In a network, a container has an IP address, and optionally a hostname.

You can create different types of networks depending on what you would like to do.

- The default bridge network, which allows simple container-to-container communication by IP address, and is created by default. A bridge network gives you simple communication between `containers on the same host`. When Docker starts up, it will create a default network called… bridge. 🤔 It should start automatically, without any configuration required by you. From that point onwards, all containers are added into to the bridge network, unless you say otherwise. In a bridge network, each container is assigned its own IP address. So containers can communicate with each other by IP.

For example, in this case, the `admin` service is running in the network `172.24.x.x` with `IP` address of `172.24.0.3` and its database is running in network `172.24.x.x` with `IP` address of `172.24.0.2`. In this case, the database and the service are on the same host, therefore we can adress the databse by the hostname. Now, service `service` is in network `172.27.x.x` with `IP` address of `172.27.0.3` and its database with IP address of `172.27.0.2`. Each service can communicate easily with their database, but they need to communicate with the rabbitmq server, which is in a different network.

- `user-defined` bridge network, which you create yourself, and allows your containers to communicate with each other, by using their container name as a hostname. To let Docker containers communicate with each other by name, you can create a user-defined bridge network. In a user-defined bridge network, you can be more explicit about who joins the network, and you get an added bonus: …containers can be addressed by their name or alias. When these containers are joined to the user-defined bridge network, they can address each other by this name.

**This means you don’t need to worry about keeping track of containers’ IP addresses, which can frequently change.**

### **TL;DR:**

- For containers to communicate with other, they need to be part of the same “network”.
- Docker creates a virtual network called bridge by default, and connects your containers to it.
- In the network, containers are assigned an IP address, which they can use to address each other.
- If you want more control (and you definitely do), you can create a user-defined bridge, which will give you the added benefit of hostnames for your containers too.

## Putting it all together

Until now, we built different services with their own databases in their own containers, using a single `docker-compose.yml` file for each one. We need all these services to run in the same network so that they can communicate with each other using the hostname, for this, we are creating a single `docker-compose.yml` file, which will create all the services in te same network, `admin app`, `admin app database`, `rabbitmq server`, `service app`, `service app database`. The consumer is running in a separate container since we need to start it manually (this is part of the **TODO** list). The ideal solution would be use celery, but this requires more research, so for now, is running in a container, `running after 30 seconds to give time to rabbitmq server to start`. This is `.yml` for the consumer:

```yml
queue:
  build:
    context: ./service
    dockerfile: Dockerfile
  container_name: ms_django_2_queue
  command: "python consumer.py"
  depends_on:
    - ms_django_2
    - ms_django_2_mysql
    - rabbitmq
  networks:
    - rabbitmq_network
```

**Inspect the `docker-compose.yml` file in the root to see the different services**

Finally, just run `docker-compose -f docker-compose.yml up -d --build` to start all the services. The firsts requests to create products. if they happen to fast, may not be consumed because it will probably be sleeping.

**TODO**:

- Adding a check in the producer to see if is possible to send the event to the queue.
- Better automation of the consumer
- Add celery to the consumer
