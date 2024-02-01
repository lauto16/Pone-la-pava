// the following 3 elements are the ones that displays 'none' when a chat modal is opened
const description = document.getElementById('description')
const container_rooms = document.getElementById('container-rooms')
const container_buttons_room = document.getElementById('container-buttons-room')

const chat_messages_list = document.getElementById('chat-messages-list')
const chat_modal = document.getElementById('chat-modal')


function changeBackgroundState(action, elements_list){

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
    const room_name = document.getElementById('room-name')

    changeBackgroundState(
        action='erase',
        elements_list=[
            description,
            container_rooms,
            container_buttons_room
    ])

    chat_messages_list.innerHTML = ""

    room_messages = room_data['room_messages']
    
    Object.keys(room_messages).forEach(key => {

        message_dict = {
            username: room_messages[key][0],
            message: room_messages[key][1],
            isUser: room_messages[key][2],            
        }

        addMessage(message_dict)
      });
    
    room_name.textContent = room_data.room_name

    // set the event listener so when the room is delete, the room div gets removed
    setEventDelete(room_data.room_code)
}


function redirectRoom(room_data) {

    let requestOptions = {

        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": getCookie('csrftoken'),
        },
        // send 
        body: JSON.stringify({
            room_name: room_data.room_name,
            room_code: room_data.room_code
        })
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

    chat_messages_list.appendChild(messageDiv);

    chat_messages_list.scrollTo({
        top: chat_messages_list.scrollHeight,
        behavior: 'smooth'
      });
}


function joinRoom(message) {

    joinSocket = new WebSocket(`ws://localhost:8000/ws/chat/join/${message.room_code}/0`);

    joinSocket.onopen = function (event) {
        joinSocket.send(JSON.stringify({ type: 'redirect_room', message: 'redirect_room' }));
    }

    joinSocket.onmessage = function (event) {
        const message = JSON.parse(event.data);

        if (message.type == 'room_redirection'){
            redirectRoom(message)
        }
        
        else if(message.type == 'chat'){
            addMessage(message)
        }
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

    const form_send_message = document.getElementById('form-send-message')
    form_send_message.addEventListener('submit', function (event) {

        const messageInput = document.getElementById('message-input');

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


//the following event listeners needs to be here so it can use the defined websocket 
const button_close_connection = document.getElementById('button-close-connection')
button_close_connection.addEventListener('click', function(){
    try {
        message = ""
        joinSocket.send(JSON.stringify({ type: 'delete_socket', message: message }));
        
        changeBackgroundState(
            action='unerase',
            elements_list=[
                description,
                container_rooms,
                container_buttons_room
        ])

    } catch (error) {
        console.log(error)
    }
})


function setEventDelete(room_code){
    const button_delete_room = document.getElementById('button-delete-room')
    button_delete_room.addEventListener('click', function(e){
        message = ""
        joinSocket.send(JSON.stringify({ type: 'delete', message: message }));
        room_id = 'room_select_' + room_code
        document.getElementById(room_id).remove()
    })
}
