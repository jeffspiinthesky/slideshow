let backgrounds = document.querySelectorAll(".image");
let imageIndex = 0;
let duration = 30;

const getDuration = () => {
    fetch("/getduration")
    .then(function(response) {
        return response.json();
    })
    .then(function(jsonResponse) {
        console.log(JSON.stringify(jsonResponse, null, 2));
        console.log("Setting duration to " + jsonResponse[0]);
        duration = jsonResponse[0];
        setInterval(changeBackground, duration * 1000);
    });
};

backgrounds[0].classList.add("showing");
getDuration();

const changeBackground = () => {
    backgrounds[imageIndex].classList.remove("showing");
    fetch("/getchange")
    .then(function(response) {
        return response.json();
    })
    .then(function(jsonResponse) {
        if(jsonResponse[0] === 1) {
            fetch("/clearchange")
            .then(function(response) {
                location.reload();
            });
        } else {
            console.log("No change - change flag still " + jsonResponse[0]);
        }
    });

    imageIndex++;
    if(imageIndex >= backgrounds.length) {
        imageIndex = 0;
    }

    backgrounds[imageIndex].classList.add("showing");
};

