let loading = '<span class="icon"><div class="loader"></div> <br>Cargando...</span>'
document.getElementById("forecast-table").innerHTML=loading

let url = "http://127.0.0.1:4000/forecast-data";

fetch(url)
    .then(response => response.json())
    .then(data => getData(data))
    .catch(error => console.log(error))

const getData = (data) => {
    let body = '<table class="w3-table-all w3-medium"><thead><tr class="w3-primary"><th>Fecha</th><th>Evapotranspiración (mm/día)</th><th>Agua (mL)</th></tr></thead>'
    length = objLength(data.Date)
    
    for (let i=0;i<length;i++){
        body += `<tr><td>${data.Date[i]}</td><td>${data.Forecast[i]}</td><td>${data.Water[i]}</td></tr>`
    }
    console.log(data)
    document.getElementById("forecast-table").innerHTML=body
}


function objLength(obj){
    var i=0;
    for (var x in obj){
      if(obj.hasOwnProperty(x)){
        i++;
      }
    } 
    return i
    ;
  }