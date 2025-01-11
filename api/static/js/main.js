function saveToken(receivedToken) { localStorage.setItem('jwtToken', receivedToken); }
function getToken() { return localStorage.getItem('jwtToken'); }
function removeToken() { localStorage.removeItem('jwtToken'); }

const kInProgress = 'in_progress';
const kPending = 'pending';
const kDone = 'done';
const kFailed = 'failed';
const kFetchTimer = 5 * 1000;


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
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error during login:', error);
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
    });
}

function register(username, password1, password2) {
    if (password1 !== password2) {
        alert('Пароли не совпадают');
        return;
    }

    fetch('/registration', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password1, password2 })
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
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error during registration:', error);
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


        startLoading("Голос синтезируется...");
        checkTaskStatus(data.reqid);
    })
    .catch(error => console.error('Ошибка:', error));
}

function checkTaskStatus(taskId) {
    const chatContainer = document.getElementById('chat-container');
    let isProcessing = false;

    const intervalId = setInterval(() => {
        if (isProcessing) {
            stopLoading();
            return;
        };

        isProcessing = true;

        fetch(`/result/${taskId}`)
            .then(response => {
                const contentType = response.headers.get('content-type');

                if (contentType && contentType.includes("application/json")) {
                    return response.json().then(data => {
                        if (data.status !== kInProgress && data.status !== kPending) {
                            alert("Во время выполнения запросы произошла ошибка. Попробуйте ещё раз");
                            console.error(data);
                            clearInterval(intervalId);
                        }
                        isProcessing = false;
                    }).catch(() => isProcessing = false);
                } else if (contentType && contentType.includes("audio")) {
                    stopLoading();
                    clearInterval(intervalId);
                    return response.blob().then(blob => {
                        sendAudio(chatContainer, blob, taskId);
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

// function sendAudio(chatContainer, audioBlob) {
//     const botMessage = document.createElement('div');
//     botMessage.className = 'message bot';


//     const audioPlayer = document.createElement('audio');
//     audioPlayer.controls = true;
//     audioPlayer.src = URL.createObjectURL(audioBlob);
//     botMessage.appendChild(audioPlayer);

//     chatContainer.appendChild(botMessage);
//     chatContainer.scrollTop = chatContainer.scrollHeight;
// }
function sendAudio(chatContainer, audioBlob, taskId) {
    const botMessage = document.createElement('div');
    botMessage.className = 'message bot';

    const audioPlayer = document.createElement('audio');
    audioPlayer.controls = true;
    audioPlayer.src = URL.createObjectURL(audioBlob);
    botMessage.appendChild(audioPlayer);

    // Создаем контейнер для кнопок лайка и дизлайка
    const feedbackContainer = document.createElement('div');
    feedbackContainer.className = 'feedback';
    feedbackContainer.id = 'feedback';
    feedbackContainer.name = `${taskId}`;

    // Создаем кнопку лайка
    const likeButton = document.createElement('button');
    likeButton.className = 'like-button';
    likeButton.innerText = '👍';
    likeButton.onclick = () => {
        likeButton.classList.add('selected');
        dislikeButton.disabled = true;
        sendReaction(true);
    };
    feedbackContainer.appendChild(likeButton);

    // Создаем кнопку дизлайка
    const dislikeButton = document.createElement('button');
    dislikeButton.className = 'dislike-button';
    dislikeButton.innerText = '👎';
    dislikeButton.onclick = () => {
        dislikeButton.classList.add('selected');
        likeButton.disabled = true;
        sendReaction(false);
    };
    feedbackContainer.appendChild(dislikeButton);

    botMessage.appendChild(feedbackContainer);

    chatContainer.appendChild(botMessage);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function sendReaction(like) {
    const taskId = document.getElementById('feedback').name;
    fetch('/feedback', {
        method: 'POST',
        headers: {
            'x-access-tokens': getToken(),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({like, taskId})
    })
    .then(response => response.json())
    .then(data => {
        console.log(JSON.stringify(data));
    })
    .catch(error => {
        console.error('Error:', error);
    });
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
    const acceptedMimeTypes = ['audio/wav', 'audio/x-wav', 'audio/wave', 'audio/vnd.wave'];
    if (!acceptedMimeTypes.includes(file.type)) {
        alert('Please select a valid WAV file.');
        return false;
    }
    if (file.size > 500 * 1024 * 1024) {
        alert('Please select a valid WAV file that is less than 500MB.');
        return false;
    }
    startLoading("Подождите, файл загружается...");


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
        stopLoading();
        alert('Файл успешно загружен.');
        return true;
    })
    .catch(error => {
        stopLoading();
        console.error('Error:', error);
        alert('Ошибка загрузки файла.');
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



function startLoading(msg) {
    const load = document.getElementById('loadingOverlay');
    load.getElementsByClassName('loading-text')[0].textContent = msg;
    load.style.display = 'flex'
}

function stopLoading() {
    const load = document.getElementById('loadingOverlay');
    load.style.display = 'none';
    load.getElementsByClassName('loading-text')[0].textContent = "";
}
