class TrumpetGame {
    constructor() {
        this.trumpetGuy = document.getElementById('trumpet-guy');
        this.moveCount = 0;
        this.isWaldo = false;
        this.initialPosition = {
            bottom: '20px',
            left: '20px',
            top: 'auto'
        };
        this.trumpetImage = 'https://web.archive.org/web/20090829191805/http://geocities.com/BourbonStreet/Inn/6163/skulltrumpet.gif';
        this.waldoImage = 'https://web.archive.org/web/20091026162516/http://geocities.com/Heartland/Hills/5271/home/WALDO.GIF';
        
        this.init();
    }

    init() {
        this.trumpetGuy.addEventListener('mouseenter', () => this.handleHover());
        this.trumpetGuy.addEventListener('click', () => this.handleClick());
        this.resetPosition();
    }

    getRandomPosition()3am-270700 {
        const maxX = window.innerWidth - 100;
        const maxY = window.innerHeight - 100;
        return {
            x: Math.max(20, Math.min(Math.random() * maxX, maxX - 20)),
            y: Math.max(20, Math.min(Math.random() * maxY, maxY - 20))
        };
    }

    handleHover() {
        if (!this.isWaldo) {
            if (this.moveCount < 5) {
                const newPosition = this.getRandomPosition();
                this.trumpetGuy.style.left = `${newPosition.x}px`;
                this.trumpetGuy.style.top = `${newPosition.y}px`;
                this.moveCount++;
            } else if (this.moveCount === 5) {
                this.transformToWaldo();
            }
        }
    }
    handleClick() {
        if (this.isWaldo) {
            this.resetGame();
        }
    }

    transformToWaldo() {
        this.isWaldo = true;
        this.trumpetGuy.style.backgroundImage = `url("${this.waldoImage}")`;
    }

    resetPosition() {
        Object.assign(this.trumpetGuy.style, this.initialPosition);
    }

    resetGame() {
        this.moveCount = 0;
        this.isWaldo = false;
        this.trumpetGuy.style.backgroundImage = `url("${this.trumpetImage}")`;
        this.resetPosition();
    }
}

// Initialize the game
const game = new TrumpetGame();
