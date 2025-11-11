
document.addEventListener('DOMContentLoaded', () => {
    document.body.style.opacity = 1;

    // --- DOM Elements ---
    const playerEl = document.getElementById('player');
    const enemyEl = document.getElementById('enemy');
    const playerHpBar = document.getElementById('player-hp');
    const playerHpText = document.getElementById('player-hp-text');
    const playerRageBar = document.getElementById('player-rage');
    const playerRageText = document.getElementById('player-rage-text');
    const enemyHpBar = document.getElementById('enemy-hp');
    const enemyHpText = document.getElementById('enemy-hp-text');
    const enemyStatusEffectsContainer = document.getElementById('enemy-status-effects');
    const playerStatsPanel = document.getElementById('player-stats');
    const enemyStatsPanel = document.getElementById('enemy-stats');
    const actionMenu = document.getElementById('action-menu');
    const skillMenu = document.getElementById('skill-menu');
    const logMessage = document.getElementById('log-message');
    const tooltip = document.getElementById('tooltip');
    const gameOverScreen = document.getElementById('game-over-screen');
    const gameOverMessage = document.getElementById('game-over-message');
    const restartButton = document.getElementById('restart-button');
    const levelUpScreen = document.getElementById('level-up-screen');
    const skillChoice1Container = document.getElementById('skill-choice-1');
    const skillChoice2Container = document.getElementById('skill-choice-2');
    const nextLevelButton = document.getElementById('next-level-button');

    // --- Game State ---
    let player, enemy, isPlayerTurn, isGameOver, currentLevel;

    const initialPlayerState = {
        hp: 100,
        maxHp: 100,
        rage: 0,
        maxRage: 100,
        attackMin: 10,
        attackMax: 15,
        defenseMin: 5,
        defenseMax: 8,
        critChance: 0.10,
        critMultiplier: 1.5,
        isDefending: false,
        cooldowns: {},
        statusEffects: [],
        passives: [],
        hpBar: playerHpBar,
        hpText: playerHpText,
        rageBar: playerRageBar,
        rageText: playerRageText,
        el: playerEl,
    };

    // --- Game Initialization ---
    function initGame() {
        currentLevel = 1;
        player = { ...initialPlayerState, cooldowns: {}, statusEffects: [], passives: [] };
        startNextLevel();
        gameOverScreen.style.display = 'none';
    }

    function createEnemy(level) {
        const levelBonus = level - 1;
        return {
            hp: 100 + levelBonus * 20,
            maxHp: 100 + levelBonus * 20,
            attackMin: 8 + levelBonus * 2,
            attackMax: 11 + levelBonus * 2,
            defenseMin: 3 + levelBonus * 1,
            defenseMax: 6 + levelBonus * 1,
            critChance: 0.10,
            critMultiplier: 1.5,
            isDefending: false,
            cooldowns: {},
            statusEffects: [],
            hpBar: enemyHpBar,
            hpText: enemyHpText,
            el: enemyEl,
        };
    }

    function startNextLevel() {
        enemy = createEnemy(currentLevel);
        player.hp = player.maxHp; // Full heal
        player.rage = 0;
        player.isDefending = false;
        
        isPlayerTurn = true;
        isGameOver = false;

        logMessage.textContent = `Level ${currentLevel}! The battle begins!`;
        levelUpScreen.style.display = 'none';
        nextLevelButton.classList.add('hidden');
        actionMenu.classList.remove('hidden');
        
        player.el.querySelector('.icon').classList.add('turn-indicator-border');
        enemy.el.querySelector('.icon').classList.remove('turn-indicator-border');
        
        updateUI();
    }

    // --- UI & Display ---
    function updateUI() {
        // Player
        player.hpBar.style.width = `${(player.hp / player.maxHp) * 100}%`;
        player.hpText.textContent = `${Math.ceil(player.hp)}/${player.maxHp}`;
        player.rageBar.style.width = `${(player.rage / player.maxRage) * 100}%`;
        player.rageText.textContent = `${player.rage.toFixed(1)}/${player.maxRage}`;

        // Enemy
        enemy.hpBar.style.width = `${(enemy.hp / enemy.maxHp) * 100}%`;
        enemy.hpText.textContent = `${Math.ceil(enemy.hp)}/${enemy.maxHp}`;

        // Enemy Status Effects
        enemyStatusEffectsContainer.innerHTML = '';
        enemy.statusEffects.forEach(effect => {
            const effectIcon = document.createElement('div');
            effectIcon.classList.add('status-icon');
            effectIcon.textContent = `${effect.type.toUpperCase()} (${effect.duration})`;
            enemyStatusEffectsContainer.appendChild(effectIcon);
        });

        // Button States
        actionMenu.querySelectorAll('button').forEach(button => button.disabled = !isPlayerTurn || isGameOver);
        updateSkillButtons();
        updateStatsPanels();
    }

    function updateSkillButtons() {
        skillMenu.querySelectorAll('button').forEach(button => {
            const skillName = button.dataset.skill;
            if (!skillName || skillName === 'back') {
                button.disabled = !isPlayerTurn || isGameOver;
                return;
            }

            let originalText = button.textContent.replace(/ \(CD: \d+\)/, '');
            if (skillName === 'heavy-strike') originalText = 'Heavy Strike';
            if (skillName === 'reckless-attack') originalText = 'Reckless Attack';

            const cd = player.cooldowns[skillName];
            if (cd > 0) {
                button.textContent = `${originalText} (CD: ${cd})`;
            } else {
                button.textContent = originalText;
            }

            let disabled = !isPlayerTurn || isGameOver || cd > 0;
            if (skillName === 'heavy-strike' && player.rage < 5) disabled = true;
            if (skillName === 'reckless-attack' && (player.rage < 8 || player.hp <= player.hp * 0.20)) disabled = true;
            
            button.disabled = disabled;
        });
    }

    function updateStatsPanels() {
        playerStatsPanel.innerHTML = `
            <div>Player (Lvl ${currentLevel})</div>
            <div>ATK: ${player.attackMin}-${player.attackMax}</div>
            <div>DEF: ${player.defenseMin}-${player.defenseMax}</div>
            <div>Crit: ${(player.critChance * 100).toFixed(0)}%</div>
            <div>Crit Dmg: ${player.critMultiplier * 100}%</div>
            ${player.passives.map(p => `<div>Passive: ${p.name}</div>`).join('')}
        `;
        enemyStatsPanel.innerHTML = `
            <div>Enemy</div>
            <div>ATK: ${enemy.attackMin}-${enemy.attackMax}</div>
            <div>DEF: ${enemy.defenseMin}-${enemy.defenseMax}</div>
            <div>Crit: ${(enemy.critChance * 100).toFixed(0)}%</div>
            <div>Crit Dmg: ${enemy.critMultiplier * 100}%</div>
        `;
    }

    // --- Combat Logic ---
    function performAttack(attacker, defender, baseMultiplier = 1.0) {
        let attackPower = Math.floor(Math.random() * (attacker.attackMax - attacker.attackMin + 1)) + attacker.attackMin;
        attackPower *= baseMultiplier;
        let defenseValue = Math.floor(Math.random() * (defender.defenseMax - defender.defenseMin + 1)) + defender.defenseMin;
        let damageDealt = Math.max(1, attackPower - (defender.isDefending ? defenseValue * 2 : defenseValue));
        
        let logText = '';
        let isCritical = Math.random() < attacker.critChance;
        if (isCritical) {
            damageDealt = Math.floor(damageDealt * attacker.critMultiplier);
            logText = `${attacker.el.id} CRITICAL attacks! `;
        } else {
            logText = `${attacker.el.id} attacks! `;
        }

        defender.hp = Math.max(0, defender.hp - damageDealt);
        logText += `${defender.el.id} takes ${damageDealt} damage.`;

        // Passive: Life Steal
        if (attacker === player && player.passives.some(p => p.id === 'lifesteal')) {
            const healAmount = Math.floor(damageDealt * 0.10);
            player.hp = Math.min(player.maxHp, player.hp + healAmount);
            logText += ` Player steals ${healAmount} HP.`;
        }
        
        // Passive: Thorns
        if (defender === player && player.passives.some(p => p.id === 'thorns')) {
            const thornDamage = 5;
            attacker.hp = Math.max(0, attacker.hp - thornDamage);
            logText += ` Enemy takes ${thornDamage} thorn damage.`;
        }

        logMessage.textContent = logText;

        // Rage gain
        if (attacker === player) {
            player.rage = Math.min(player.maxRage, player.rage + (damageDealt * 0.025) + 1);
        } else if (defender === player) {
            player.rage = Math.min(player.maxRage, player.rage + (damageDealt * 0.05) + 1);
        }

        defender.el.classList.add('damaged');
        setTimeout(() => defender.el.classList.remove('damaged'), 500);

        defender.isDefending = false;
        // This was the bug. The turn should end regardless of who the attacker is.
        // By making this unconditional, the enemy turn will now correctly pass back to the player.
        endTurn();
    }

    function performDefend(character) {
        character.isDefending = true;
        logMessage.textContent = `${character.el.id} is defending!`;
        endTurn();
    }

    function useSkill(skillName) {
        let skillUsed = false;
        const rageCost = skillName === 'heavy-strike' ? 5 : 8;
        const cooldown = 4;

        if (player.rage < rageCost) {
            logMessage.textContent = `Not enough Rage for this skill!`;
            return;
        }
        if (player.cooldowns[skillName] > 0) {
            logMessage.textContent = `This skill is on cooldown!`;
            return;
        }

        player.rage -= rageCost;
        player.cooldowns[skillName] = cooldown;

        if (skillName === 'heavy-strike') {
            let attackPower = Math.floor(Math.random() * (player.attackMax - player.attackMin + 1)) + player.attackMin;
            let damage = Math.max(1, Math.floor(attackPower * 1.25) - (enemy.isDefending ? Math.floor(Math.random() * (enemy.defenseMax - enemy.defenseMin + 1)) + enemy.defenseMin * 2 : Math.floor(Math.random() * (enemy.defenseMax - enemy.defenseMin + 1)) + enemy.defenseMin));
            enemy.hp = Math.max(0, enemy.hp - damage);
            logMessage.textContent = `Player uses Heavy Strike! Enemy takes ${damage} damage.`;
            if (Math.random() < 0.70) {
                enemy.statusEffects.push({ type: 'stun', duration: 3 });
                logMessage.textContent += ' Enemy is stunned!';
            }
            skillUsed = true;
        } else if (skillName === 'reckless-attack') {
            const hpCost = Math.floor(player.hp * 0.20);
            if (player.hp <= hpCost) {
                logMessage.textContent = 'Not enough HP for Reckless Attack!';
                player.rage += rageCost; // Refund rage
                player.cooldowns[skillName] = 0; // Reset cooldown
                return;
            }
            player.hp -= hpCost;
            let attackPower = Math.floor(Math.random() * (player.attackMax - player.attackMin + 1)) + player.attackMin;
            let damage = Math.max(1, Math.floor(attackPower * 1.50) + hpCost - (enemy.isDefending ? Math.floor(Math.random() * (enemy.defenseMax - enemy.defenseMin + 1)) + enemy.defenseMin * 2 : Math.floor(Math.random() * (enemy.defenseMax - enemy.defenseMin + 1)) + enemy.defenseMin));
            enemy.hp = Math.max(0, enemy.hp - damage);
            logMessage.textContent = `Player uses Reckless Attack! Player takes ${hpCost} damage. Enemy takes ${damage} damage.`;
            skillUsed = true;
        }

        if (skillUsed) {
            enemy.el.classList.add('damaged');
            setTimeout(() => enemy.el.classList.remove('damaged'), 500);
            endTurn();
        }
    }

    // --- Turn & Game Flow ---
    function endTurn() {
        if (checkGameOver()) return;

        if (isPlayerTurn) { // Player's turn just ended
            Object.keys(player.cooldowns).forEach(skill => {
                if (player.cooldowns[skill] > 0) player.cooldowns[skill]--;
            });
        }

        isPlayerTurn = !isPlayerTurn;
        updateUI();

        if (!isPlayerTurn) { // Enemy's turn
            player.el.querySelector('.icon').classList.remove('turn-indicator-border');
            enemy.el.querySelector('.icon').classList.add('turn-indicator-border');
            
            let isStunned = false;
            enemy.statusEffects = enemy.statusEffects.filter(effect => {
                if (effect.type === 'stun') {
                    isStunned = true;
                    effect.duration--;
                    return effect.duration > 0;
                }
                return true;
            });

            if (isStunned) {
                logMessage.textContent = 'Enemy is stunned and cannot act!';
                setTimeout(endTurn, 1000); // Skip turn
            } else {
                setTimeout(() => performAttack(enemy, player), 1000);
            }
        } else { // Player's turn
            player.el.querySelector('.icon').classList.add('turn-indicator-border');
            enemy.el.querySelector('.icon').classList.remove('turn-indicator-border');
        }
    }

    function checkGameOver() {
        if (player.hp <= 0) {
            isGameOver = true;
            gameOverMessage.textContent = 'You Lose!';
            gameOverScreen.style.display = 'flex';
            restartButton.classList.remove('hidden');
            return true;
        }
        if (enemy.hp <= 0) {
            isGameOver = true;
            actionMenu.classList.add('hidden');
            logMessage.textContent = `You defeated the enemy!`;
            setTimeout(showLevelUpScreen, 1500);
            return true;
        }
        return false;
    }

    // --- Level Up ---
    const statUpgrades = [
        { name: "+10 Max HP", apply: p => p.maxHp += 10 },
        { name: "+2 Attack", apply: p => { p.attackMin += 2; p.attackMax += 2; } },
        { name: "+2 Defense", apply: p => { p.defenseMin += 2; p.defenseMax += 2; } },
        { name: "+5% Crit Chance", apply: p => p.critChance += 0.05 },
    ];

    const passiveUpgrades = [
        { id: 'lifesteal', name: "Life Steal", description: "Attacks heal you for 10% of damage dealt." },
        { id: 'thorns', name: "Thorns", description: "Enemies take 5 damage when they attack you." },
    ];

    function showLevelUpScreen() {
        levelUpScreen.style.display = 'block';
        populateUpgradeChoices();
    }

    function populateUpgradeChoices() {
        skillChoice1Container.innerHTML = '';
        skillChoice2Container.innerHTML = '';

        // Stat boosts
        const availableStats = [...statUpgrades].sort(() => 0.5 - Math.random()).slice(0, 2);
        availableStats.forEach(upgrade => {
            const button = document.createElement('button');
            button.textContent = upgrade.name;
            button.onclick = () => selectUpgrade(upgrade, 'stat');
            skillChoice1Container.appendChild(button);
        });

        // Passive skills
        const availablePassives = passiveUpgrades.filter(pass => !player.passives.some(p => p.id === pass.id));
        if (availablePassives.length > 0) {
            const passive = availablePassives[Math.floor(Math.random() * availablePassives.length)];
            const button = document.createElement('button');
            button.textContent = `${passive.name}: ${passive.description}`;
            button.onclick = () => selectUpgrade(passive, 'passive');
            skillChoice2Container.appendChild(button);
        } else {
            skillChoice2Container.innerHTML = '<p>All passive skills learned!</p>';
        }
    }

    function selectUpgrade(upgrade, type) {
        if (type === 'stat') {
            upgrade.apply(player);
            skillChoice1Container.innerHTML = `<p>Selected: ${upgrade.name}</p>`;
        } else if (type === 'passive') {
            player.passives.push(upgrade);
            skillChoice2Container.innerHTML = `<p>Learned: ${upgrade.name}</p>`;
        }
        nextLevelButton.classList.remove('hidden');
    }

    // --- Event Listeners ---
    actionMenu.addEventListener('click', (e) => {
        if (!isPlayerTurn || !e.target.matches('button')) return;
        const action = e.target.dataset.action;
        if (action === 'attack') performAttack(player, enemy);
        if (action === 'defend') performDefend(player);
        if (action === 'skill') {
            actionMenu.classList.add('hidden');
            skillMenu.classList.remove('hidden');
        }
    });

    skillMenu.addEventListener('click', (e) => {
        if (!isPlayerTurn || !e.target.matches('button')) return;
        const skill = e.target.dataset.skill;
        if (skill === 'back') {
            skillMenu.classList.add('hidden');
            actionMenu.classList.remove('hidden');
        } else {
            useSkill(skill);
            skillMenu.classList.add('hidden');
            actionMenu.classList.remove('hidden');
        }
    });

    restartButton.addEventListener('click', () => {
        gameOverScreen.style.display = 'none';
        restartButton.classList.add('hidden');

        initGame();
    });
    
    nextLevelButton.addEventListener('click', () => {
        currentLevel++;
        startNextLevel();
    });

    skillMenu.addEventListener('mouseover', e => {
        if (e.target.matches('[data-description]')) {
            tooltip.textContent = e.target.dataset.description;
            tooltip.classList.remove('hidden');
        }
    });
    skillMenu.addEventListener('mouseout', () => tooltip.classList.add('hidden'));
    skillMenu.addEventListener('mousemove', e => {
        tooltip.style.left = `${e.clientX + 15}px`;
        tooltip.style.top = `${e.clientY - 30}px`;
    });

    // --- Game Start ---
    initGame();
});
