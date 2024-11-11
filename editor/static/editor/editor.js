const editor = document.getElementById('editor');
let socket;

function connectWebSocket() {
    socket = new WebSocket(
        'ws://' + window.location.host + '/ws/editor/' + documentId + '/'
    );

    socket.onopen = function(e) {
        console.log('WebSocket connected.');
    };

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'initial_content') {
            editor.innerText = data.content;
        } else if (data.type === 'update_content') {
            // Update editor content without triggering event
            editor.removeEventListener('input', handleInputEvent);
            editor.innerText = data.message;
            editor.addEventListener('input', handleInputEvent);
        }
    };

    socket.onclose = function(e) {
        console.error('WebSocket closed unexpectedly. Reconnecting...');
        setTimeout(connectWebSocket, 1000);
    };
}

function handleInputEvent(e) {
    const message = editor.innerText;
    socket.send(JSON.stringify({
        'message': message
    }));
}

editor.addEventListener('input', handleInputEvent);

connectWebSocket();