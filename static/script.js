const search = document.getElementById("search");
const songs = document.querySelectorAll(".song-card");

search.addEventListener("input", function() {

    const searchText = search.value.toLowerCase();

    songs.forEach(function(song) {

        const songText = song.innerText.toLowerCase();

        if (songText.includes(searchText)) {
            song.style.display = "block";
        } else {
            song.style.display = "none";
        }

    });

});
