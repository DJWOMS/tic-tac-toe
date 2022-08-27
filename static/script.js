let ws
let gameNumber
let iPlayer
let otherPlayer
let activeGame
let gameState

function start() {
    checkToken()
    let token = sessionStorage.getItem('token')
    let username = sessionStorage.getItem('username')

    gameNumber = 0
    iPlayer = {}
    otherPlayer = {}
    activeGame = false
    gameState = ["", "", "", "", "", "", "", "", ""]

    if (token && username) {
        showLogout()
        showBtnMyStat()
        hideLoginSignup()
        showUsername(username)

        ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`)
        wsFunctions()
        return
    }
    ws = new WebSocket('ws://localhost:8000/ws')
    wsFunctions()
}

function wsFunctions() {
    ws.onopen = function (event) {
        newUser()
    }

    ws.onmessage = function (event) {
        let data = JSON.parse(event.data)
        switch (data.action) {
            case 'new':
                gameList(data.games)
                break
            case 'create':
                createdGame(data.number, data.player)
                break
            case 'join':
                startGame(data.number, data.player, data.other_player, data.move)
                break
            case 'move':
                moveGame(data.is_active, data.cell, data.move, data.state, data.message)
                break
            case 'close':
                actionCloseGame(data.games)
                break
            case 'error':
                errorGame(data.message)
                break
            case 'online':
                onlineUsers(data.count)
                break
            case 'top':
                topUsers(data.top)
                break
            case 'stat':
                myStat(data.stat)
                break
            default:
                break
        }
    }
}


function send(data) {
    ws.send(JSON.stringify(data))
}


function newUser() {
    send({action: 'new'})
}


function createGame() {
    send({action: 'create'})
}


function createdGame(number, player) {
    iPlayer = player
    gameNumber = number
    changeGameStatusMessage('Waiting for another player...')
    newGame()
}


function joinGame(event) {
    let btn = event.target
    send({action: 'join', game: parseInt(btn.id)})
}


function startGame(number, player, other_player, move) {
    iPlayer = player
    otherPlayer = other_player
    activeGame = move
    gameNumber = number
    if (move) {
        changeGameStatusMessage(`Your turn. To you join the player ${otherPlayer.username} - ${otherPlayer.state}`)
    } else {
        changeGameStatusMessage(
            `Player turn ${otherPlayer.state}. 
            To you join the player ${otherPlayer.username} - ${otherPlayer.state}`
        )
    }
    newGame(move)
}


function moveGame(is_active, cellIndex, move, state, message) {
    let cellClicked = document.querySelector(`[data-cell-index="${cellIndex}"]`)
    changeGameStatusMessage(message)
    activeGame = move

    if (!activeGame || gameState[cellIndex] !== "") {
        return
    }

    cellClicked.innerHTML = state
    gameState[cellIndex] = state

    if (!is_active) {
        activeGame = is_active
    }
}


function gameList(games) {
    let gameList = document.getElementById('gameList')
    let ch = gameList.lastElementChild
    if (ch) {
        gameList.removeChild(ch)
    }
    let j = 0
    for (let i in games) {
        let gameList = document.getElementById('gameList')
        let li = document.createElement('li')
        let text = document.createTextNode(`${j + 1} `)
        let span = document.createElement('span')
        span.innerHTML = games[i].creator
        let btn = document.createElement('button')
        btn.id = `${i}`
        btn.className = 'btn-join'

        if (!games[i].isActive) {
            btn.addEventListener('click', joinGame)
            btn.innerHTML = 'Join'
        } else {
            btn.disabled = true
            btn.innerHTML = 'Close'
        }

        li.appendChild(text)
        li.appendChild(span)
        li.appendChild(btn)
        gameList.appendChild(li)
        j++
    }
}


function clickCell(event) {
    const cell = event.target
    const cellIndex = parseInt(cell.getAttribute('data-cell-index'))

    if (!activeGame || gameState[cellIndex] !== "") {
        return
    }

    gameState[cellIndex] = iPlayer.state
    cell.innerHTML = iPlayer.state

    activeGame = false
    send({action: 'move', number: gameNumber, 'cell': cellIndex})
}


function newGame() {
    document.getElementById('game').className = 'game-off container-game'
    document.getElementById('tic-tac-toe').className = 'game-on'
    let playerState = document.getElementById('player')
    playerState.className = 'game-on'
    playerState.innerHTML = `You are ${iPlayer.state}`
}


function resetGames() {
    document.getElementById('game').className = 'container-game'
    document.getElementById('tic-tac-toe').className = 'game-off'
    document.querySelectorAll('.cell').forEach(cell => cell.innerHTML = '')
    gameState = ["", "", "", "", "", "", "", "", ""]
    activeGame = false
    iPlayer = {}

    let state = document.getElementById('player')
    state.className = 'game-off'
    state.innerHTML = ''
}


function changeGameStatusMessage(message) {
    document.querySelector('.game-status').innerHTML = message
}

function actionCloseGame(games) {
    resetGames()
    gameList(games)
    send({action: 'close'})
}


function closeGame() {
    resetGames()
    send({action: 'close'})
}


function errorGame(message) {
    alert(message)
}

function closeWS() {
    ws.close()
}

function onlineUsers(count) {
    document.getElementById('online').innerHTML = `Online ${count}`
}

function topUsers(top) {
    let wrapperTop = document.querySelector('.wrapper-top')
    while (wrapperTop.firstChild) {
        wrapperTop.removeChild(wrapperTop.firstChild);
    }
    let j = 1
    for (let user of top) {
        let divId = document.createElement('div')
        let text = document.createTextNode(`${j}`)
        divId.className = 'column'
        divId.appendChild(text)

        let divUser = document.createElement('div')
        text = document.createTextNode(`${user.name}`)
        divUser.className = 'column'
        divUser.appendChild(text)

        let divWin = document.createElement('div')
        text = document.createTextNode(`${user.win}`)
        divWin.className = 'column'
        divWin.appendChild(text)

        let divLose = document.createElement('div')
        text = document.createTextNode(`${user.lose}`)
        divLose.className = 'column'
        divLose.appendChild(text)

        let divDraw = document.createElement('div')
        text = document.createTextNode(`${user.draw}`)
        divDraw.className = 'column'
        divDraw.appendChild(text)

        wrapperTop.appendChild(divId)
        wrapperTop.appendChild(divUser)
        wrapperTop.appendChild(divWin)
        wrapperTop.appendChild(divLose)
        wrapperTop.appendChild(divDraw)
        j++
    }
}

function myStat(myStat) {
    document.querySelector('.column-username').innerHTML = `${myStat.name}`
    document.querySelector('.column-win').innerHTML = `${myStat.win}`
    document.querySelector('.column-lose').innerHTML = `${myStat.lose}`
    document.querySelector('.column-draw').innerHTML = `${myStat.draw}`
}


function checkToken() {
    fetch('http://127.0.0.1:8000/check', {
        method: 'POST',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({token: sessionStorage.getItem('token')})
    })
        .then(response => {
            if (response.ok) {
                return response.json()
            }
            return Promise.reject(response);
        })
        .then(response => sessionStorage.setItem('username', response.username))
        .catch(response => response.json().then(response => {
            sessionStorage.removeItem('token')
            sessionStorage.removeItem('username')
            hideLogout()
            hideBtnMyStat()
            hideUsername()
            showLoginSignup()
        }))
}

document.getElementById('create-game').addEventListener('click', createGame)
document.getElementById('close-game').addEventListener('click', closeGame)
document.querySelectorAll('.cell').forEach(
    cell => cell.addEventListener('click', clickCell)
)

start()
