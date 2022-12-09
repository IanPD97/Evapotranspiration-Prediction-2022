// Historical data //

const optionMenu = document.querySelector(".select-menu"),
  selectBtn = optionMenu.querySelector(".select-btn"),
  options = optionMenu.querySelectorAll(".option"),
  sBtn_text = optionMenu.querySelector(".sBtn-text");

selectBtn.addEventListener("click", () =>
  optionMenu.classList.toggle("active")
);

options.forEach((option) => {
  option.addEventListener("click", () => {
    let selectedOption = option.querySelector(".option-text").innerText;
    sBtn_text.innerText = selectedOption;
    optionMenu.classList.remove("active");
    var stringWithNumbers = document.getElementById("days").innerHTML;
    var onlyNumbers = stringWithNumbers.replace(/[^0-9]+/g, "");
    var days = onlyNumbers;
    let loading =
      '<span class="icon"><div class="loader"></div> <br>Cargando...</span>';
    document.getElementById("tabla-w").innerHTML = loading;
    document.getElementById("chart-w").innerHTML = "";

    let url = "http://127.0.0.1:4000/historical-water?days=" + String(days);
    fetch(url)
      .then((response) => response.json())
      .then((data) => getData(data))
      .catch((error) => console.log(error));
  });
});


const getData = (data) => {
    let body =
      '<table class="w3-table-all w3-medium"><thead><tr class="w3-primary"><th>Fecha</th><th>Agua (S)(mL)</th><th>Agua (ET)(mL)</th></tr></thead>';
    length = objLength(data.Date);
  
    let body_w =
      '<div class="w3-container w3-white w3-box-shadow w3-round-large w3-padding-16">' +
      '<div class="sensor-name-chart">Agua (mL)</div>' +
      '<div class="chart-container"><canvas id="chart-historical-w"></canvas></div></div>';

    const dataset_water = {
      label: "Agua (S)",
      backgroundColor: "rgb(13, 147, 215)",
      borderColor: "rgb(13, 147, 215)",
      data: [],
      fill: false,
    };
    const dataset_water_et = {
        label: "Agua (ET)",
        backgroundColor: "rgb(65, 110, 114)",
        borderColor: "rgb(65, 110, 114)",
        data: [],
        fill: false,
      };

    const config_historical_w = {
      type: "line",
      data: {
        labels: [],
        datasets: [dataset_water,dataset_water_et],
      },
      options: {
        responsive: true,
        title: {
          display: false,
        },
        tooltips: {
          mode: "index",
          intersect: false,
        },
        hover: {
          mode: "nearest",
          intersect: true,
        },
        scales: {
          xAxes: [
            {
              display: true,
              scaleLabel: {
                display: true,
                labelString: "Time",
              },
            },
          ],
          yAxes: [
            {
              display: true,
              scaleLabel: {
                display: true,
                labelString: "Value",
              },
            },
          ],
        },
      },
    };

    document.getElementById("chart-w").innerHTML = body_w;

    const ctx_historical_w = document
      .getElementById("chart-historical-w")
      .getContext("2d");
  
    if (Chart.getChart("chart-historical-w")) {
      Chart.getChart("chart-historical-w").destroy();
    }
  
    var chart_historical_w = new Chart(ctx_historical_w, config_historical_w);
  
    for (let i = 0; i < length; i++) {
      body += `<tr><td>${data.Date[i]}</td><td>${
        data.Water[i]
      }</td><td>${data.Water_et[i]}</td></tr>`;
  
      config_historical_w.data.labels.push(data.Date[length - i - 1]);
      config_historical_w.data.datasets[0].data.push(data.Water[length - i - 1]);
      config_historical_w.data.datasets[1].data.push(data.Water_et[length - i - 1]);
    }
    chart_historical_w.update();
    document.getElementById("tabla-w").innerHTML = body;
  };
  
  function objLength(obj) {
    var i = 0;
    for (var x in obj) {
      if (obj.hasOwnProperty(x)) {
        i++;
      }
    }
    return i;
  }
  

