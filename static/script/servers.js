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

document.getElementById('add_check_type').addEventListener('change', function(event) {
  let value = document.getElementById('add_check_type').value
  console.log(value)
  if (value == 'ping'){
    document.getElementById('web-scheme').classList.add('hidden');
  }else{
    document.getElementById('web-scheme').classList.remove('hidden');
  }
});

document.getElementById('server-check-type').addEventListener('change', function(event) {
  let value = document.getElementById('server-check-type').value

  if (value == 'ping'){
    document.getElementById('server-scheme-box').classList.add('hidden');
  }else{
    document.getElementById('server-scheme-box').classList.remove('hidden');
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

function showPopup(id){
    document.getElementById(id).classList.remove('hidden');
    document.getElementById('blanket').classList.remove('hidden');
}

function hidePopup(id){
    document.getElementById(id).classList.add('hidden');
    document.getElementById('blanket').classList.add('hidden');
}

function showSidebar(id){
  document.getElementById(id).classList.remove('hidden');
}

function hideSidebar(id){
  document.getElementById(id).classList.add('hidden');
}

function deleteServer(){ // Deletes the server
    let serverId = parseInt(document.getElementById('server-id').value);
    console.log(serverId)
    if (confirm("Are you sure you want to delete this server?")) {
        fetch(`/delete/server/${serverId}`)
        .then(response => {
          if (response.ok) {
            update_servers()
            hidePopup('server-popup')
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

function rowClick(id){
    url = '/get_server/'+id
    fetch(url)
    .then(response => response.json())
    .then(strResponse=>{
        const SERVER = strResponse.server;
        
          document.getElementById('server-id').value = SERVER.id;
          document.getElementById('server-name').value = SERVER.name;
          document.getElementById('server-address').value = SERVER.address;
          document.getElementById('server-check-type').value = SERVER.check_type.toLowerCase()

          if (SERVER.check_type == 'Ping'){ // Hides scheme selection if ping
            document.getElementById('server-scheme-box').classList.add('hidden')
          }else{
            document.getElementById('server-scheme-box').classList.remove('hidden')
            document.getElementById('server-scheme').value = SERVER.scheme;
          }

          loadPingGraph(id, SERVER.check_type.toLowerCase())

          showSidebar("server-sidebar");
    });
}

update_servers()
setInterval(() => { // Refresh server data every 15 seconds
    update_servers()
}, 10000);