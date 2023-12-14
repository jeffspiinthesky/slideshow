const form = document.querySelector("form");
const fileInput = form.querySelector(".file-input");
const progressArea = document.querySelector(".progress-area");
const uploadedArea = document.querySelector(".uploaded-area");
const pictureArea = document.querySelector(".picture-area");
const durationArea = document.querySelector("#duration");

const initSortableList = (e) => {
    e.preventDefault();
    const sortableList = document.querySelector(".sortable-list");    
    const draggingItem = sortableList.querySelector(".dragging");
    const siblings = [...sortableList.querySelectorAll(".picture:not(.dragging)")];
    let nextSibling = siblings.find(sibling => {
        return e.clientY <= sibling.offsetTop + sibling.offsetHeight / 2;
    });
    sortableList.insertBefore(draggingItem, nextSibling);
};

const loadPictures = () => {
    fetch("/pictures")
        .then(function(response) {
            return response.json();
        })
        .then(function(jsonResponse) {
            renderPictures(jsonResponse);
        });
};

const uploadNewOrder = () => {
    const pictures = pictureArea.querySelectorAll('.picture');
    let picArray = [];
    for(picture of pictures) {
        picArray.push(parseInt(picture.getAttribute("id")));
    }
    fetch("/reorder", {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify(picArray),
        })
        .then(function(response) {
            loadPictures();
        });
};

const renderPictures = (pictures) => {
    ulHtml = "<ul class=\"sortable-list\">\n";
    for(let picture of pictures) {
        li =   `<li class="picture" draggable="true" id="${picture[0]}">
                    <div class="content">
                        <img src="/static/images/${picture[1]}"/>
                        <div class="details">
                            <span class="name">${picture[1]}</span>
                        </div>
                    </div>
                    <i class="fas fa-times"></i>
                </li>`
        ulHtml+=li;
    }
    ulHtml += "</ul>\n";
    pictureArea.innerHTML = ulHtml;
    const sortableList = document.querySelector(".sortable-list");    
    sortableList.addEventListener("dragover", initSortableList);
    sortableList.addEventListener("dragenter", e => e.preventDefault());
    pictureRows = document.querySelectorAll(".picture");
    pictureRows.forEach(picture => {
        picture.addEventListener("dragstart", () => {
            setTimeout(() => picture.classList.add('dragging'), 0);
        });
        picture.addEventListener("dragend", () => {
            picture.classList.remove('dragging');
            uploadNewOrder();
        });
        id = picture.getAttribute("id");
        let delButton = picture.querySelector(".fa-times");
        delButton.addEventListener("click", () => {
            id = delButton.parentNode.getAttribute("id");
            fetch("/delpicture", {
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": JSON.stringify({id: id}),
                })
                .then(function(response) {
                    loadPictures();
                });
                })
    });
};


loadPictures();

durationArea.addEventListener("change", () => {
    let duration = { duration: durationArea.value };
    fetch("/updateduration", {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify(duration),
        });;
});

form.addEventListener("click", () => {
    fileInput.click();
});

fileInput.onchange = ({target}) => {
    let file = target.files[0];
    let fileName = file.name;
    if(fileName.length >= 12) {
        let splitName = fileName.split('.');
        fileName = splitName[0].substring(0,12) + "... ." + splitName[1];
    }
    uploadFile(fileName);
};

function uploadFile(fileName) {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload");
    let fileTotal = 0;
    xhr.upload.addEventListener("progress", ({loaded, total}) => {
        let fileLoaded = Math.floor((loaded/total) * 100);
        fileTotal = Math.floor(total/1000);
        console.log(fileLoaded + " / " + fileTotal);
        let progressHTML = `<li class="row">
                                <i class="fas fa-file-alt"></i>
                                <div class="content">
                                    <div class="details">
                                        <span class="name">${fileName} - uploading</span>
                                        <span class="percent">${fileLoaded}%</span>
                                    </div>
                                    <div class="progress-bar">
                                        <div class="progress" style="width: ${fileLoaded}%"></div>
                                    </div>
                                </div>
                            </li>`;
        uploadedArea.innerHTML = "";
        progressArea.innerHTML = progressHTML;
    });
    let formData = new FormData(form);
    xhr.onreadystatechange = function() {
        if(this.readyState == 4) {
            progressArea.innerHTML = "";
            let uploadedHTML = "";
            switch(this.status) {
                case(200): 
                    uploadedHTML = `<li class="row">
                                            <div class="content">
                                                <i class="fas fa-file-alt"></i>
                                                <div class="details">
                                                    <span class="name">${fileName} - uploaded</span>
                                                    <span class="size">${fileTotal} KB</span>
                                                </div>
                                            </div>
                                            <i class="fas fa-check"></i>
                                        </li>`;
                                        uploadedArea.innerHTML = uploadedHTML;
                                        renderPictures(JSON.parse(this.response));
                    break;
                default:
                    uploadedHTML = `<li class="row" style="background: #f26990;">
                                            <div class="content">
                                                <i class="fas fa-file-alt"></i>
                                                <div class="details">
                                                    <span class="name">${fileName} - uploaded</span>
                                                    <span class="size">${fileTotal} KB</span>
                                                </div>
                                            </div>
                                            <i class="fas fa-times"></i>
                                        </li>`;
                                        uploadedArea.innerHTML = uploadedHTML;
                    break;
            }
        }
    };
    xhr.send(formData);
}