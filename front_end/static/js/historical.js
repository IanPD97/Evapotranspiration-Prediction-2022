// Historical data //

let loading = '<span class="icon"><div class="loader"></div> <br>Cargando...</span>'
document.getElementById("tabla").innerHTML=loading

let url = "http://127.0.0.1:4000/historical-data";
fetch(url)
    .then(response => response.json())
    .then(data => getData(data))
    .catch(error => console.log(error))

const getData = (data) => {
    let body = '<table class="w3-table-all w3-medium"><thead><tr class="w3-primary"><th>Fecha</th><th>Temperatura</th><th>Humedad</th><th>Suelo 1</th><th>Suelo 2</th><th>Suelo 3</th></tr></thead>'
    length = objLength(data.Date)
    
    for (let i=0;i<length;i++){
        body += `<tr><td>${data.Date[length-i-1]}</td><td>${data.Temperature[length-i-1]}</td><td>${data.Humidity[length-i-1]}</td><td>${data.Soil1[length-i-1]}</td><td>${data.Soil2[length-i-1]}</td><td>${data.Soil3[length-i-1]}</td></tr>`
    }
    
    document.getElementById("tabla").innerHTML=body
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