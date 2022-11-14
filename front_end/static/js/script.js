let toggle = document.querySelector('.toggle');
let navigation = document.querySelector('.navigation');
let main = document.querySelector('.main');
// const Chart = require('chart.js');

toggle.onclick = function(){
    navigation.classList.toggle('active');
    main.classList.toggle('active');
}


let list = document.querySelectorAll('.navigation li');
function activeLink(){
    list.forEach((item)=>
    item.classList.remove('hovered'));
    this.classList.add('hovered');
}


list.forEach((item)=>
item.addEventListener('click',activeLink));




// CHARTS //

$(document).ready(function () {
    const config_temperature = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperatura',
                backgroundColor: 'rgb(186, 186, 0)',
                borderColor: 'rgb(186, 186, 0)',
                data: [],
                fill: false,
            }],
        },
        options: {
            responsive: true,
            title: {
                display: false,
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Time'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Value'
                    }
                }]
            }
        }
    };
    const config_humidity = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Humedad',
                backgroundColor: 'rgb(13, 147, 215)',
                borderColor: 'rgb(13, 147, 215)',
                data: [],
                fill: false,
            }],
        },
        options: {
            responsive: true,
            title: {
                display: false,
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Time'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Value'
                    }
                }]
            }
        }
    };
    const config_soil1 = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Suelo 1',
                backgroundColor: 'rgb(155, 162, 182)',
                borderColor: 'rgb(155, 162, 182)',
                data: [],
                fill: false,
            }],
        },
        options: {
            responsive: true,
            title: {
                display: false,
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Time'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Value'
                    }
                }]
            }
        }
    };
    const config_soil2 = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Suelo 2',
                backgroundColor: 'rgb(155, 162, 182)',
                borderColor: 'rgb(155, 162, 182)',
                data: [],
                fill: false,
            }],
        },
        options: {
            responsive: true,
            title: {
                display: false,
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Time'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Value'
                    }
                }]
            }
        }
    };
    const config_soil3 = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Suelo 3',
                backgroundColor: 'rgb(155, 162, 182)',
                borderColor: 'rgb(155, 162, 182)',
                data: [],
                fill: false,
            }],
        },
        options: {
            responsive: true,
            title: {
                display: false,
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Time'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Value'
                    }
                }]
            }
        }
    };

    const ctx_temperature = document.getElementById('chart-temperature').getContext('2d');
    const ctx_humidity = document.getElementById('chart-humidity').getContext('2d');
    const ctx_soil1 = document.getElementById('chart-soil1').getContext('2d');
    const ctx_soil2 = document.getElementById('chart-soil2').getContext('2d');
    const ctx_soil3 = document.getElementById('chart-soil3').getContext('2d');

    const chart_temperature = new Chart(ctx_temperature, config_temperature);
    const chart_humidity = new Chart(ctx_humidity, config_humidity);
    const chart_soil1 = new Chart(ctx_soil1, config_soil1);
    const chart_soil2 = new Chart(ctx_soil2, config_soil2);
    const chart_soil3 = new Chart(ctx_soil3, config_soil3);


    const source = new EventSource("http://127.0.0.1:4000/chart-data");
    

    source.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (config_temperature.data.labels.length === 10) {

            config_temperature.data.labels.shift();
            config_temperature.data.datasets[0].data.shift();
        }
        if (config_humidity.data.labels.length === 10) {

            config_humidity.data.labels.shift();
            config_humidity.data.datasets[0].data.shift();
        }
        if (config_soil1.data.labels.length === 10) {

            config_soil1.data.labels.shift();
            config_soil1.data.datasets[0].data.shift();
        }
        if (config_soil2.data.labels.length === 10) {

            config_soil2.data.labels.shift();
            config_soil2.data.datasets[0].data.shift();
        }
        if (config_soil3.data.labels.length === 10) {

            config_soil3.data.labels.shift();
            config_soil3.data.datasets[0].data.shift();
        }
        
        config_temperature.data.labels.push(data.time);
        config_temperature.data.datasets[0].data.push(data.temp);

        config_humidity.data.labels.push(data.time);
        config_humidity.data.datasets[0].data.push(data.humidity);

        config_soil1.data.labels.push(data.time);
        config_soil1.data.datasets[0].data.push(data.soil1);

        config_soil2.data.labels.push(data.time);
        config_soil2.data.datasets[0].data.push(data.soil2);

        config_soil3.data.labels.push(data.time);
        config_soil3.data.datasets[0].data.push(data.soil3);
        
        chart_temperature.update();
        chart_humidity.update();
        chart_soil1.update();
        chart_soil2.update();
        chart_soil3.update();
        $(".temp").text("");
        $(".temp").text(Math.round(data.temp)+'°C');
        $(".hum").text("");
        $(".hum").text(Math.round(data.humidity)+'%');
        $(".soil1").text("");
        $(".soil1").text(Math.round(data.soil1)+'%');
        $(".soil2").text("");
        $(".soil2").text(Math.round(data.soil2)+'%');
        $(".soil3").text("");
        $(".soil3").text(Math.round(data.soil3)+'%');
    }
});


