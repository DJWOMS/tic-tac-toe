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
    console.log(event)
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
            moveGame(data.cell, data.move, data.state, data.message)
            break
        case 'close':
            closeGame(data.games)
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
    console.log(iPlayer, gameNumber)
    newGame()
}


function joinGame(event) {
    let btn = event.target
    send({action: 'join', game: btn.id})
}


function startGame(number, player, other_player, move) {
    iPlayer = player
    otherPlayer = other_player
    activeGame = move
    gameNumber = number
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
    let i = 0
    if (game === 0) {
        let gameList = document.getElementById('gameList')
        let ch = gameList.lastElementChild
        if (ch) {
            gameList.removeChild(ch)
            return
        }
    }

    while (i < game) {
        let gameList = document.getElementById('gameList')
        let li = document.createElement('li')
        let text = document.createTextNode(`${i + 1} `)
        let btn = document.createElement('button')
        btn.id = `${i}`
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
    let data = {action: 'move', number: gameNumber, 'cell': cellIndex}
    console.log('data', data)
    send(data)
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
    showListGames()
    send({action: 'close'})
}


document.getElementById('create-game').addEventListener('click', createGame)
document.getElementById('close-game').addEventListener('click', closeGame)
document.querySelectorAll('.cell').forEach(
    cell => cell.addEventListener('click', clickCell)
)











