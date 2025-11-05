const loadJoke = async () => {
    try {
        const norrisJoke = await fetch("https://api.chucknorris.io/jokes/random");
        const jokeData = await norrisJoke.json();
        document.getElementById("joke-text").innerText = jokeData.value;
    } catch (error) {
        console.error("Error fetching joke:", error);
    }
}

document.getElementById("new-joke-btn").addEventListener("click", loadJoke);
