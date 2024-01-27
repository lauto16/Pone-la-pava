const modal_create_room = document.getElementById('modal-create-room')
const modal_join_room = document.getElementById('modal-join-room')

const button_create_room = document.getElementById('create-room-button')
const button_cancel_create = document.getElementById('cancel-create-modal')
const button_cancel_join = document.getElementById('cancel-join-modal')
const button_close_create = document.getElementById('close-modal-create')
const button_close_join = document.getElementById('close-modal-join')
const create_room_button_modal = document.getElementById('create-room-modal')
const join_room_button = document.getElementById('join-room-button')
const button_close_connection = document.getElementById('button-close-connection')

const range_form = document.getElementById('input-people-amount');
const label_range_form = document.getElementById('label-range-form');

const form_create = document.getElementById('form-create-room')
const form_join = document.getElementById('form-join-room')
const form_send_message = document.getElementById('form-send-message')


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


function redirectRoom(data) {

    let requestOptions = {

        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": getCookie('csrftoken'),
        },
        body: JSON.stringify(data)
    };

    fetch('./', requestOptions)

        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Network response was not ok.');
        })

        .then(data => {
            console.log(data);
        })

        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });

}


let joinSocket;


function joinRoom(message) {

    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');

    joinSocket = new WebSocket(`ws://localhost:8000/ws/chat/join/${message['room_code']}/0`);

    joinSocket.onopen = function (event) {
        console.log('connection opened(join)');
    }

    joinSocket.onclose = function (event) {
        console.log('WebSocket connection closed.');
    }

    joinSocket.onmessage = function (event) {
        const message = JSON.parse(event.data);
        console.log(message)
        const li = document.createElement('li');
        li.textContent = message.message;
        chatMessages.appendChild(li);
    }


    form_send_message.addEventListener('submit', function (event) {

        event.preventDefault();
        const message = messageInput.value;

        console.log("mensaje: ", message, " enviado!")

        joinSocket.send(JSON.stringify({ type: 'chat_message', message: message }));
        form_send_message.reset()
    })
}


let createSocket;


function createRoom(message) {
    createSocket = new WebSocket(`ws://localhost:8000/ws/chat/create/${message['room_name']}/${message['people_amount']}`);

    createSocket.onopen = function (event) {
        console.log('connection opened(create)')
    }

}


form_join.addEventListener('submit', function (e) {

    e.preventDefault()

    let room_code = document.getElementById('input-room-code').value

    let message = {
        room_code: room_code
    }

    try {
        joinSocket.close()
    } catch (error) {
        //
    }

    joinRoom(message)
    form_join.reset();
})


form_create.addEventListener('submit', function (e) {

    e.preventDefault();

    let room_name = document.getElementById('input-room-name').value
    let people_amount = document.getElementById('input-people-amount').value

    let message = {
        room_name: room_name,
        people_amount: people_amount
    };

    createRoom(message);
    form_create.reset();

})


button_close_create.addEventListener('click', function (e) {
    modal_create_room.style.display = 'none'
})


button_close_join.addEventListener('click', function (e) {
    modal_join_room.style.display = 'none'
})


join_room_button.addEventListener('click', function (e) {
    modal_join_room.style.display = 'block'
})


button_create_room.addEventListener('click', function () {
    modal_create_room.style.display = 'block'
})


button_cancel_create.addEventListener('click', function (e) {
    e.preventDefault()
    modal_create_room.style.display = 'none'
})


button_cancel_join.addEventListener('click', function (e) {
    e.preventDefault()
    modal_join_room.style.display = 'none'
})


button_close_connection.addEventListener('click', function () {
    let message = ""
    try {
        joinSocket.send(JSON.stringify({ type: 'delete_socket', message: message }));
    } catch (error) {
    }
})


range_form.addEventListener('input', function () {
    label_range_form.textContent = `Integrantes: ${range_form.value}`;
});


label_range_form.textContent = `Integrantes: ${range_form.value}`;