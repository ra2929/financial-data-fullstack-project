function() {

var options = {
	animationEnabled: true,
	theme: "light2", // "light1", "light2", "dark1", "dark2"
	exportEnabled: true,
	title:{
		text: "Stock Price"
	},
	axisX: {
		valueFormatString: "MMM"
	},
	axisY: {
		includeZero:false, 
		prefix: "$",
		title: "Price (in USD)"
	},
	data: [{
		type: "candlestick",
		yValueFormatString: "$###0.00",
		xValueFormatString: "MMM",
		dataPoints: [
			{ x: new Date(2016, 00, 01), y: [34.080002, 36.060001, 33.410000, 36.060001] },
			{ x: new Date(2016, 01, 01), y: [36.040001, 37.500000, 35.790001, 36.950001] },
			{ x: new Date(2016, 02, 01), y: [37.099998, 39.720001, 37.060001, 39.169998] },
			{ x: new Date(2016, 03, 01), y: [38.669998, 39.360001, 37.730000, 38.820000] },
			{ x: new Date(2016, 04, 01), y: [38.869999, 39.669998, 37.770000, 39.150002] },
			{ x: new Date(2016, 05, 01), y: [39.099998, 43.419998, 38.580002, 43.209999] },
			{ x: new Date(2016, 06, 01), y: [43.209999, 43.889999, 41.700001, 43.290001] },
			{ x: new Date(2016, 07, 01), y: [43.250000, 43.500000, 40.549999, 40.880001] },
			{ x: new Date(2016, 08, 01), y: [40.849998, 41.700001, 39.549999, 40.610001] },
			{ x: new Date(2016, 09, 01), y: [40.619999, 41.040001, 36.270000, 36.790001] },
			{ x: new Date(2016, 10, 01), y: [36.970001, 39.669998, 36.099998, 38.630001] },
			{ x: new Date(2016, 11, 01), y: [38.630001, 42.840000, 38.160000, 40.380001] }
		]
	}]
};
$("#chartContainer").CanvasJSChart(options);

}
