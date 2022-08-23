const ws = new WebSocket('ws://localhost:8000/ws')

let gameNumber = 0
let iPlayer = ''
let otherPlayer
let activeGame = false
let gameState = ["", "", "", "", "", "", "", "", ""]


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
        default:
            break
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


function createdGame(number, state) {
    iPlayer = state
    gameNumber = number
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
    newGame()
}


function moveGame(is_active, cellIndex, move, state, message) {
    let cellClicked = document.querySelector(`[data-cell-index="${cellIndex}"]`)
    document.querySelector('.game-status').innerHTML = message
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
        let btn = document.createElement('button')
        btn.id = `${i}`
        btn.className = 'btn-join'

        if (!games[i]) {
            btn.addEventListener('click', joinGame)
            btn.innerHTML = 'Подключиться'
        } else {
            btn.disabled = true
            btn.innerHTML = 'Занято'
        }

        li.appendChild(text)
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

    gameState[cellIndex] = iPlayer
    cell.innerHTML = iPlayer

    activeGame = false
    send({action: 'move', number: gameNumber, 'cell': cellIndex})
}


function newGame() {
    document.getElementById('game').className = 'game-off container-game'
    document.getElementById('tic-tac-toe').className = 'game-on'
    let state = document.getElementById('player')
    state.className = 'game-on'
    state.innerHTML = `Вы игрок ${iPlayer}`
}


function resetGames() {
    document.getElementById('game').className = 'container-game'
    document.getElementById('tic-tac-toe').className = 'game-off'
    document.querySelectorAll('.cell').forEach(cell => cell.innerHTML = '')
    gameState = ["", "", "", "", "", "", "", "", ""]
    activeGame = false
    iPlayer = ''

    // document.querySelector('.game-status').innerHTML = 'Ожидание игрока'
    let state = document.getElementById('player')
    state.className = 'game-off'
    state.innerHTML = ''
}


function actionCloseGame(games) {
    resetGames()
    gameList(games)
}

function closeGame() {
    resetGames()
    send({action: 'close'})
}


function errorGame(message) {
    alert(message)
}

document.getElementById('create-game').addEventListener('click', createGame)
document.getElementById('close-game').addEventListener('click', closeGame)
document.querySelectorAll('.cell').forEach(
    cell => cell.addEventListener('click', clickCell)
)











