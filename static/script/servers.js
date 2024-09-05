function update_servers() {
    url = '/server_updates'
    fetch(url)
    .then(response => response.json())
    .then(strResponse=>{
        const SERVERS = strResponse.servers;

        SERVERS.forEach(server => {
            if (document.getElementById(server.id)){
                update_element(server)
            }else{
                create_element(server)
            }
        });

    });
};

function update_element(server){
    let row = document.getElementById(`${server.id}`);

    if(server.state != 'None'){
        server.state = server.state ? "True" : "False";
    }

    row.innerHTML = `
    <tr id="${server.id}">
        <td>
            <p class="server-state server-state-${server.state}"></p>
        </td>
        <td>${server.name}</td>
        <td>${server.ip}</td>
        <td>
            ${server.trip_time}
        </td>
        <td>
            ${server.last_active}
        </td> 
    </tr>
    `
}

function create_element(server){
    const TABLE= document.getElementById('servers-table')
    let row = document.createElement('tr')

    if(server.state != 'None'){
        server.state = server.state ? "True" : "False";
    }

    row.id = server.id
    row.innerHTML = `
    <td>
        <p class="server-state server-state-${server.state}"></p>
    </td>
    <td>${server.name}</td>
    <td>${server.ip}</td>
    <td>
        ${server.trip_time}
    </td>
    <td>
        ${server.last_active}
    </td> 
    `
    TABLE.appendChild(row);
}

setInterval(() => { // Refresh every 15 seconds
    update_servers()
}, 10000);