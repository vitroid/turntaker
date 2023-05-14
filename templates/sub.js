var input = document.getElementById('issue');
var issuepane = document.getElementById('issuepane');

input.addEventListener('change',function(){
    if(this.checked) {
        fetch("{{BASEURL}}/s/{{admin}}/1")
        console.log("block");
        issuepane.style.display="block";
    } else {
        fetch("{{BASEURL}}/s/{{admin}}/0")
        console.log("none");
        issuepane.style.display="none";
    }
});


// Get the input box
let textbox = document.getElementById('title');

// Init a timeout variable to be used below
let timeout = null;

// Listen for keystroke events
textbox.addEventListener('keyup', function (e) {
    // Clear the timeout if it has already been set.
    // This will prevent the previous task from executing
    // if it has been less than <MILLISECONDS>
    clearTimeout(timeout);

    // Make a new timeout set to go off in 1000ms (1 second)
    timeout = setTimeout(function () {
        fetch("{{BASEURL}}/t/{{admin}}/"+textbox.value)
        console.log('Input Value:', textbox.value);
    }, 1000);
});



// QR code generator
var qrcode = new QRCode(document.getElementById("qrcode"), {
    text: "{{baseurl}}/R/{{occasion_id}}",
    width: 128,
    height: 128,
    colorDark : "#000",
    colorLight : "#fff",
    correctLevel : QRCode.CorrectLevel.H
});
