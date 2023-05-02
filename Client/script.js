var addButton = document.querySelector("button");
addButton.addEventListener('click',addTask);

document.getElementById("swichLogin").addEventListener('click',function (){
  document.getElementById("badLogin").style.display = "none";
  document.getElementById("badCreate").style.display = "none";
  document.getElementById("createUser").style.display = "none";
  document.getElementById("login").style.display = "";
})

document.getElementById("swichCreate").addEventListener('click',function (){
  document.getElementById("badLogin").style.display = "none";
  document.getElementById("badCreate").style.display = "none";
  document.getElementById("login").style.display = "none";
  document.getElementById("createUser").style.display = "";
})

document.getElementById("loginButton").addEventListener('click',function (){
  email = document.getElementById("emailLogin").value
  password = document.getElementById("passwordLogin").value
  data = ("email=" + encodeURIComponent(email));
  data +=  ("&password=" + encodeURIComponent(password));
  fetch("http://localhost:8080/sessions", {
    credentials: 'include',
    method: "POST",
    body: data,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  }).then(function (response){
    if (response.status == 422){
      document.getElementById("badLogin").style.display = "";
      return;
    }
    refresh()})
})

document.getElementById("createUserButton").addEventListener('click',function (){
  email = document.getElementById("emailNew").value
  password = document.getElementById("passwordNew").value
  namef = document.getElementById("namel").value
  namel = document.getElementById("namef").value
  data = ("email=" + encodeURIComponent(email));
  data +=  ("&password=" + encodeURIComponent(password));
  data +=  ("&namef=" + encodeURIComponent(namef));
  data +=  ("&namel=" + encodeURIComponent(namel));
  fetch("http://localhost:8080/users", {
    credentials: 'include',
    method: "POST",
    body: data,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  }).then(function (response){
    if (response.status == 422){
      document.getElementById("badCreate").style.display = "";
      return;
    }else{refresh();}
  })
})

updating = false;
refresh();
function addTask(){
  var newTaskWords = document.querySelector("input");
  var endDate = document.getElementById("endDate");
  var startDate = document.getElementById("startDate");
  var progress = document.getElementById("progress");
  createTaskOnServer(newTaskWords.value,startDate.value,endDate.value,progress.value)
  newTaskWords.value = "";
  endDate.value = "";
  startDate.value = "";
  progress.value = "";
}

function createTaskOnServer(task,startDate,endDate,progress) {
  data = ("name=" + encodeURIComponent(task));
  data +=  ("&startDate=" + encodeURIComponent(startDate));
  data +=  ("&endDate=" + encodeURIComponent(endDate));
  data +=  ("&progress=" + encodeURIComponent(progress));
  fetch("http://localhost:8080/tasks", {
    credentials: 'include',
    method: "POST",
    body: data,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  }).then(refresh)
}


function refresh(){
fetch("http://localhost:8080/tasks", {credentials: 'include'}).then(function (response){
  response.json().then(function(data){
    if (response.status == 401) {
      document.querySelector("input").style.display = "none";
      document.getElementById("endDate").style.display = "none";
      document.getElementById("startDate").style.display = "none";
      document.getElementById("progress").style.display = "none";
      addButton.style.display = "none";
      // bring up login
      document.getElementById("login").style.display = "";
      return;
    }
    document.getElementById("badCreate").style.display = "none";
    document.getElementById("login").style.display = "none";
    document.getElementById("createUser").style.display = "none";
    document.getElementById("badLogin").style.display = "none";
    document.querySelector("input").style.display = "inline";
    document.getElementById("endDate").style.display = "inline";
    document.getElementById("startDate").style.display = "inline";
    document.getElementById("progress").style.display = "inline";
    addButton.style.display = "";
    updating = false;
    var tasks = data;
    var taskContainer = document.getElementById("contain");
    taskContainer.replaceChildren();
    for (let i = 0; i < tasks.length; i++) {
      var task = document.createElement("div");
      task.classList.remove("flex-item2");
      task.classList.add('flex-item');
      taskContainer.appendChild(task);
      task.id = data[i]["id"];
      var name = document.createElement("div");
      name.innerHTML = data[i]["name"];
      name.classList.add('name');
      var startDate = document.createElement("div");
      startDate.innerHTML = data[i]["startDate"];
      startDate.classList.add('startDate');
      var endDate = document.createElement("div");
      endDate.innerHTML = data[i]["endDate"];
      endDate.classList.add('endDate');
      var progress = document.createElement("div");
      progress.innerHTML = data[i]["progress"] + "%";
      progress.classList.add('progress');
      var deleteButton = document.createElement("button");
      deleteButton.id = data[i]["id"];
      deleteButton.classList.add("deleteButton");
      deleteButton.innerHTML = "Delete";
      task.appendChild(name);
      task.appendChild(startDate);
      task.appendChild(endDate);
      task.appendChild(progress);
      task.appendChild(deleteButton);
      deleteButton.onclick = function () {
        updating = true;
        if(confirm("Are you sure") == false){
          setTimeout(function(){updating = false}, 1);
          return;
        }
        id = this.id;
        fetch("http://localhost:8080/tasks/" + id, {
          credentials: "include",
          method: "DELETE",
          }).then(refresh)
      }
      task.onclick = function () {
        // where I add the update menu
        if(updating){
          return;
        }
        updating = true;
        Name = this.children[0].innerHTML;
        StartDate = this.children[1].innerHTML;
        EndDate = this.children[2].innerHTML;
        Progress = this.children[3].innerHTML;
        this.innerHTML = "";
        this.classList.remove("flex-item");
        this.classList.add("flex-item2");
        var name = document.createElement("input");
        name.value = Name;
        name.classList.add("update");
        var startDate = document.createElement("input");
        startDate.value = StartDate;
        startDate.classList.add("update");
        var endDate = document.createElement("input");
        endDate.value = EndDate;
        endDate.classList.add("update");
        var progress = document.createElement("input");
        progress.type = "number";
        progress.value = Progress.substring(0, Progress.length - 1);
        progress.classList.add("update");
        var updateButton = document.createElement("button");
        updateButton.id = this.id;
        updateButton.innerHTML = "Update";
        this.appendChild(name);
        this.appendChild(startDate);
        this.appendChild(endDate);
        this.appendChild(progress);
        this.appendChild(updateButton);
        updateButton.onclick = function () {
          id = this.id;
          data = ("name=" + encodeURIComponent(name.value));
          data +=  ("&startDate=" + encodeURIComponent(startDate.value));
          data +=  ("&endDate=" + encodeURIComponent(endDate.value));
          data +=  ("&progress=" + encodeURIComponent(progress.value));
          fetch("http://localhost:8080/tasks/" + id, {
            credentials: "include",
            method: "PUT",
            body: data,
            headers: {
              "Content-Type": "application/x-www-form-urlencoded"
            }
          }).then(refresh)
        }
      }
  }}).catch(err => {
    if (response.status == 401) {
      document.querySelector("input").style.display = "none";
      document.getElementById("endDate").style.display = "none";
      document.getElementById("startDate").style.display = "none";
      document.getElementById("progress").style.display = "none";
      addButton.style.display = "none";
      // bring up login
      document.getElementById("login").style.display = "";
      return;
    }
    });
})
}