// Function to trigger confetti animation
function triggerConfetti() {
    confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
    });
}

// Check the game result stored in the body attribute
document.addEventListener("DOMContentLoaded", () => {
    const result = document.body.getAttribute("data-result");

    // Trigger confetti if the result is a win
    if (result === 'You Win!') {
        triggerConfetti();
    }
});
