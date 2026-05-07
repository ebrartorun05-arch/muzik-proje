async function getRecommendations(){

    const song =
    document.getElementById("songSelect").value;

    const response = await fetch("/recommend",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({
            song:song
        })

    });

    const data = await response.json();

    const resultsDiv =
    document.getElementById("results");

    resultsDiv.innerHTML = "";

    data.forEach(song => {

        resultsDiv.innerHTML += `

        <div class="song-card">

            <h3>${song.track_name}</h3>

            <p>${song.artist}</p>

        </div>

        `;
    });
}