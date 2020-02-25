var fs = require('fs');
var osc = require('node-osc'),
    io = require('socket.io').listen(8081);

var oscServer, oscClient;

// Create stream to log data
var stream = fs.createWriteStream("data.txt", {flags:'a'});

io.on('connection', function (socket) {
  socket.on('config', function (obj) {
    console.log('config', obj);
    oscServer = new osc.Server(obj.server.port, obj.server.host);
    oscClient = new osc.Client(obj.client.host, obj.client.port);

    oscClient.send('/status', socket.id + ' connected');

    oscServer.on('message', function(msg, rinfo) {
      socket.emit('message', msg);
      console.log('sent OSC message to WS', msg, rinfo);
    });
  });
  socket.on('message', function (obj) {
    var toSend = obj.split(' ');
    oscClient.send(...toSend);
    console.log('sent WS message to OSC', toSend);

    // Write to file
    stream.write(toSend + "\n");
  });
  socket.on("disconnect", function () {
    oscServer.kill();
  })
});

