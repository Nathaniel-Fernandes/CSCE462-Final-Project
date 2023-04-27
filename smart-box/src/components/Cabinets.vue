<script setup lang="ts">
import { onMounted, ref, computed, watch, onBeforeUnmount } from 'vue';
import type { Ref } from 'vue'
import { fetchCabinets, fetchStatusEvents, remoteUnlock, grantPermission, deletePermission, fetchUserData, fetchPermissions } from '../../services/fetch.ts'
import type { Item, ItemType, User } from 'services/types';
import EasyDataTable from "vue3-easy-data-table"
import type { RealtimeChannel } from '@supabase/supabase-js';
import { supabase } from '@/main';
import { DateTime } from 'luxon'

const cabinets = ref(new Array())
const cabinetIDs = computed(() => cabinets.value.map((c) => c.cabinet_id))
const selectedCabinet = ref('')

const statusEvents = ref(new Array())
const permissions = ref(new Array())

const currCabinetPermissions = computed(() => permissions.value.filter((p) => p.cabinet_id === selectedCabinet.value))
const currCabinetStatusEvents = computed(() => statusEvents.value.filter((p) => p.cabinet_id === selectedCabinet.value))

console.log(currCabinetPermissions)

const uuidToGrant = ref('')

const employees: any = ref(new Array());

const rtchannel1: Ref<RealtimeChannel|undefined> = ref(undefined)
const rtchannel2: Ref<RealtimeChannel|undefined> = ref(undefined)
const rtchannel3: Ref<RealtimeChannel|undefined> = ref(undefined)

const subscribeToTables = () => {
    rtchannel1.value = supabase.channel('fetch-status-events')
        .on('postgres_changes', {event: 'INSERT', schema: 'public', table: 'Events'}, payload => {
            console.log('Change received!', payload)
            try {
                statusEvents.value = [payload.new, ...statusEvents.value]
            }
            catch(e) {
                console.log(e)
            }
    }).subscribe()
    
    rtchannel2.value = supabase.channel('fetch-permissions')
        .on('postgres_changes', {event: '*', schema: 'public', table: 'Permissions'}, payload => {
            console.log('change received!', payload)
            try {
                permissions.value = [...permissions.value.filter(e => e.id !== (payload.old as ItemType).id), (payload.new as ItemType)]
            }
            catch (e) {
                console.log(e)
            }
        }).subscribe()

    rtchannel3.value = supabase
    .channel('fetch-employees')
    .on('postgres_changes', { event: '*', schema: 'public', table: 'Users' }, payload => {
      console.log('Change received!', payload)
      try {
        employees.value = [...employees.value.filter((e: User) => e.id !== (payload.old as User).id), (payload.new as User)]
      }
      catch(e) {
        console.log(e)
      }
    })
    .subscribe()
}

onMounted(async () => {
    employees.value = await fetchUserData();
    cabinets.value = await fetchCabinets();
    statusEvents.value = await fetchStatusEvents();
    permissions.value = await fetchPermissions();

    subscribeToTables()
});

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

</script>

<template>

<label style="display: block;" for="select-cabinet">Select a cabinet to start: {{ selectedCabinet }}</label>
<select id="select-cabinet" v-model="selectedCabinet">
  <option value="all">All</option>
  <option v-for="cabinetID in cabinetIDs" :value="cabinetID" :key="cabinetID"></option>
</select>

<div v-if="selectedCabinet !== '' && selectedCabinet !== 'all'">
  <h3 class="bold mt-md">7. Remote Unlock</h3>
  <button class="red" @click="remoteUnlock(selectedCabinet)">Unlock Cabinet</button>


  <h3 class="bold mt-md">8. Authorized Personnel</h3>

  <input type="text" placeholder="UUID of Employee" v-model="uuidToGrant"/>
  <button @click="grantPermission(uuidToGrant, selectedCabinet)">Grant Access To Cabinet {{ selectedCabinet }}</button>

  <span>Users w/ Authorization</span>
  <div v-for="permission in currCabinetPermissions" class="permission">
    <span>{{ employees.filter((e: any) => e.uuid === permission.personnel_uuid)[0]?.name }}</span>
    <span>{{ permission.personnel_uuid }}</span>
    <button @click="deletePermission(permission.personnel_uuid, selectedCabinet)" class="red" >Delete</button>
  </div>
</div>

<div v-if="selectedCabinet !== '' && selectedCabinet !== 'all'">
  <h3>Status Events</h3>
  <table class="table">
    <tr>
      <th>Inserted At</th>
      <th>Event</th>
      <th>UUID's Detected</th>
      <th>User</th>
    </tr>
    <tr v-for="event in currCabinetStatusEvents" :key="event.inserted_at">
      <td>{{ DateTime.fromISO(event.inserted_at).toLocaleString(DateTime.DATETIME_SHORT_WITH_SECONDS) }}</td>
      <td>{{ event.event }}</td>
      <td>{{ event.scan_result }}</td>
      <td>{{ event.user }}</td>
    </tr>
  </table>
</div>

</template>

<style>
table.table {
  width: 100%;
  text-align: center;
  border: 1px solid white;
}

.table td {
  border: 1px solid white;
}

.permission {
  margin: 10px;
}

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

img {
  width: 50px;
}

.create-item {
  align-self: start;
}

#select-cabinet {
  width: 50px;
}

#select-cabinet option {
  color: black;
}

</style>
  