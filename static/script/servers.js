const eventSource = new EventSource('/server_updates');
const serverList = document.getElementById('server-list');

eventSource.onmessage = function(event) {
    const servers = JSON.parse(event.data).servers; 

    // Identify new servers (not already in the list)
    const newServers = servers.filter(newServer => {
        return !Array.from(serverList.children).some(listItem => {
            return listItem.textContent.includes(newServer.name); // Check if server name exists
        });
    });

    // Identify current servers (already in the list)
    const currentServers = servers.filter(newServer => {
        return !Array.from(serverList.children).some(listItem => {
            return listItem.textContent.includes(newServer.name); // Check if server name exists
        });
    });

    // Add new servers to the list
    newServers.forEach(server => {
        create_element(server)
    });

    // Update servers in list
    currentServers.forEach(server => {
        update_element(server)
    });
};

function update_element(server){

}

function create_element(server){

}