document.addEventListener('DOMContentLoaded', () => {
    const boardData = [];
    const players = [
        { id: 1, name: '玩家 1', money: 1500, position: 0, properties: [] },
        { id: 2, name: '電腦', money: 1500, position: 0, properties: [] }
    ];
    let currentPlayerIndex = 0;
    let round = 1;
    const boardSize = 6;
    const totalCells = (boardSize - 1) * 4;

    // DOM Elements
    const gameBoard = document.getElementById('game-board');
    const logContent = document.getElementById('log-content');
    const rollDiceBtn = document.getElementById('roll-dice-btn');
    const die1Elem = document.getElementById('die1');
    const die2Elem = document.getElementById('die2');
    const decisionPanel = document.getElementById('decision-panel');
    const decisionText = document.getElementById('decision-text');
    const buyBtn = document.getElementById('buy-btn');
    const buildBtn = document.getElementById('build-btn');
    const passBtn = document.getElementById('pass-btn');
    const roundCounterElem = document.getElementById('round-counter');

    function log(message) {
        logContent.innerHTML = message + '<br>' + logContent.innerHTML;
    }

    function updatePlayerInfo() {
        document.getElementById('player1-money').textContent = Math.round(players[0].money);
        document.getElementById('player2-money').textContent = Math.round(players[1].money);
    }

    function updateRoundCounter() {
        roundCounterElem.textContent = `第 ${round} 回合`;
    }

    function createBoard() {
        for (let i = 0; i < boardSize; i++) {
            for (let j = 0; j < boardSize; j++) {
                if (i === 0 || i === boardSize - 1 || j === 0 || j === boardSize - 1) {
                    const cell = document.createElement('div');
                    cell.classList.add('cell');
                    const pathIndex = getPathIndex(i, j);
                    cell.dataset.index = pathIndex;
                    
                    if (!isNaN(pathIndex)) {
                        let type, name, price;
                        if (pathIndex === 0) {
                            type = 'corner'; name = '起點'; price = 0;
                        } else if (pathIndex % 5 === 0) {
                            type = 'corner'; name = '角落'; price = 0;
                        } else {
                            type = 'property'; name = `地產 ${pathIndex}`; price = 100 + pathIndex * 10;
                        }
                        boardData[pathIndex] = { name, type, price, owner: null, houses: 0 };
                        cell.innerHTML = `<div class="name">${name}</div><div class="house-container"></div><div class="price">${price > 0 ? '$'+price : ''}</div>`;
                        cell.classList.add(type);
                    } else {
                        cell.style.visibility = 'hidden';
                    }
                    gameBoard.appendChild(cell);
                } else {
                    const emptyCell = document.createElement('div');
                    emptyCell.style.visibility = 'hidden';
                    gameBoard.appendChild(emptyCell);
                }
            }
        }
        players.forEach(player => {
            const token = document.createElement('div');
            token.id = `player${player.id}-token`;
            token.classList.add('player-token');
            gameBoard.appendChild(token);
            updatePlayerTokenPosition(player);
        });
    }
    
    function getPathIndex(row, col) {
        if (row === boardSize - 1 && col === boardSize - 1) return 0;
        if (row === boardSize - 1) return (boardSize - 1) - col;
        if (col === 0) return (boardSize - 1) + (boardSize - 1 - row);
        if (row === 0) return (boardSize - 1) * 2 + col;
        if (col === boardSize - 1) return (boardSize - 1) * 3 + row;
        return NaN;
    }
    
    function getCoordsFromPathIndex(index) {
        if (index < boardSize - 1) return { row: boardSize - 1, col: (boardSize - 1) - index };
        if (index < (boardSize - 1) * 2) return { row: (boardSize - 1) - (index - (boardSize - 1)), col: 0 };
        if (index < (boardSize - 1) * 3) return { row: 0, col: index - (boardSize - 1) * 2 };
        return { row: index - (boardSize - 1) * 3, col: boardSize - 1 };
    }

    function updatePlayerTokenPosition(player) {
        const token = document.getElementById(`player${player.id}-token`);
        const coords = getCoordsFromPathIndex(player.position);
        const offset = player.id === 1 ? 10 : 30;
        token.style.top = `${coords.row * 80 + offset}px`;
        token.style.left = `${coords.col * 80 + offset}px`;
    }

    function rollDice() {
        const d1 = Math.floor(Math.random() * 6) + 1;
        const d2 = Math.floor(Math.random() * 6) + 1;
        return [d1, d2];
    }

    function updateDiceUI(rolls) {
        die1Elem.textContent = rolls[0];
        die2Elem.textContent = rolls[1];
    }

    function switchTurn() {
        // Check if the current player is the last one. If so, the round ends.
        if (currentPlayerIndex === players.length - 1) {
            round++;
            updateRoundCounter();
        }

        // Move to the next player
        currentPlayerIndex = (currentPlayerIndex + 1) % players.length;

        // Handle next turn
        if (players[currentPlayerIndex].id === 2) { // AI's turn
            setTimeout(playAITurn, 1000);
        } else { // Player's turn
            rollDiceBtn.disabled = false;
            log("輪到您了，請擲骰子。");
        }
    }

    function playTurn() {
        const currentPlayer = players[currentPlayerIndex];
        log(`--- ${currentPlayer.name} 的回合 ---`);
        rollDiceBtn.disabled = true;

        const rolls = rollDice();
        const totalRoll = rolls[0] + rolls[1];
        updateDiceUI(rolls);
        log(`${currentPlayer.name} 擲出了 ${rolls[0]} 和 ${rolls[1]}，共 ${totalRoll} 點。`);
        
        const oldPosition = currentPlayer.position;
        currentPlayer.position = (currentPlayer.position + totalRoll) % totalCells;

        if (currentPlayer.position < oldPosition) {
            log(`${currentPlayer.name} 經過起點，獲得 $150。`);
            currentPlayer.money += 150;
            updatePlayerInfo();
        }

        updatePlayerTokenPosition(currentPlayer);
        log(`${currentPlayer.name} 移動到 ${boardData[currentPlayer.position].name}。`);

        handleLanding(currentPlayer);
    }
    
    function handleLanding(player) {
        const currentCell = boardData[player.position];
        if (currentCell.type !== 'property') {
            switchTurn();
            return;
        }

        if (!currentCell.owner) { // Unowned property
            if (player.money < currentCell.price) {
                log(`${player.name} 的資金不足，無法購買 ${currentCell.name}。`);
                switchTurn();
                return;
            }

            if (player.id === 1) { // Human player's decision
                decisionPanel.style.display = 'block';
                decisionText.textContent = `要用 $${currentCell.price} 購買 ${currentCell.name} 嗎？`;
                buyBtn.style.display = 'inline-block';
                passBtn.textContent = '放棄';
                buildBtn.style.display = 'none';
                
                buyBtn.onclick = () => {
                    buyProperty(player, player.position);
                    decisionPanel.style.display = 'none';
                    switchTurn();
                };
                passBtn.onclick = () => {
                    log(`${player.name} 放棄購買。`);
                    decisionPanel.style.display = 'none';
                    switchTurn();
                };
            } else { // AI player buys automatically
                buyProperty(player, player.position);
                switchTurn();
            }
        } else if (currentCell.owner !== player.id) { // Owned by someone else
            payRent(player, currentCell);
            switchTurn();
        } else if (currentCell.owner === player.id) { // Owned by self
            handleBuild(player, player.position);
        }
    }

    function getBuildCost(cell) {
        return Math.round(cell.price * Math.pow(1.1, cell.houses + 1));
    }

    function handleBuild(player, position) {
        const cell = boardData[position];
        if (cell.houses >= 5) {
            log(`${cell.name} 已蓋滿。`);
            switchTurn();
            return;
        }

        const cost = getBuildCost(cell);
        if (player.money < cost) {
            log(`${player.name} 資金不足，無法蓋房子。`);
            switchTurn();
            return;
        }

        if (player.id === 1) { // Human player
            decisionPanel.style.display = 'block';
            decisionText.textContent = `要花 $${cost} 在 ${cell.name} 上蓋房子嗎？ (目前 ${cell.houses} 間)`;
            buyBtn.style.display = 'none';
            buildBtn.style.display = 'inline-block';
            passBtn.textContent = '下次再說';

            buildBtn.onclick = () => {
                buildHouse(player, position);
                decisionPanel.style.display = 'none';
                switchTurn();
            };
            passBtn.onclick = () => {
                decisionPanel.style.display = 'none';
                switchTurn();
            };

        } else { // AI player
            buildHouse(player, position);
            switchTurn();
        }
    }

    function buildHouse(player, position) {
        const cell = boardData[position];
        const cost = getBuildCost(cell);
        player.money -= cost;
        cell.houses++;
        log(`${player.name} 在 ${cell.name} 上蓋了第 ${cell.houses} 間房子，花費 $${cost}。`);
        updateHouseVisuals(position);
        updatePlayerInfo();
    }

    function updateHouseVisuals(position) {
        const cellElement = document.querySelector(`[data-index='${position}']`);
        const houseContainer = cellElement.querySelector('.house-container');
        houseContainer.innerHTML = ''; // Clear existing houses

        const houses = boardData[position].houses;
        if (houses === 5) {
            const hotel = document.createElement('div');
            hotel.className = 'hotel';
            houseContainer.appendChild(hotel);
        } else {
            for (let i = 0; i < houses; i++) {
                const house = document.createElement('div');
                house.className = 'house';
                houseContainer.appendChild(house);
            }
        }
    }

    function buyProperty(player, position) {
        const cell = boardData[position];
        player.money -= cell.price;
        cell.owner = player.id;
        player.properties.push(position);
        log(`${player.name} 花了 $${cell.price} 購買了 ${cell.name}。`);
        document.querySelector(`[data-index='${position}']`).style.border = `3px solid ${player.id === 1 ? 'blue' : 'red'}`;
        updatePlayerInfo();
    }

    function payRent(player, cell) {
        const owner = players.find(p => p.id === cell.owner);
        const baseRent = cell.price * 0.2; // Changed to 20%
        const totalRent = baseRent * (1 + 0.75 * cell.houses);
        const finalRent = Math.round(totalRent);

        player.money -= finalRent;
        owner.money += finalRent;
        log(`${player.name} 支付了 $${finalRent} 的租金給 ${owner.name}。(${cell.houses} 間房子)`);
        updatePlayerInfo();
    }

    function playAITurn() {
        playTurn();
    }

    rollDiceBtn.addEventListener('click', playTurn);

    function init() {
        log("遊戲開始！輪到玩家 1。");
        createBoard();
        updatePlayerInfo();
        updateRoundCounter();
    }

    init();
});