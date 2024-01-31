// the following 3 elements are the ones that displays 'none' when a chat modal is opened
const description = document.getElementById('description')
const container_rooms = document.getElementById('container-rooms')
const container_buttons_room = document.getElementById('container-buttons-room')

const rooms = document.getElementById('rooms')
const modal_join_room = document.getElementById('modal-join-room')
const chat_modal = document.getElementById('chat-modal')

const form_send_message = document.getElementById('form-send-message')

const room_name = document.getElementById('room-name')

const button_close_connection = document.getElementById('button-close-connection')
const button_delete_room = document.getElementById('button-delete-room')

function changeBackgroundState(action, elements_list){

    elements_list = [
        description,
        container_rooms, 
        container_buttons_room
    ]

    if (action == 'erase'){
        for (let i = 0; i < elements_list.length; i++) {
            const element = elements_list[i];
            element.style.display = 'none'        
        }
    
    }
    
    if (action == 'unerase'){
        for (let i = 0; i < elements_list.length; i++) {
            const element = elements_list[i];
            element.style.display = 'flex'        
        }
    
    }

    

}


function textShortener(element_class, x){

    const textElements = document.querySelectorAll(element_class)

    textElements.forEach(element => {
        var text = element.textContent || element.innerText;
        if (text.length > 10){
            element.textContent = text.substring(0, x) + "...";
        }
    });
}


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


async function errorHandler(error) {
    const div_errors = document.getElementById("div-errors")
    const p_errors = document.getElementById("p-errors")

    if (error) {

        div_errors.setAttribute('style', 'display:inline-block')
        p_errors.setAttribute('style', 'display:inline-block')
        p_errors.textContent = error

        await sleep(3000)

        $("#div-errors").fadeOut("slow", function () {
            div_errors.setAttribute('style', 'display:none')
            p_errors.setAttribute('style', 'display:none')
        });


    }
    else {
        div_errors.setAttribute('style', 'display:none')
        p_errors.setAttribute('style', 'display:none')
    }
}


function getCookie(name) {

    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function openRoom(room_data){
    modal_join_room.style.display = 'none'
    chat_modal.style.display = 'block'

    changeBackgroundState(
        action='erase',
        elements_list=[
            description,
            container_rooms,
            container_buttons_room
    ])

    
    room_name.textContent = room_data['room_name']
}


function redirectRoom(room_name) {

    let requestOptions = {

        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": getCookie('csrftoken'),
        },
        body: JSON.stringify(room_name)
    };

    fetch('./', requestOptions)

        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Network response was not ok.');
        })

        .then(data => {
            openRoom(room_data=data)
        })

        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });

}


let joinSocket;


function addMessage(message) {

    const chatMessages = document.getElementById('chat-messages-list');

    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message';

    const strongElement = document.createElement('strong');
    strongElement.textContent = message.username;
    strongElement.className = 'strong-username'

    const pElement = document.createElement('p');
    pElement.textContent = message.message;

    if (message.isUser === true){
        messageDiv.style.float = 'right'
    }

    else{
        messageDiv.style.float = 'left'
    }

    messageDiv.appendChild(strongElement);
    messageDiv.appendChild(pElement);

    chatMessages.appendChild(messageDiv);
}


function joinRoom(message) {

    const messageInput = document.getElementById('message-input');

    joinSocket = new WebSocket(`ws://localhost:8000/ws/chat/join/${message.room_code}/0`);

    joinSocket.onopen = function (event) {
        joinSocket.send(JSON.stringify({ type: 'redirect_room', message: 'redirect_room' }));
    }

    joinSocket.onclose = function(event){
        changeBackgroundState(
            action='unerase',
            elements_list=[
                description,
                container_rooms,
                container_buttons_room
        ])
        
        chat_modal.style.display = 'none'
    }

    joinSocket.onmessage = function (event) {
        const message = JSON.parse(event.data);

        if (message.type == 'room_redirection'){
            redirectRoom(message.room_name)
        }
        
        else if(message.type == 'chat'){
            addMessage(message)
        }
    }


    form_send_message.addEventListener('submit', function (event) {

        event.preventDefault();
        const message = messageInput.value;

        joinSocket.send(JSON.stringify({ type: 'chat_message', message: message }));
        form_send_message.reset()
    })
}


let createSocket;


function createRoom(message) {

    createSocket = new WebSocket(`ws://localhost:8000/ws/chat/create/${message.room_name}/${message.people_amount}`);

    createSocket.onmessage = function(event){
        const message = JSON.parse(event.data);
        if (message.type == 'room_created'){
            room_code_strong.textContent = message.room_code
            addRoom(message)
        }
    }

}


//this event listener needs to be here so it can use the defined websocket 
button_close_connection.addEventListener('click', function(){
    try {
        joinSocket.send(JSON.stringify({ type: 'delete_socket', message: message }));
        
        changeBackgroundState(
            action='unerase',
            elements_list=[
                description,
                container_rooms,
                container_buttons_room
        ])
        
        chat_modal.style.display = 'none'

        //AGREGAR PARA ELIMINAR LOS MENSAJES VIEJOS

    } catch (error) {
        console.log(error)
    }
})
button_delete_room.addEventListener('click', function(){
    message = ""

    joinSocket.send(JSON.stringify({ type: 'delete', message: message }));
        
})

