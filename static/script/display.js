function update_servers() {
    url = '/server_updates'
    fetch(url)
    .then(response => response.json())
    .then(strResponse=>{
        const SERVERS = strResponse.servers;
        
        let server_ids = []

        SERVERS.forEach(server => {
            if (document.getElementById(server.id)){
                update_element(server)
            }else{
                create_element(server)
            }
            server_ids.push(server.id)
        });

        let row_ids = Array.from(document.getElementById('servers-table').querySelectorAll('tr')).map(tr => parseInt(tr.id));

        row_ids.forEach(id => {
            if (!server_ids.includes(id)) {
              const elementToRemove = document.getElementById(id); 
              if (elementToRemove) {
                elementToRemove.remove();
              }
            }
          });

        totals();

    });
};

function update_element(server){
    let row = document.getElementById(`${server.id}`);

    const online = document.getElementById('online-checkbox').checked;
    const offline = document.getElementById('offline-checkbox').checked;

    if(server.state != 'None'){
        server.state = server.state ? "True" : "False";
    }

    row.classList.remove('row-True')
    row.classList.remove('row-False')
    row.classList.remove('hidden')

    if ((!online & server.state==='True') || (!offline & server.state==='False')){
        row.classList.add('hidden')
    }

    let dataHTML = `
    <td>
        ${server.trip_time}
    </td>
    <td></td>
    `
    if (server.check_type == 'Fetch'){
        dataHTML = `
        <td></td>
        <td>
            ${server.response_code}
        </td>
        `
    }

    row.classList.add(`row-${server.state}`)
    row.innerHTML = `
    <td>
        <p class="server-state server-state-${server.state}"></p>
    </td>
    <td>
        ${server.check_type}
    </td>
    <td>${server.name}</td>
    <td>${server.address}</td>
    ${dataHTML}
    <td>
        ${server.last_active}
    </td>
    `
}

function create_element(server){
    const TABLE= document.getElementById('servers-table')
    let row = document.createElement('tr')

    const online = document.getElementById('online-checkbox').checked;
    const offline = document.getElementById('offline-checkbox').checked;

    if(server.state != 'None'){
        server.state = server.state ? "True" : "False";
    }

    if ((!online & server.state==='True') || (!offline & server.state==='False')){
        row.className.add('hidden')
    }
    let dataHTML = `
    <td>
        ${server.trip_time}
    </td>
    <td></td>
    `
    if (server.check_type == 'Fetch'){
        dataHTML = `
        <td></td>
        <td>
            ${server.response_code}
        </td>
        `
    }

    row.id = server.id
    row.classList.add(`row-${server.state}`)
    row.innerHTML = `
    <td>
        <p class="server-state server-state-${server.state}"></p>
    </td>
    <td>
        ${server.check_type}
    </td>
    <td>${server.name}</td>
    <td>${server.address}</td>
    ${dataHTML}
    <td>
        ${server.last_active}
    </td>
    `
    row.addEventListener("click", function(event) {     
        rowClick(server.id);
    });

    TABLE.appendChild(row);
}