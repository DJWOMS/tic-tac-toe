const modalSignup = document.getElementById("modal-signup")

document.querySelector(".signup").addEventListener('click', modalSignupOpen)
document.getElementsByClassName("close")[0].addEventListener('click', modalSignupClose)
document.querySelector(".form-signup").addEventListener('submit', sendFormSignup)

function modalSignupOpen() {
    modalSignup.style.display = "block"
}

function modalSignupClose() {
    modalSignup.style.display = "none"
}

window.onclick = function (event) {
    if (event.target === modalSignup) {
        modalSignup.style.display = "none"
    }
}

function sendFormSignup(event) {
    event.preventDefault()
    let data = {}
    let formData = new FormData(this)
    formData.forEach(function (value, key) {
        data[key] = value;
    });

    console.log('this', data)
    fetch('http://127.0.0.1:8000/signup', {
        method: 'POST',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(response => console.log(response))
        .catch(error => alert(error))
}
