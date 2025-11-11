
document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const timeDisplay = document.querySelector('.time-display');
    const startBtn = document.getElementById('start-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const resetBtn = document.getElementById('reset-btn');
    const tabButtons = document.querySelectorAll('.tab-button');
    const cycleDotsContainer = document.getElementById('cycle-dots');
    const alarmSound = document.getElementById('alarm-sound');
    const breakSound = document.getElementById('break-sound');
    const rainSound = document.getElementById('rain-sound');

    // --- Settings Modal Elements ---
    const settingsBtn = document.getElementById('settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const saveSettingsBtn = document.getElementById('save-settings-btn');
    const cancelSettingsBtn = document.getElementById('cancel-settings-btn');
    const pomodoroMinutesInput = document.getElementById('pomodoro-minutes');
    const pomodoroSecondsInput = document.getElementById('pomodoro-seconds');
    const shortBreakMinutesInput = document.getElementById('short-break-minutes');
    const shortBreakSecondsInput = document.getElementById('short-break-seconds');
    const longBreakMinutesInput = document.getElementById('long-break-minutes');
    const longBreakSecondsInput = document.getElementById('long-break-seconds');
    const longBreakIntervalInput = document.getElementById('long-break-interval');

    // --- State ---
    let timers = {};
    let longBreakInterval;
    let currentMode = 'pomodoro';
    let remainingTime;
    let timerInterval = null;
    let pomodoroCycle = 0;
    let isAudioUnlocked = false;

    // --- Audio --- 
    function playSound(sound) {
        alarmSound.pause();
        breakSound.pause();
        rainSound.pause();
        alarmSound.currentTime = 0;
        breakSound.currentTime = 0;
        rainSound.currentTime = 0;
        if (sound) {
            sound.play();
        }
    }

    // --- Core Functions ---
    function updateDisplay() {
        const minutes = Math.floor(remainingTime / 60).toString().padStart(2, '0');
        const seconds = (remainingTime % 60).toString().padStart(2, '0');
        timeDisplay.textContent = `${minutes}:${seconds}`;
        document.title = `${minutes}:${seconds} - ${currentMode === 'pomodoro' ? 'Focus' : 'Break'}`;
    }

    function updateCycleDots() {
        cycleDotsContainer.innerHTML = '';
        for (let i = 0; i < longBreakInterval; i++) {
            const dot = document.createElement('div');
            dot.classList.add('dot');
            if (i < pomodoroCycle) {
                dot.classList.add('completed');
            }
            cycleDotsContainer.appendChild(dot);
        }
    }

    function switchMode(mode) {
        currentMode = mode;
        remainingTime = timers[mode];
        tabButtons.forEach(button => {
            button.classList.toggle('active', button.dataset.mode === mode);
        });
        updateDisplay();
    }

    function stopTimer(shouldReset) {
        clearInterval(timerInterval);
        timerInterval = null;
        startBtn.style.visibility = 'visible';
        pauseBtn.style.visibility = 'hidden';
        playSound(null); // Stop all sounds
        if (shouldReset) {
            remainingTime = timers[currentMode];
            updateDisplay();
        }
    }

    function handleTimerEnd() {
        if (currentMode === 'pomodoro') {
            pomodoroCycle++;
            updateCycleDots();
            if (pomodoroCycle > 0 && pomodoroCycle % longBreakInterval === 0) {
                switchMode('longBreak');
                playSound(rainSound);
            } else {
                switchMode('shortBreak');
                playSound(breakSound);
            }
        } else {
            switchMode('pomodoro');
            playSound(alarmSound);
        }
        // Automatically start the next timer
        startTimer();
    }

    function startTimer() {
        if (timerInterval) return;
        startBtn.style.visibility = 'hidden';
        pauseBtn.style.visibility = 'visible';
        timerInterval = setInterval(() => {
            remainingTime--;
            updateDisplay();
            if (remainingTime < 0) { // Use < 0 to ensure the 00:00 state is displayed for a second
                stopTimer(false);
                handleTimerEnd();
            }
        }, 1000);
    }

    // --- Settings --- 
    function saveSettings() {
        const pomodoroMinutes = parseInt(pomodoroMinutesInput.value, 10) || 0;
        const pomodoroSeconds = parseInt(pomodoroSecondsInput.value, 10) || 0;
        const shortBreakMinutes = parseInt(shortBreakMinutesInput.value, 10) || 0;
        const shortBreakSeconds = parseInt(shortBreakSecondsInput.value, 10) || 0;
        const longBreakMinutes = parseInt(longBreakMinutesInput.value, 10) || 0;
        const longBreakSeconds = parseInt(longBreakSecondsInput.value, 10) || 0;
        const newInterval = parseInt(longBreakIntervalInput.value, 10);

        const newPomodoroTotalSeconds = (pomodoroMinutes * 60) + pomodoroSeconds;
        const newShortBreakTotalSeconds = (shortBreakMinutes * 60) + shortBreakSeconds;
        const newLongBreakTotalSeconds = (longBreakMinutes * 60) + longBreakSeconds;

        if (newPomodoroTotalSeconds > 0 && newShortBreakTotalSeconds > 0 && newLongBreakTotalSeconds > 0 && newInterval > 0) {
            localStorage.setItem('pomodoroSettings', JSON.stringify({
                pomodoro: newPomodoroTotalSeconds,
                shortBreak: newShortBreakTotalSeconds,
                longBreak: newLongBreakTotalSeconds,
                longBreakInterval: newInterval
            }));
            loadSettings();
            closeSettingsModal();
            // Reset timer to apply new settings
            stopTimer(true);
            pomodoroCycle = 0;
            switchMode('pomodoro');
            updateCycleDots();
        } else {
            alert('請確保所有時間欄位都大於 0 秒，且長休間隔大於 0。');
        }
    }

    function loadSettings() {
        const savedSettings = JSON.parse(localStorage.getItem('pomodoroSettings')) || {};
        timers = {
            pomodoro: (savedSettings.pomodoro || 25 * 60),
            shortBreak: (savedSettings.shortBreak || 5 * 60),
            longBreak: (savedSettings.longBreak || 15 * 60),
        };
        longBreakInterval = savedSettings.longBreakInterval || 4;
        remainingTime = timers[currentMode];
    }

    function openSettingsModal() {
        const pomodoroTotalSeconds = timers.pomodoro;
        pomodoroMinutesInput.value = Math.floor(pomodoroTotalSeconds / 60);
        pomodoroSecondsInput.value = pomodoroTotalSeconds % 60;

        const shortBreakTotalSeconds = timers.shortBreak;
        shortBreakMinutesInput.value = Math.floor(shortBreakTotalSeconds / 60);
        shortBreakSecondsInput.value = shortBreakTotalSeconds % 60;

        const longBreakTotalSeconds = timers.longBreak;
        longBreakMinutesInput.value = Math.floor(longBreakTotalSeconds / 60);
        longBreakSecondsInput.value = longBreakTotalSeconds % 60;

        longBreakIntervalInput.value = longBreakInterval;
        settingsModal.style.display = 'flex';
    }

    function closeSettingsModal() {
        settingsModal.style.display = 'none';
    }

    // --- Event Listeners ---
    startBtn.addEventListener('click', () => {
        if (!isAudioUnlocked) {
            // This is a trick to get around browser autoplay policies.
            // The first user click "unlocks" the audio.
            alarmSound.play().catch(() => {});
            alarmSound.pause();
            alarmSound.currentTime = 0;
            breakSound.play().catch(() => {});
            breakSound.pause();
            breakSound.currentTime = 0;
            rainSound.play().catch(() => {});
            rainSound.pause();
            rainSound.currentTime = 0;
            isAudioUnlocked = true;
        }
        startTimer();
    });

    pauseBtn.addEventListener('click', () => stopTimer(false));
    
    resetBtn.addEventListener('click', () => {
        stopTimer(true);
        pomodoroCycle = 0;
        updateCycleDots();
    });

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            if (timerInterval) {
                if (!confirm('計時器正在執行中，確定要切換嗎？這將會重設計時器。')) {
                    return;
                }
                stopTimer(true);
            }
            switchMode(button.dataset.mode);
        });
    });

    settingsBtn.addEventListener('click', openSettingsModal);
    cancelSettingsBtn.addEventListener('click', closeSettingsModal);
    saveSettingsBtn.addEventListener('click', saveSettings);
    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) {
            closeSettingsModal();
        }
    });

    // --- Initial Setup ---
    loadSettings();
    updateDisplay();
    updateCycleDots();
});
