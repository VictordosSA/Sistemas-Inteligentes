const socket = io();
const video = document.getElementById('video');

// Ativa câmera traseira
navigator.mediaDevices.getUserMedia({
    video: { facingMode: "environment" }
})
.then(stream => {
    video.srcObject = stream;
})
.catch(err => console.error("Erro ao acessar câmera:", err));

// Captura frame do vídeo
function capturarFrame() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    return canvas.toDataURL('image/jpeg', 0.5);
}

// Envio inteligente (só envia se vídeo estiver ativo)
setInterval(() => {
    if (video.videoWidth > 0) {
        socket.emit("frame", capturarFrame());
    }
}, 500);

// Recebe resultado do servidor
socket.on("resultado", (data) => {
    document.getElementById('resultado').innerText = data.resultado;
    document.getElementById('regiao').innerText = data.regiao;
    document.getElementById('imagem').src = data.imagem;
});

// Atualiza dashboard em tempo real (se estiver na página)
socket.on("dashboard", (data) => {
    if (window.chart) {
        chart.data.labels = Object.keys(data);
        chart.data.datasets[0].data = Object.values(data);
        chart.update();
    }
});