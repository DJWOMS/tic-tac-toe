const ws = new WebSocket('ws://localhost:8000/ws')
let iPlayer
let otherPlayer
let activeGame = false
let gameState = ["", "", "", "", "", "", "", "", ""]


ws.onopen = function (event) {
    console.log(event)
    newUser()
}


ws.onmessage = function (event) {
    console.log(event)
    let data = JSON.parse(event.data)
    switch (data.action) {
        case 'new':
            gameList(data.games)
            break
        case 'join':
            startGame(data.action, data.player, data.other_player, data.move)
            break
        case 'create':
            createdGame(data.player)
            break
        case 'move':
            moveGame(data.cell, data.move, data.state, data.message)
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


function createGame(event) {
    send({action: 'create'})
}


function createdGame(state) {
    iPlayer = state
    newGame()
}


function joinGame(event) {
    let btn = event.target
    send({action: 'join', game: btn.id})
}


function startGame(action, player, other_player, move) {
    iPlayer = player
    otherPlayer = other_player
    activeGame = move
    newGame()
}


function moveGame(cellIndex, move, state, message) {
    let cellClicked = document.querySelector(`[data-cell-index="${cellIndex}"]`)
    document.querySelector('.game-status').innerHTML = message
    activeGame = move

    if (!activeGame || gameState[cellIndex] !== "") {
        return
    }

    cellClicked.innerHTML = state
    gameState[cellIndex] = state


}


function gameList(game) {
    showListGames()
    let i = 0
    if (game === 0) {
        // let gameList = document.getElementById('gameList')
        // let ch = gameList.lastElementChild
        // console.log(ch, typeof ch)
        // gameList.removeChild(ch)
        return
    }

    while (i < game) {
        let gameList = document.getElementById('gameList')
        let li = document.createElement('li')
        let text = document.createTextNode(`${i}`)
        let btn = document.createElement('button')
        btn.id = `${i + 1}`
        btn.innerHTML = 'Подключиться'
        btn.addEventListener('click', joinGame)
        li.appendChild(text)
        li.appendChild(btn)
        gameList.appendChild(li)
        i++
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
    send({action: 'move', 'cell': cellIndex})
}


function newGame() {
    document.getElementById('game').className = 'game-off'
    document.getElementById('tic-tac-toe').className = 'game-on'
    let state = document.getElementById('player')
    state.className = 'game-on'
    state.innerHTML = `Вы игрок ${iPlayer}`
}


function showListGames() {
    document.getElementById('game').className = 'game-on'
    document.getElementById('tic-tac-toe').className = 'game-off'
    document.querySelectorAll('.cell').forEach(cell => cell.innerHTML = '')
    gameState = ["", "", "", "", "", "", "", "", ""]
    activeGame = false
    let state = document.getElementById('player')
    document.querySelector('.game-status').innerHTML = 'Ожидание игрока'
    state.className = 'game-off'
    state.innerHTML = ''
}


function closeGame() {
    send({action: 'close'})
}

document.getElementById('create-game').addEventListener('click', createGame)
document.getElementById('close-game').addEventListener('click', closeGame)

document.querySelectorAll('.cell').forEach(cell => cell.addEventListener('click', clickCell))












