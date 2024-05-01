window.onload = function () {
  // Menu
  const para = document.getElementById("stockMenu");

  var selectorDiv = document.createElement("div");
  selectorDiv.classList.add("selector");

  var selectFieldDiv = document.createElement("div");
  selectFieldDiv.id = "selectField";

  var options = ["ltceur2018", "two", "three", "four", "five", "six", "seven"];
  var choiceStockP = document.createElement("p");
  choiceStockP.id = "choiceStock";
  choiceStockP.textContent = options[0];
  choiceStockP.style = "margin-bottom: 0px;"
  selectFieldDiv.appendChild(choiceStockP);

  var listUl = document.createElement("ul");
  listUl.id = "list";
  listUl.classList.add("hide");
  options.forEach(function (optionText) {
    var li = document.createElement("li");
    li.classList.add("options");
    var p = document.createElement("p");
    p.id = "textOption"
    p.style = "margin-bottom: 0px;"
    p.textContent = optionText;
    li.appendChild(p);
    listUl.appendChild(li);
  });
  selectFieldDiv.appendChild(listUl);
  selectorDiv.appendChild(selectFieldDiv);
  para.appendChild(selectorDiv);
  // --------------------------------------------------------------------------------------------------
  var selectField = document.getElementById("selectField");
  var choiceStock = document.getElementById("choiceStock");
  var options = document.getElementsByClassName("options");
  var list = document.getElementById("list");
  selectField.onclick = function () {
    list.classList.toggle("hide");
  };
  for (option of options) {
    option.onclick = function () {
      choiceStock.innerHTML = this.textContent;
      var Path = "/static/" + choiceStock.textContent.trim() + ".json";
      var title = choiceStock.textContent.trim() + " " + "Stock Chart";
      drawChart(Path,title);
    };
    var Path = "/static/" + choiceStock.textContent.trim() + ".json";
    var title = choiceStock.textContent.trim() + " " + "Stock Chart";
    drawChart(Path,title);
  }
};

function drawChart(Path,title) {
  var dataPoints1 = [],
    dataPoints2 = [],
    dataPoints3 = [];
  var stockChart = new CanvasJS.StockChart("chartContainer", {
    exportEnabled: true,
    theme: "dark1",
    title: {
      text: title,
    },
    charts: [
      {
        toolTip: {
          shared: true,
        },
        axisX: {
          lineThickness: 5,
          tickLength: 0,
          labelFormatter: function (e) {
            return "";
          },
          crosshair: {
            enabled: true,
            snapToDataPoint: true,
            labelFormatter: function (e) {
              return "";
            },
          },
        },
        axisY2: {
          title: "Litecoin Price",
          prefix: "€",
        },
        legend: {
          verticalAlign: "top",
          horizontalAlign: "left",
        },
        data: [
          {
            name: "Price (in EUR)",
            yValueFormatString: "€#,###.##",
            axisYType: "secondary",
            type: "candlestick",
            risingColor: "green",
            fallingColor: "red",
            dataPoints: dataPoints1,
          },
        ],
      },
      {
        height: 100,
        toolTip: {
          shared: true,
        },
        axisX: {
          crosshair: {
            enabled: true,
            snapToDataPoint: true,
          },
        },
        axisY2: {
          prefix: "€",
          title: "LTC/EUR",
        },
        legend: {
          horizontalAlign: "left",
        },
        data: [
          {
            yValueFormatString: "€#,###.##",
            axisYType: "secondary",
            name: "LTC/EUR",
            dataPoints: dataPoints2,
          },
        ],
      },
    ],
    navigator: {
      data: [
        {
          color: "grey",
          dataPoints: dataPoints3,
        },
      ],
      slider: {
        minimum: new Date(2018, 6, 1),
        maximum: new Date(2018, 8, 1),
      },
    },
  });
  $.getJSON(Path, function (data) {
    for (var i = 0; i < data.length; i++) {
      dataPoints1.push({
        x: new Date(data[i].date),
        y: [
          Number(data[i].open),
          Number(data[i].high),
          Number(data[i].low),
          Number(data[i].close),
        ],
        color: data[i].open < data[i].close ? "green" : "red",
      });
      dataPoints2.push({
        x: new Date(data[i].date),
        y: Number(data[i].volume_eur),
        color: data[i].open < data[i].close ? "green" : "red",
      });
      dataPoints3.push({
        x: new Date(data[i].date),
        y: Number(data[i].close),
      });
    }
    stockChart.render();
  });
}
