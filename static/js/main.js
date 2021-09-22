// For confetti effect
function confettiFalling(){
    let box = document.getElementById("box");
    let colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'pink'];

    for (let i = 0; i < 1000; i++){
        let span = document.createElement("span");
        span.classList.add("confetti");
        box.appendChild(span);
    }

    let confetti = document.querySelectorAll('.confetti')

    for (let i = 0; i < confetti.length; i++){
        let size = Math.random() * 0.01 * [i];

        confetti[i].style.width = 5 + size + 'px';
        confetti[i].style.height = 15 + size + 'px';
        confetti[i].style.left = Math.random() * innerWidth + 'px';

        let background = colors[Math.floor(Math.random() * colors.length)];
        confetti[i].style.backgroundColor = background;
        
        box.children[i].style.transform = "rotate("+ size*[i] +"deg)";
    }
}
confettiFalling();