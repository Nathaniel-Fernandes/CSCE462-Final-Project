import type { User, Item, ItemType } from "./types";

const domain = "http://localhost:8080";

// create a user
export const fetchUserData = async () => {
    const url = domain + '/users/';
    // console.log(url)
    const options: RequestInit = {
      // mode: 'no-cors',
      method: 'GET'
      // headers: {
      //   // 'Content-Type': 'application/json'
      // },
    };

    const response = await fetch(url, options);
    console.log(response)
    const data = await response.json();

    console.log(data)

    return data;
}

export const createUser = async (user: User) => {
    const url = domain + '/users/create';
    console.log(JSON.stringify(user))
    console.log(url)

    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(user)
    };
  
    const response = await fetch(url, options);
    
    console.log(response)

    if (response.ok) {
      return true
    }

    else {
      return response.status
    }
};

export const updateUser = async (user: User) => {
    console.log(JSON.stringify(user))
    const response = await fetch(domain + '/users/update', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(user)
    });

    if (response.ok) {
      return true
    }

    else {
      return response.status
    }
};

export const updateAdminsNumber = async (phone_number: string) => {
    const response = await fetch(domain + '/user/update-admins-number', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ phone_number })
    });
    
    if (response.ok) {
      return true
    }

    else {
      return response.status
    }
};

export const fetchCabinets = async () => {
  const response = await fetch(domain + '/cabinets', {
    method: 'GET'
  })

  console.log(response)
  const data = await response.json();

  console.log(data)

  return data;
}

export const fetchStatusEvents = async () => {
  const response = await fetch(domain + '/status-events', {
    method: 'GET', 
  })

  console.log(response)
  const data = await response.json();

  console.log(data)

  return data;
}

export const fetchPermissions = async () => {
  const response = await fetch(domain + '/permissions', {
    method: 'GET', 
  })

  console.log(response)
  const data = await response.json();

  console.log(data)

  return data;
}

export const grantPermission = async (personnel_uuid: string, cabinet_id: string) => {
    const response = await fetch(domain + '/permissions/grant', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ personnel_uuid, cabinet_id })
    });
    
    if (response.ok) {
      return true
    }

    else {
      return response.status
    }
};

export const deletePermission = async (personnel_uuid: string, cabinet_id: string) => {
    const response = await fetch(domain + '/permissions/delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ personnel_uuid, cabinet_id })
    });

    if (response.ok) {
      return true
    }

    else {
      return response.status
    }
};

export const remoteUnlock = async (cabinet_id: string) => {
    const response = await fetch(domain + '/remote-unlock', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ cabinet_id })
    });

    if (response.ok) {
      return true
    }

    else {
      return response.status
    }
};

export const fetchItemTypes = async () => {
  const response = await fetch(domain + '/item-types/', {
    method: 'GET'
  })

  const data = await response.json()

  console.log(data)
  return data
}

export const fetchItems = async () => {
  const response = await fetch(domain + '/items/', {
    method: 'GET'
  })

  const data = await response.json()
  console.log(data)

  return data
}

export const createItemType = async (name: string) => {
  console.log(name)

    const response = await fetch(domain + '/item-types/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name } as ItemType)
    });

    if (response.ok) {
      return true
    }

    else {
      return response.status
    }
};

export const deleteItemType = async (name: string) => {
    const response = await fetch(domain + '/item-types/delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name } as ItemType)
    });

    if (response.ok) {
      return true
    }

    else {
      return response.status
    }
};

export const createItem = async (item: Item) => {
    const url = domain + '/items/create';
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(item)
    };
  
    const response = await fetch(url, options);
    
    if (response.ok) {
      return true
    }

    else {
      return response.status
    }
};

export const deleteItem = async (item: Item) => {
    const url = domain + '/items/delete';
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(item)
    };
  
    const response = await fetch(url, options);
    
    if (response.ok) {
      return true
    }

    else {
      return response.status
    }
};
