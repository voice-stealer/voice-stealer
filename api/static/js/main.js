function saveToken(receivedToken) { localStorage.setItem('jwtToken', receivedToken); }
function getToken() { return localStorage.getItem('jwtToken'); }
function removeToken() { localStorage.removeItem('jwtToken'); }

const kInProgress = 'in_progress';
const kPending = 'pending';
const kFetchTimer = 20 * 1000;


function login(username, password) {
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data) {
            document.getElementById('message').innerText = data.message;
        }
    })
    .catch(error => {
        console.error('Error during login:', error);
        document.getElementById('message').innerText = 'An error occurred during login.';
    });
}

function logout() {
    console.log('Logging out...');
    fetch('/logout', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data) {
            document.getElementById('message').innerText = data.message;
            removeToken();
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error during logout:', error);
        document.getElementById('message').innerText = 'An error occurred during logout.';
    });
}


function postMessage(message, selected_audio, messageInput, chatContainer) {
    console.log(message, selected_audio);


    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-access-tokens': getToken()
        },
        body: JSON.stringify({ message, selected_audio })
    })
    .then(response => response.json())
    .then(data => {
        const userMessage = document.createElement('div');
        userMessage.className = 'message user';
        userMessage.textContent = message;
        chatContainer.appendChild(userMessage);
        messageInput.value = '';
        chatContainer.scrollTop = chatContainer.scrollHeight;


        checkTaskStatus(data.reqid);
    })
    .catch(error => console.error('Ошибка:', error));
}

function checkTaskStatus(taskId) {
    const chatContainer = document.getElementById('chat-container');
    let isProcessing = false;

    const intervalId = setInterval(() => {
        if (isProcessing) return;

        isProcessing = true;

        fetch(`/result/${taskId}`)
            .then(response => {
                const contentType = response.headers.get('content-type');

                if (contentType && contentType.includes("application/json")) {
                    return response.json().then(data => {
                        if (data.status !== kInProgress && data.status !== kPending) {
                            console.log(data);
                            clearInterval(intervalId);
                            console.log('Error in server');
                        }
                        isProcessing = false;
                    }).catch(() => isProcessing = false);
                } else if (contentType && contentType.includes("audio")) {
                    clearInterval(intervalId);
                    return response.blob().then(blob => {
                        sendAudio(chatContainer, blob);
                        isProcessing = false;
                    }).catch(() => isProcessing = false);
                } else {
                    return response.text().finally(() => {
                        isProcessing = false;
                    });
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                isProcessing = false;
            });
    }, kFetchTimer);
}

function sendAudio(chatContainer, audioBlob) {
    const botMessage = document.createElement('div');
    botMessage.className = 'message bot';


    const audioPlayer = document.createElement('audio');
    audioPlayer.controls = true;
    audioPlayer.src = URL.createObjectURL(audioBlob);
    botMessage.appendChild(audioPlayer);

    chatContainer.appendChild(botMessage);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}


function uploadFile() {
    const fileInput = document.getElementById('file');

    if (fileInput.files.length === 0) {
        alert('Please select a file to upload.');
        return false;
    }
    const file = fileInput.files[0];
    if (!file) {
        alert('Select a file to upload.');
        return false;
    }
    if (file.type !== 'audio/wav') {
        alert('Please select a valid WAV file.');
        return false;
    }
    if (file.size > 500 * 1024 * 1024) {
        alert('Please select a valid WAV file that is less than 500MB.');
        return false;
    }


    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload/wav', {
        method: 'POST',
        headers: {
            'x-access-tokens': getToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(JSON.stringify(data));

        // add to list audio-select
        const audioSelect = document.getElementById('audio-select');
        audioSelect.appendChild(document.createElement('option'));
        audioSelect.lastChild.textContent = file.name;
        return true;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error uploading file.');
        return false;
    });
}

// function retrieveAudio() {
//     const filename = document.getElementById('audioFilename').value;

//     fetch(`/get/wav/${filename}`, {
//         method: 'GET',
//         headers: {
//             'x-access-tokens': getToken()
//         }
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error('Audio not found or another error occurred');
//         }
//         return response.blob();
//     })
//     .then(blob => {
//         const audioURL = URL.createObjectURL(blob);

//         // Обновление источника элемента audio
//         const audioSource = document.getElementById('audioSource');
//         audioSource.src = audioURL;

//         const audioPlayer = document.getElementById('audioPlayer');
//         audioPlayer.load();  // Перезагрузить/завершить загрузку аудио

//         // "Провидим" элементы управления аудио и ссылку на скачивание
//         const audioControls = document.getElementById('audioControls');
//         audioControls.style.display = 'block';

//         // Настройка ссылки для скачивания
//         const downloadLink = document.getElementById('downloadLink');
//         downloadLink.href = audioURL;
//         downloadLink.download = filename;
//     })
//     .catch(error => {
//         console.error('Error:', error);
//         alert('Error retrieving the audio file.');
//     });
// }
