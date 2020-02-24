// Function for drawing graph of heart rate data in real time
function drawWaves(valueArray, canvas, scale, xScale=30, adjust=0) {


  requestAnimationFrame(() => {
    canvas.width = parseInt(getComputedStyle(canvas).width.slice(0, -2)) * devicePixelRatio;
    canvas.height = parseInt(getComputedStyle(canvas).height.slice(0, -2)) * devicePixelRatio;

    var context = canvas.getContext('2d');
    var margin = 2;
    var max = Math.max(0, Math.round(canvas.width / xScale));
    var offset = valueArray.length - max;
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.strokeStyle = '#00796B';

    context.beginPath();
    context.lineWidth = 3;
    context.lineJoin = 'round';
    // context.shadowBlur = '1';
    // context.shadowColor = '#333';
    // context.shadowOffsetY = '1';
    for (var i = 0; i < Math.max(valueArray.length, max); i++) {
      // var lineHeight = Math.round(valueArray[i] * canvas.height / scale);
      var lineHeight = Math.round(valueArray[i + offset] * canvas.height / scale);
      if (i === 0) {
        context.moveTo(xScale * i, canvas.height - lineHeight);
      } else {
        context.lineTo(adjust + xScale * i, canvas.height - lineHeight);
      }
      context.stroke();
    }
  });
}

window.onresize = drawWaves;

document.addEventListener("visibilitychange", () => {
  if (!document.hidden) {
    drawWaves();
  }
});


