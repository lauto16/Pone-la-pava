const modal_create_room = document.getElementById('modal-create-room')
const button_create_room = document.getElementById('create-room-button')
const button_cancel_room = document.getElementById('cancel-room-modal')
const button_close_form = document.getElementById('close-modal')
const range_form = document.getElementById('input-people-amount');
const label_range_form = document.getElementById('label-range-form');


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