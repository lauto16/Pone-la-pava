const modal_create_room = document.getElementById('modal-create-room')
const button_create_room = document.getElementById('create-room-button')
const button_cancel_room = document.getElementById('cancel-room-modal')
const button_close_form = document.getElementById('close-modal')
const range_form = document.getElementById('input-people-amount');
const label_range_form = document.getElementById('label-range-form');
const create_room_button_modal = document.getElementById('create-room-modal')


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


async function errorHandler(error) {
    const div_errores = document.getElementById("div-errores")
    const p_errores = document.getElementById("p-errores")

    if (error) {

        div_errores.setAttribute('style', 'display:inline-block')
        p_errores.setAttribute('style', 'display:inline-block')
        p_errores.textContent = error

        await sleep(3000)

        $("#div-errores").fadeOut("slow", function () {
            div_errores.setAttribute('style', 'display:none')
            p_errores.setAttribute('style', 'display:none')
        });


    }
    else {
        div_errores.setAttribute('style', 'display:none')
        p_errores.setAttribute('style', 'display:none')
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


let form = document.getElementById('form-create-room')

let chatSocket;

function createRoomAndConnect(message) {

    if (chatSocket) {
        chatSocket.close();
    }

    chatSocket = new WebSocket(`ws://${window.location.host}/ws/socket-server/room/${message['room_code']}/`);

    chatSocket.onopen = function (event) {
        chatSocket.send(JSON.stringify(message));
    };


    chatSocket.onmessage = function (event) {
        let data = JSON.parse(event.data);

        if (data.type === 'chat') {
            redirectRoom(data)
        }

    };

    chatSocket.onclose = function (event) {
        console.log('WebSocket connection closed.');
    };

    chatSocket.onerror = function (error) {
        console.error('error del websocket')
    };
}


form.addEventListener('submit', function (e) {
    e.preventDefault();
    let message = {
        'user_name': e.target.user_name.value,
        'room_name': e.target.room_name.value,
        'room_code': e.target.room_code.value,
        'people_amount': e.target.people_amount.value
    };
    // Llamar a la función para crear la sala y establecer la conexión WebSocket
    createRoomAndConnect(message);
    form.reset();
});



button_close_form.addEventListener('click', function (e) {
    modal_create_room.style.display = 'none'
})



button_create_room.addEventListener('click', function () {
    modal_create_room.style.display = 'block'
})


button_cancel_room.addEventListener('click', function (e) {
    e.preventDefault()
    modal_create_room.style.display = 'none'
})





range_form.addEventListener('input', function () {
    label_range_form.textContent = `Integrantes: ${range_form.value}`;
});


label_range_form.textContent = `Integrantes: ${range_form.value}`;