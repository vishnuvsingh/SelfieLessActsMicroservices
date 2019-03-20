var corsURL = ""
corsURL = "https://cors-anywhere.herokuapp.com/"


//var url = "http://127.0.0.1:5000";  //Local Running
var url = "http://3.209.1.133:8080";  //AWS Running

url = corsURL + url


//Login
function login(){
    var cUrl = url + "/api/v1/login";
    var username = document.getElementById("luname").value;
    var password = document.getElementById("lpwd").value;
    var error = document.getElementById("loginError");
    var encodePass = SHA1(password)
    var data = {"username":username,"password":encodePass};
    var json = JSON.stringify(data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", cUrl, true);
    xhttp.setRequestHeader('Content-type','application/json; charset=utf-8');

    xhttp.onreadystatechange = function () {

        if (xhttp.readyState == 4){
          var users = xhttp.responseText;
          console.log(users)
        }
        
        if (xhttp.readyState == 4 && xhttp.status == "200") {
          window.location.href = "homepage.html";
        } 

        else if(xhttp.readyState == 4) {
          error.innerHTML = xhttp.status + " : " + xhttp.statusText + " : " + xhttp.responseText;
        }

    }
    xhttp.send(json);
}

//Add user
function add() {

    var cUrl = url + "/api/v1/users";
    var username = document.getElementById("uname").value;
    var password = document.getElementById("pwd").value;
    var error = document.getElementById("signError");
    var encodePass = SHA1(password)
    var data = {"username":username,"password":encodePass};
    console.log(data)
    var json = JSON.stringify(data);
    console.log(data)

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", cUrl, true);
    xhttp.setRequestHeader('Content-type','application/json; charset=utf-8');

    xhttp.onreadystatechange = function () {

        if (xhttp.readyState == 4){
          var users = xhttp.responseText;
          console.log(users)
        }
        
        if (xhttp.readyState == 4 && xhttp.status == "201") {
          console.log("Im here")
          window.location.href = "homepage.html";
        } 

        else if(xhttp.readyState == 4) {
          error.innerHTML = xhttp.status + " : " + xhttp.statusText + " : " + xhttp.responseText;
        }

    }
    xhttp.send(json);

}

//Delete User
function del() {
    var username = document.getElementById("delUname").value;
    var error = document.getElementById("deleteError");
    var cUrl = url + "/api/v1/users/" + username;
    var xhttp = new XMLHttpRequest()
    xhttp.open("DELETE", cUrl, true);

    xhttp.onreadystatechange = function () {

        if (xhttp.readyState == 4){
          var users = xhttp.responseText;
          console.log(users)
        }
        
        if (xhttp.readyState == 4 && xhttp.status == "200") {
          console.log("Im here")
          window.location.href = "index.html";
        } 
        
        else if(xhttp.readyState == 4) {
          error.innerHTML = xhttp.status + " : " + xhttp.statusText + " : " + xhttp.responseText;
        }

    }
    xhttp.send(null);

}