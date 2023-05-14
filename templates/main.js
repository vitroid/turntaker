function setval(id, value){
    var element = document.getElementById(id)
    if ( element ){
        element.innerText = value
    }
}

function increment(){
    var count = document.getElementById("count").innerText
    count ++
    setval("count", count)
    fetch("{{BASEURL}}/set/{{admin}}/"+count)
}


function decrement(){
    var count = document.getElementById("count").innerText
    count --
    setval("count", count)
    fetch("{{BASEURL}}/set/{{admin}}/"+count)
}


// auto-update counter and waiting number
function update_count(){
    fetch("{{BASEURL}}/set/{{admin}}/0")
    .then((res)=>{
        return res.json();
    })
    .then((json)=>{
        // console.log(json)
        setval("title", json.title)
        setval("count", json.count)
        setval("waiting", json.waiting)
    });
}


function update2(){
    fetch("{{BASEURL}}/q/{{token}}")
    .then((res)=>{
        return res.json();
    })
    .then((json)=>{
        console.log(json)
        setval("title", json.title)
        setval("count", json.count)
        if (json.mode == 0){
            document.getElementById("idpane").style.display = "none";
        }else{
            document.getElementById("idpane").style.display = "flex";
        }
        // if ( json.waiting <= json.count ){
        //     document.getElementById("count").style.color = "#F44"
        // }
    });
}
