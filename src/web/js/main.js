
//user clicked button
document.getElementById("userInputButton").addEventListener("click", getUserInput, false);
//user pressed enter '13'
document.getElementById("userInput").addEventListener("keyup", function (event) {
    if (event.keyCode === 13) {
        //cancel the default action
        event.preventDefault();
        //process event
        getUserInput();
    }
});

eel.expose(addUserMsg);
eel.expose(addAppMsg);


// Global tracker for Jarvis container animation timeout
let jarvisTimeout = null;

function triggerJarvisReactive() {
    const jarvisContainer = document.getElementById("jarvisContainer");
    if (jarvisContainer) {
        jarvisContainer.classList.add("listening");
        
        if (jarvisTimeout) {
            clearTimeout(jarvisTimeout);
        }
        
        // Return to calm spinning state after 3.5 seconds
        jarvisTimeout = setTimeout(() => {
            jarvisContainer.classList.remove("listening");
        }, 3500);
    }
}

function addUserMsg(msg) {
    triggerJarvisReactive();
    element = document.getElementById("messages");
    element.innerHTML += '<div class="message from ready rtol">' + msg + '</div>';
    element.scrollTop = element.scrollHeight - element.clientHeight - 15;
    //add delay for animation to complete and then modify class to => "message from"
    index = element.childElementCount - 1;
    setTimeout(changeClass.bind(null, element, index, "message from"), 500);
}

function addAppMsg(msg) {
    triggerJarvisReactive();
    element = document.getElementById("messages");
    element.innerHTML += '<div class="message to ready ltor">' + msg + '</div>';
    element.scrollTop = element.scrollHeight - element.clientHeight - 15;
    //add delay for animation to complete and then modify class to => "message to"
    index = element.childElementCount - 1;
    setTimeout(changeClass.bind(null, element, index, "message to"), 500);
}

function changeClass(element, index, newClass) {
    console.log(newClass +' '+ index);
    element.children[index].className = newClass;
}


function getUserInput() {
    element = document.getElementById("userInput");
    msg = element.value;
    if (msg.length != 0) {
        element.value = "";
        eel.getUserInput(msg);
    }
}

// Fetch and populate microphones on DOM load
window.addEventListener('DOMContentLoaded', async () => {
    // Populate Microphones
    try {
        const mics = await eel.getMicrophones()();
        const select = document.getElementById("micSelect");
        mics.forEach(mic => {
            const opt = document.createElement("option");
            opt.value = mic.index;
            opt.textContent = mic.name;
            select.appendChild(opt);
        });
    } catch (err) {
        console.error("Failed to fetch microphones:", err);
    }
});

// Handle mic selection change
document.getElementById("micSelect").addEventListener("change", (e) => {
    const index = e.target.value;
    eel.setMicrophone(index);
});