<script setup lang="ts">
import { onMounted, ref, computed, watch, onBeforeUnmount } from 'vue';
import type { Ref } from 'vue'
import { fetchItemTypes, fetchItems, createItemType, deleteItemType, createItem, deleteItem } from '../../services/fetch.ts'
import type { Item, ItemType } from 'services/types';
import EasyDataTable from "vue3-easy-data-table"
import type { RealtimeChannel } from '@supabase/supabase-js';
import { supabase } from '@/main';

let itemTypesState: any = ref(new Array());
let items: any = ref(new Array())
const enteredItemTypeName = ref('')

const selectedItemType = ref('')

const name = ref('')
const expiration = ref('') // YYYY-MM-DD
const imagelink = ref('') // YYYY-MM-DD
const uuid = ref('')
const itemType = ref('')

const headers = [
    {
      text: 'Name',
      value: 'name', 
    },
    { text: 'Image', sortable: true, value: 'image' },
    { text: 'UUID', sortable: true, value: 'uuid' },
    { text: 'Expiration', sortable: true, value: 'expiration' },
    { text: 'Type', sortable: true, value: 'type' },
  ]

const itemTypes = computed(() => {
    // console.log(itemTypesState)
  if (itemTypesState.value != null && itemTypesState.value.length > 0) {
    return itemTypesState.value.map((e: any) => e.name)
  }
    return []
})

onMounted(async () => {
    await getItemTypes()
    await getItems();

    subscribeItemTypes();
    subscribeItems();
});

const getItemTypes = async () => {
    try {
        let response = await fetchItemTypes();
        itemTypesState.value = response
    }
    catch (e) {
        console.log(e);
    }
}

let rtchannel1: Ref<RealtimeChannel|undefined> = ref(undefined)
let rtchannel2: Ref<RealtimeChannel|undefined> = ref(undefined)

const subscribeItemTypes = () => {
  rtchannel1.value = supabase
    .channel('fetch-item-types')
    .on('postgres_changes', { event: '*', schema: 'public', table: 'ItemTypes' }, payload => {
      console.log('Change received!', payload)
      try {
        itemTypesState.value = [...itemTypesState.value.filter((e: ItemType) => e.id !== (payload.old as ItemType).id), (payload.new as ItemType)]
      }
      catch(e) {
        console.log(e)
      }
    })
    .subscribe()

    console.log(rtchannel1.value)
}

const subscribeItems = () => {
  rtchannel2.value = supabase
    .channel('get-items')
    .on('postgres_changes', { event: '*', schema: 'public', table: 'Items' }, payload => {
      console.log('Change received!', payload)
      try {
        items.value = [...items.value.filter((e: Item) => e.id !== (payload.old as Item).id), (payload.new as Item)]
      }
      catch(e) {
        console.log(e)
      }
    })
    .subscribe()
}

onBeforeUnmount(async () => {
  if (rtchannel1 != undefined) {
      const result = await supabase.removeChannel(rtchannel1.value as RealtimeChannel)
      console.log(result)
  }
  if (rtchannel2 != undefined) {
      const result = await supabase.removeChannel(rtchannel2.value as RealtimeChannel)
      console.log(result)
  }
})

const getItems = async () => {
    try {
        let response = await fetchItems();
        items.value = response
    }
    catch (e) {
        console.log(e);
    }
}

const submitForm = (action: string) => {
    const data = {
        name: name.value,
        expiration: expiration.value, // YYYY-MM-DD
        uuid: uuid.value,
        type: itemType.value,
        image: imagelink.value
    }

    let processedData = Object.entries(data).filter(([key, value]) => value !== '').reduce((obj, [key, value]) => ({ ...obj, [key]: value }), {});
    
    if (action == "create") {
      createItem(processedData as Item)
    }
    else if (action == "delete") {
      deleteItem(processedData as Item)
    }
}
</script>

<template>
  <div>
    <div>
        <h3 class="mt-md bold">4. Create/Delete An Item Type</h3>
        <input type="text" v-model="enteredItemTypeName" />
        <button class="ms-md" @click="createItemType(enteredItemTypeName)">Create</button>
        <button class="red" @click="deleteItemType(enteredItemTypeName)">Delete</button>
    </div>

    <div>
      <h3 class="bold mt-md">5. Add Item to Inventory</h3>
      <div class="form">
        <div class="column">
          <span>
            <label for="name">Name</label>
            <input id="name" placeholder="Name" v-model="name" />
          </span>
          <span>
            <label for="uuid">UUID</label>
            <input id="uuid" placeholder="EPC Code" v-model="uuid" />
          </span>
          <span>
            <label for="imagelink">Image</label>
            <input id="imagelink" placeholder="" v-model="imagelink" />
          </span>
        </div>

        <div class="column">
          <span>
            <label for="expiration">Expiration</label>
            <input id="expiration" placeholder="YYY-MM-DD" v-model="expiration" />
          </span>
          <span>
            <label for="item-type">Item Type</label>
            <select v-model="itemType">
                <option value="">NULL</option>
                <option v-for="itemType in itemTypes" :value="itemType" :key="itemType">{{ itemType }}</option>
            </select>
          </span>
        </div>

        <div>
          <button class="mt-sm create-item" @click="submitForm('create')">Create Item</button>
          <button class="mt-sm delete-item red" @click="submitForm('delete')">Delete Item</button>
        </div>
      </div>
    </div>

    <div>
      <h3 class="mt-md bold">6. View Types of Inventory</h3>
      <select v-model="selectedItemType">
        <option value="all">All</option>
        <option v-for="itemType in itemTypes" :value="itemType" :key="itemType">{{ itemType }}</option>
      </select>
    </div>

    <div>
        <h3 class="mt-md bold">7. View Inventory</h3>
        <EasyDataTable
            :headers="headers"
            :items="items">
            <template #item-image="{ image }">
                <img class="avator" :src="image" alt=""/>
            </template>
        </EasyDataTable>
    </div>

    
  </div>
</template>

<style>
button {
  color: white;
  font-size: 15px;
  text-align: center;
  padding: 0.25rem 0.625rem;
  border-radius: 0.25rem;
  cursor: pointer;
  background-color: #2b825b;
  border: 0;
}

button.red {
    background-color: #ff6369;
}

.mt-md {
  margin-top: 20px;
}

.ms-md {
  margin: 0 10px;
}

.mt-sm {
  margin-top: 10px;
}

.bold {
  font-weight: bold;
}

hr {
  margin: 20px 0;
}

.employee-info {
  column-count: 2;
  margin-top: 10px;
}

.employee-info>span {
  display: block;
}

.form {
  display: flex;
  gap: 30px;
}

.column > span {
  display: flex;
  justify-content: space-between;
  /* margin-right: 30px; */
  gap: 15px
}

.vue3-easy-data-table {
    /* background-color: white; */
    text-align: center;
    border: 1px solid white;
}

.vue3-easy-data-table table {
    width: 100%
}

.vue3-easy-data-table tr {
  border-bottom: 1px solid white;
  margin: 10px;
  height: 50px;
}

td {
  vertical-align: middle;
}

.pagination__rows-per-page {
    display: none;
}

img {
  width: 50px;
}

.create-item {
  align-self: start;
}

</style>
  