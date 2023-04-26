<script setup lang="ts">
import { reactive, onMounted, ref, computed, watch } from 'vue';
import { fetchItemTypes, fetchItems, createItemType, deleteItemType, createItem } from '../../services/fetch.ts'
import type { Item } from 'services/types';
// import TableLite from "vue3-table-lite/ts"; 
import EasyDataTable from "vue3-easy-data-table"

let itemTypesState: any = ref(new Array());
let items: any = ref(new Array())
const enteredItemTypeName = ref('')

const selectedItemType = ref('')

const name = ref('')
const expiration = ref('') // YYYY-MM-DD
const uuid = ref('')
const itemType = ref('')

const headers = [
    {
      text: 'Name',
    //   filterable: false,
    //   field: 'name',
      value: 'name', 
    },
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

const getItems = async () => {
    try {
        let response = await fetchItems();
        items.value = response
    }
    catch (e) {
        console.log(e);
    }
}

const submitForm = () => {
    const data = {
        name: name.value,
        expiration: expiration.value, // YYYY-MM-DD
        uuid: uuid.value,
        type: itemType.value
    }

    let processedData = Object.entries(data).filter(([key, value]) => value !== '').reduce((obj, [key, value]) => ({ ...obj, [key]: value }), {});
    createItem(processedData as Item)
}
</script>

<template>
  <div>
    <div>
        <h3 class="mt-md bold">4. Create/Delete An Item Type</h3>
        <input type="text" v-model="enteredItemTypeName">
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

        <button class="mt-sm" @click="submitForm()">Create Item</button>
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
            :items="items"
        />
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

.pagination__rows-per-page {
    display: none;
}

</style>
  