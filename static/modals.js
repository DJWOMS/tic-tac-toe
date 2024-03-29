const modalSignup = document.getElementById("modal-signup")
const modalLogin = document.getElementById("modal-login")
const modalTop = document.getElementById("modal-top")
const modalMyStat = document.getElementById("modal-myStat")

const btnLogout = document.querySelector(".logout")
const spanUsername = document.querySelector(".span-username")
const btnMyStat = document.querySelector(".btn-myStat")

btnLogout.addEventListener('click', logout)

document.querySelector(".signup").addEventListener('click', modalSignupOpen)
document.getElementsByClassName("close")[0].addEventListener('click', modalSignupClose)
document.querySelector(".form-signup").addEventListener('submit', sendFormSignup)

document.querySelector(".login").addEventListener('click', modalLoginOpen)
document.getElementsByClassName("close")[1].addEventListener('click', modalLoginClose)
document.querySelector(".form-login").addEventListener('submit', sendFormLogin)

document.querySelector(".btn-top").addEventListener('click', modalTopOpen)
document.querySelector(".close-top").addEventListener('click', modalTopClose)


btnMyStat.addEventListener('click', modalMyStatOpen)
document.querySelector(".close-myStat").addEventListener('click', modalMyStatClose)


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
function modalTopOpen() {
    modalTop.style.display = 'block'
}

function modalTopClose() {
    modalTop.style.display = "none"
}

function modalMyStatOpen() {
    modalMyStat.style.display = 'block'
    send({action: 'stat'})
}

function modalMyStatClose() {
    modalMyStat.style.display = "none"
}

function showLogout() {
    btnLogout.style.display = "block"
}

function hideLogout() {
    btnLogout.style.display = "none"
}

function showLoginSignup() {
    document.querySelector(".signup").style.display = "block"
    document.querySelector(".login").style.display = "block"
}

function hideLoginSignup() {
    document.querySelector(".signup").style.display = "none"
    document.querySelector(".login").style.display = "none"
}

function showUsername(username) {
    spanUsername.innerHTML = username
}

function hideUsername() {
    spanUsername.innerHTML = ''
}

function showBtnMyStat() {
    btnMyStat.style.display = "block"
}

function hideBtnMyStat() {
    btnMyStat.style.display = "none"
}

window.onclick = function (event) {
    switch (event.target) {
        case modalSignup:
            modalSignup.style.display = "none"
            break
        case modalLogin:
            modalLogin.style.display = "none"
            break
        case modalTop:
            modalTop.style.display = "none"
            break
        case modalMyStat:
            modalMyStat.style.display = "none"
            break
        default:
            break
    }
}

function sendFormSignup(event) {
    event.preventDefault()
    let data = {}
    let formData = new FormData(this)
    formData.forEach(function (value, key) {
        data[key] = value;
    });

    fetch(`http://${location.host}/signup`, {
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

    fetch(`http://${location.host}/login`, {
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
            showLogout()
            showBtnMyStat()
            hideLoginSignup()
            showUsername(response.username)
            closeWS()
            start()
            modalLoginClose()
        })
        .catch(response => response.json().then(response => alert(response.error)))
}

function logout() {
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('username')
    hideLogout()
    hideBtnMyStat()
    hideUsername()
    showLoginSignup()
    closeWS()
    start()
}
