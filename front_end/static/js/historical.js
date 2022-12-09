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
    var stringWithNumbers = document.getElementById("hours").innerHTML;
    var onlyNumbers = stringWithNumbers.replace(/[^0-9]+/g, "");
    var hours = onlyNumbers;
    let loading =
      '<span class="icon"><div class="loader"></div> <br>Cargando...</span>';
    document.getElementById("tabla").innerHTML = loading;
    document.getElementById("chart-th").innerHTML = "";
    document.getElementById("chart-s").innerHTML = "";

    let url = "http://127.0.0.1:4000/historical-data?hours=" + String(hours);
    fetch(url)
      .then((response) => response.json())
      .then((data) => getData(data))
      .catch((error) => console.log(error));
  });
});

const getData = (data) => {
  let body =
    '<table class="w3-table-all w3-medium"><thead><tr class="w3-primary"><th>Fecha</th><th>Temperatura °C</th><th>Humedad %</th><th>Suelo 1 %</th><th>Suelo 2 %</th><th>Suelo 3 %</th></tr></thead>';
  length = objLength(data.Date);

  let body_th =
    '<div class="w3-container w3-white w3-box-shadow w3-round-large w3-padding-16">' +
    '<div class="sensor-name-chart">Temperatura (°C) Humedad (%)</div>' +
    '<div class="chart-container"><canvas id="chart-historical-th"></canvas></div></div>';
  let body_s =
    '<div class="w3-container w3-white w3-box-shadow w3-round-large w3-padding-16">' +
    '<div class="sensor-name-chart">Humedad del suelo (%)</div><div class="chart-container">' +
    '<canvas id="chart-historical-s"></canvas></div></div>';
  const dataset_temperature = {
    label: "Temperatura",
    backgroundColor: "rgb(186, 186, 0)",
    borderColor: "rgb(186, 186, 0)",
    data: [],
    fill: false,
  };
  const dataset_humidity = {
    label: "Humedad",
    backgroundColor: "rgb(13, 147, 215)",
    borderColor: "rgb(13, 147, 215)",
    data: [],
    fill: false,
  };
  const dataset_soil1 = {
    label: "Suelo 1",
    backgroundColor: "rgb(134, 152, 154)",
    borderColor: "rgb(134, 152, 154)",
    data: [],
    fill: false,
  };
  const dataset_soil2 = {
    label: "Suelo 2",
    backgroundColor: "rgb(87, 152, 154)",
    borderColor: "rgb(87, 152, 154)",
    data: [],
    fill: false,
  };
  const dataset_soil3 = {
    label: "Suelo 3",
    backgroundColor: "rgb(65, 110, 114)",
    borderColor: "rgb(65, 110, 114)",
    data: [],
    fill: false,
  };

  const config_historical_th = {
    type: "line",
    data: {
      labels: [],
      datasets: [dataset_temperature, dataset_humidity],
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
  const config_historical_s = {
    type: "line",
    data: {
      labels: [],
      datasets: [dataset_soil1, dataset_soil2, dataset_soil3],
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

  document.getElementById("chart-th").innerHTML = body_th;
  document.getElementById("chart-s").innerHTML = body_s;
  const ctx_historical_th = document
    .getElementById("chart-historical-th")
    .getContext("2d");

  if (Chart.getChart("chart-historical-th")) {
    Chart.getChart("chart-historical-th").destroy();
  }

  var chart_historical_th = new Chart(ctx_historical_th, config_historical_th);

  const ctx_historical_s = document
    .getElementById("chart-historical-s")
    .getContext("2d");

  if (Chart.getChart("chart-historical-s")) {
    Chart.getChart("chart-historical-s").destroy();
  }

  var chart_historical_s = new Chart(ctx_historical_s, config_historical_s);

  for (let i = 0; i < length; i++) {
    body += `<tr><td>${data.Date[length - i - 1]}</td><td>${
      data.Temperature[length - i - 1]
    }</td><td>${data.Humidity[length - i - 1]}</td><td>${
      data.Soil1[length - i - 1]
    }</td><td>${data.Soil2[length - i - 1]}</td><td>${
      data.Soil3[length - i - 1]
    }</td></tr>`;

    config_historical_th.data.labels.push(data.Date[i]);
    config_historical_s.data.labels.push(data.Date[i]);
    config_historical_th.data.datasets[0].data.push(data.Temperature[i]);
    config_historical_th.data.datasets[1].data.push(data.Humidity[i]);
    config_historical_s.data.datasets[0].data.push(data.Soil1[i]);
    config_historical_s.data.datasets[1].data.push(data.Soil2[i]);
    config_historical_s.data.datasets[2].data.push(data.Soil3[i]);
  }
  chart_historical_th.update();
  chart_historical_s.update();
  document.getElementById("tabla").innerHTML = body;
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
