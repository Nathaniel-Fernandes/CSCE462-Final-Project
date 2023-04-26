<script setup lang="ts">
import { reactive, onMounted, ref, computed, watch } from 'vue';
import { fetchUserData, updateAdminsNumber, updateUser, createUser } from '../../services/fetch.ts'
import type { User } from 'services/types';

let employees: any = ref(new Array());
const enteredPhoneNumber = ref('')
const selectedEmployeeName = ref('')

const first_name = ref('')
const last_name = ref('')
const dob = ref('') // YYYY-MM-DD
const uuid = ref('')
const start_date = ref('') // YYYY-MM-DD
const role = ref('')
const department = ref('')
const salary = ref('')
const phone_number = ref('')

onMounted(async () => {
  try {
    const response = await fetchUserData();
    employees.value = response
  }
  catch (e) {
    console.log(e);
  }

});

const adminPhoneNumber = computed(() => {
  if (employees.value != null && employees.value.length > 0) {
    const admin: User = employees.value.find((item: User) => item.role === "admin");
    if (admin) {
      return admin.phone_number
    }
  }
})

const employeeNames = computed(() => {
  if (employees.value != null && employees.value.length > 0) {
    const map = employees.value.filter((e: any) => e.first_name != "Manager").map((e: any) => `${e.first_name} ${e.last_name}`)
    return map
  }
  else {
    return []
  }
})

const employeeUUIDs = computed(() => {
  if (employees.value != null && employees.value.length > 0) {
    const map = employees.value.filter((e: any) => e.first_name != "Manager").map((e: any) => e.uuid)
    return map
  }
  else {
    return []
  }
})

const selectedEmployee = computed(() => {
  const temp = employees.value.filter((user: User) => selectedEmployeeName.value.startsWith(user.first_name))

  if (temp.length > 0) {
    return temp[0]
  }

  else return null;
})

watch(selectedEmployee, (newVal, oldVal) => {
      if (newVal) {
        first_name.value = newVal.first_name;
        last_name.value = newVal.last_name;
        dob.value = newVal.dob;
        uuid.value = newVal.uuid;
        start_date.value = newVal.start_date;
        role.value = newVal.role;
        department.value = newVal.department;
        salary.value = newVal.salary;
        phone_number.value = newVal.phone_number;
      }
});

const submitForm = () => {
  const data: User = {
    first_name: first_name.value,
    last_name: last_name.value,
    dob: dob.value,
    uuid: uuid.value,
    start_date: start_date.value,
    role: role.value,
    department: department.value,
    salary: salary.value,
    phone_number: phone_number.value,
  }

  let processedData = Object.entries(data).filter(([key, value]) => value !== '').reduce((obj, [key, value]) => ({ ...obj, [key]: value }), {});

  // console.log(processedData)

  if (employeeUUIDs.value.includes(uuid.value)) {
    updateUser(processedData as User)
  }
  else {
    // console.log(data)
    createUser(processedData as User)
  }
}

</script>

<template>
  <div>
    <div>
      <h3 class="bold">1. Update manager's phone number</h3>
      <input type="text" v-model="enteredPhoneNumber" :placeholder="adminPhoneNumber">
      <button class="ms-md" @click="updateAdminsNumber(enteredPhoneNumber)">Update manager's number</button>
    </div>

    <div>
      <h3 class="mt-md bold">2. View Employees</h3>
      <select v-model="selectedEmployeeName" onselect="">
        <option disabled value="">Please select one</option>
        <option v-for="name in employeeNames" :value="name" :key="name"> {{ name }}</option>
      </select>

      <div v-if="selectedEmployeeName != ''" class="employee-info">
        <span>UUID: {{ (selectedEmployee as User).uuid || "-" }} </span>
        <span>Start Date: {{ (selectedEmployee as User).start_date || "-" }} </span>
        <span>Salary: ${{ (selectedEmployee as User).salary || "-" }} </span>
        <span>Role: {{ (selectedEmployee as User).role || "-" }} </span>
        <span>Phone #: {{ (selectedEmployee as User).phone_number || "-" }} </span>
        <span>Department: {{ (selectedEmployee as User).department || "-" }} </span>
        <span>DOB: {{ (selectedEmployee as User).dob || "-" }} </span>
      </div>

      <h3 class="mt-md bold">3. Create or Update Employee</h3>
      <div class="form">
        <div class="column">
          <span>
            <label for="first-name">First Name</label>
            <input id="first-name" :placeholder="first_name" v-model="first_name" />
          </span>
          <span>
            <label for="last-name">Last Name</label>
            <input id="last-name" :placeholder="last_name" v-model="last_name" />
          </span>
          <span>
            <label for="uuid">UUID</label>
            <input id="uuid" :placeholder="uuid" v-model="uuid" />
          </span>
          <span>
            <label for="phone-number">Phone Number</label>
            <input id="phone-number" :placeholder="phone_number" v-model="phone_number" />
          </span>
          <span> 
            <label for="dob">Date of Birth</label>
            <input id="dob" :placeholder="dob" v-model="dob" />
          </span>
        </div>
        <div class="column">
          <span>
            <label for="role">Role</label>
            <input id="role" :placeholder="role" v-model="role" />
          </span>

          <span> 
            <label for="department">Department</label>
            <input id="department" :placeholder="department" v-model="department" />
          </span>
          <span>
            <label for="start-date">Start Date</label>
            <input id="start-date" :placeholder="start_date" v-model="start_date" />
          </span>
          <span>
            <label for="salary">Salary ($)</label>
            <input id="salary" :placeholder="salary" v-model="salary" />
          </span>
        </div>
      </div>

      <button class="mt-sm" @click="submitForm()">Create/Update User</button>
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


</style>
  