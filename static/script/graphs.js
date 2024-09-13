let graph_1;
let graph_2;

function loadPingGraph(id, type){
    url = '/get_logs/'+id
    fetch(url)
    .then(response => response.json())
    .then(strResponse=>{
        if(strResponse.data == null){
            return
        }
        let graph_1_data = []
        let graph_2_data = []
        let uptime_log = []
        strResponse.data.forEach(row => {
            let state = 0.5
            if(row.state){
                state = 1
                uptime_log.push(1)
            }

            graph_1_data.push({
                x: row.unix_timestamp*1000,
                y: row.trip_time
            })
            graph_2_data.push({
                x: row.unix_timestamp*1000,
                y: state
            })
        });
        document.getElementById('server-uptime').innerHTML = `${((uptime_log.length/strResponse.data.length)*100).toFixed(2)}% Uptime`;

        const GRAPH_1_ELEMENT = document.getElementById('graph-1')
        const GRAPH_2_ELEMENT = document.getElementById('graph-2')

        if (graph_1) {
            graph_1.destroy();
        }
        if (graph_2) {
            graph_2.destroy();
        }
        if (type =='ping'){
            GRAPH_1_ELEMENT.classList.remove('hidden');
            const g1ctx = GRAPH_1_ELEMENT.getContext('2d');
            graph_1 = new Chart(g1ctx, {
                type: 'line', // or another suitable chart type
                data: {
                    datasets: [{
                        data: graph_1_data, // Use the populated graph_1_data array
                        borderColor: 'rgba(75, 192, 192, 1)',
                        tension: 0.1,
                        pointRadius: 0, // Set point radius to 0 to hide data points
                        fill: true, // Fill the area under the line
                        backgroundColor: 'rgba(75, 192, 192, 0.2)' // Fill color (adjust alpha for transparency)
                    }]
                },
                options: {
                    plugins: {
                        legend: {
                            display: false // Hide the legend
                        }
                    },
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'second', // Or another suitable unit based on your data
                                displayFormats: {
                                    day: 'MMM D' 
                                }
                            },
                            title: {
                                display: false,
                                text: 'Date'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Trip Time (ms)'
                            }
                        }
                    }
                }
            });
        }else{
            GRAPH_1_ELEMENT.classList.add('hidden');
        }

        const g2ctx = GRAPH_2_ELEMENT.getContext('2d');
        graph_2 = new Chart(g2ctx, {
            type: 'line', // or another suitable chart type
            data: {
                datasets: [{
                    data: graph_2_data, // Use the populated chart_data array
                    borderColor: 'rgba(75, 192, 192, 1)',
                    tension: 0.1,
                    pointRadius: 0, // Set point radius to 0 to hide data points
                    fill: true, // Fill the area under the line
                    backgroundColor: 'rgba(75, 192, 192, 0.2)', // Fill color (adjust alpha for transparency)
                    segment: {
                        borderColor: ctx => ctx.p0.parsed.y < 1 ? 'red' : 'green', // Color based on Y-value
                        backgroundColor: ctx => ctx.p0.parsed.y < 0.5 ? 'rgba(255, 0, 0, 0.2)' : 'rgba(0, 128, 0, 0.2)'
                    }
                }]
            },
            options: {
                plugins: {
                    legend: {
                        display: false // Hide the legend
                    },
                    title: {
                        display: false // Enable the title
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'second', // Or another suitable unit based on your data
                            displayFormats: {
                                day: 'MMM D' 
                            }
                        },
                        title: {
                            display: false,
                            text: 'Date'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        display: false,
                        title: {
                            display: false
                        },
                        min: 0,
                        max: 1.5
                    }
                }
            }
        });
    })
}