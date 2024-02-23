const modal_create_room = document.getElementById('modal-create-room')
const modal_join_room = document.getElementById('modal-join-room')
const people_modal = document.getElementById('people-modal')
const room_code_strong = document.getElementById('room-code-strong')


function setSeeEvents(){
    let see_buttons = document.querySelectorAll('.see-room-code')
    see_buttons.forEach(button => {
       button.addEventListener('click', function(e){

        let id = 'room_code-' + e.target.id
        let input_code = document.getElementById(id)
        let img_see = document.getElementById(e.target.id)
        let src_img_notsee = document.getElementById('img-not-see-src').value
        let src_img_see = document.getElementById('img-see-src').value

        //case password is not visible
        if(input_code.type === 'password'){
            input_code.setAttribute('type', 'text')
            img_see.src = src_img_notsee
        }

        //case password is visible
        else if(input_code.type === 'text'){
            input_code.setAttribute('type', 'password')
            img_see.src = src_img_see
        }
        
       }) 
    });
}


function setJoinFormsEvents(){
    let join_forms = document.querySelectorAll('.form-join-created-room')

    join_forms.forEach(form => {
       form.addEventListener('submit', function(e){
            e.preventDefault()
            let room_code = e.target.id.substring(5)

            message = {
                room_code:room_code
            }
            joinRoom(message)
        });
    });
}


const form_logout = document.getElementById('form-logout')
form_logout.addEventListener('submit', function (e) {

    e.preventDefault()
    logout()

})

const form_join = document.getElementById('form-join-room')
form_join.addEventListener('submit', function (e) {

    e.preventDefault()

    let room_code = document.getElementById('input-room-code').value

    let message = {
        room_code: room_code
    }

    joinRoom(message)
    form_join.reset();
})


const form_create = document.getElementById('form-create-room')
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


const button_close_create = document.getElementById('close-modal-create')
button_close_create.addEventListener('click', function (e) {
    modal_create_room.style.display = 'none'
    room_code_strong.textContent = ""
})


const close_people_modal = document.getElementById('close-people-modal')
close_people_modal.addEventListener('click', function(e){
    people_modal.style.display = "none"
})

const button_close_join = document.getElementById('close-modal-join')
button_close_join.addEventListener('click', function (e) {
    modal_join_room.style.display = 'none'
})


const join_room_button = document.getElementById('join-room-button')
join_room_button.addEventListener('click', function (e) {
    modal_join_room.style.display = 'block'
})


const button_create_room = document.getElementById('create-room-button')
button_create_room.addEventListener('click', function () {
    modal_create_room.style.display = 'block'
})


const button_cancel_create = document.getElementById('cancel-create-modal')
button_cancel_create.addEventListener('click', function (e) {
    e.preventDefault()
    modal_create_room.style.display = 'none'
    room_code_strong.textContent = ""
})


const button_cancel_join = document.getElementById('cancel-join-modal')
button_cancel_join.addEventListener('click', function (e) {
    e.preventDefault()
    modal_join_room.style.display = 'none'
})


const range_form = document.getElementById('input-people-amount');
range_form.addEventListener('input', function () {
    label_range_form.textContent = `Integrantes: ${range_form.value}`;
});


const label_range_form = document.getElementById('label-range-form');
label_range_form.textContent = `Integrantes: ${range_form.value}`;

