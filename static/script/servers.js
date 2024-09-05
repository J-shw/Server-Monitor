const enabledCheckbox = document.getElementById('online-checkbox');
const disabledCheckbox = document.getElementById('offline-checkbox');

enabledCheckbox.addEventListener('change', function(event) {
    if(enabledCheckbox.checked){
      show("row-True");
    }else{
      hide("row-True");
    }
});

disabledCheckbox.addEventListener('change', function(event) {
    if(disabledCheckbox.checked){
      show("row-False");
    }else{
      hide("row-False");
    }
});

function show(className){
    let elements = document.getElementsByClassName(className);
    Array.from(elements).forEach(element => {
        element.classList.remove('hidden');
    });
}

function hide(className){
    let elements = document.getElementsByClassName(className);
    Array.from(elements).forEach(element => {
        element.classList.add('hidden');
    });
}

function totals(){
    let online = document.getElementById('servers-table').getElementsByClassName('row-True');
    let offline = document.getElementById('servers-table').getElementsByClassName('row-False');

    document.getElementById('online-total').innerHTML = online.length;
    document.getElementById('offline-total').innerHTML = offline.length;
}

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

    let show = 'show';
    if ((!online & server.state==='True') || (!offline & server.state==='False')){
        show = 'hidden';
    }
    row.classList.remove('row-True')
    row.classList.remove('row-False')
    row.classList.remove('show')
    row.classList.remove('hidden')
    row.classList.add(`${show}`)
    row.classList.add(`row-${server.state}`)
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
    <td><button onclick="deleteItem('${server.id}')">Delete</button></td>
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

    row.id = server.id
    row.className.add(`row-${server.state}`)
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
    <td><button onclick="deleteItem('${server.id}')">Delete</button></td>
    `
    TABLE.appendChild(row);
}

function showPopup(id){
    document.getElementById(id).classList.remove('hidden');
    document.getElementById('blanket').classList.remove('hidden');
}

function hidePopup(id){
    document.getElementById(id).classList.add('hidden');
    document.getElementById('blanket').classList.add('hidden');
}

function deleteItem(serverId){
    if (confirm("Are you sure you want to delete this server?")) {
        fetch(`/delete/server/${serverId}`)
        .then(response => {
          if (response.ok) {
            update_servers()
          } else {
            console.error('Error deleting server:', response.statusText);
            alert('Failed to delete server')
          }
        })
        .catch(error => {
          console.error('Error deleting server:', error);
          alert('Failed to delete server')
        })
    }
}

totals()

setInterval(() => { // Refresh server data every 15 seconds
    update_servers()
}, 10000);