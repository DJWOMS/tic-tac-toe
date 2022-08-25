const modalSignup = document.getElementById("modal-signup")
const modalLogin = document.getElementById("modal-login")

document.querySelector(".signup").addEventListener('click', modalSignupOpen)
document.getElementsByClassName("close")[0].addEventListener('click', modalSignupClose)
document.querySelector(".form-signup").addEventListener('submit', sendFormSignup)

document.querySelector(".login").addEventListener('click', modalLoginOpen)
document.getElementsByClassName("close")[1].addEventListener('click', modalLoginClose)
document.querySelector(".form-login").addEventListener('submit', sendFormLogin)


function modalSignupOpen() {
    modalSignup.style.display = "block"
}

function modalSignupClose() {
    modalSignup.style.display = "none"
}

function modalLoginOpen() {
    modalLogin.style.display = "block"
}

function modalLoginClose() {
    modalLogin.style.display = "none"
}

window.onclick = function (event) {
    if (event.target === modalSignup) {
        modalSignup.style.display = "none"
    } else if (event.target === modalLogin) {
        modalLogin.style.display = "none"
    }
}

function sendFormSignup(event) {
    event.preventDefault()
    let data = {}
    let formData = new FormData(this)
    formData.forEach(function (value, key) {
        data[key] = value;
    });

    fetch('http://127.0.0.1:8000/signup', {
        method: 'POST',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (response.ok) {
                alert('Account created')
                modalSignupClose()
                return
            }
            return Promise.reject(response);
        })
        .catch(response => response.json().then(response => alert(response.error)))
}

function sendFormLogin(event) {
    event.preventDefault()
    let data = {}
    let formData = new FormData(this)
    formData.forEach(function (value, key) {
        data[key] = value;
    });

    fetch('http://127.0.0.1:8000/login', {
        method: 'POST',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (response.ok) {
                return response.json()
            }
            return Promise.reject(response);
        })
        .then(response => {
            sessionStorage.setItem('token', response.access_token)
            sessionStorage.setItem('username', response.username)
            modalLoginClose()
        })
        .catch(response => response.json().then(response => alert(response.error)))
}
