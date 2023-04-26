<script setup lang="ts">
import Manager from './components/Manager.vue'
import Inventory from './components/Inventory.vue';

// use some password protection lol
// let password = "A+ project";
// let userInput;
// while (userInput !== password) {
//   userInput = prompt("Please enter your password:");
//   if (userInput !== password) alert("Incorrect password. Please try again.");
// }

</script>

<template>
  <main>
    <div>
      <h2 class="bold">People</h2>
      <Manager />
    </div>

    <!-- <br /> -->
    <hr />
    <div>
      <h2 class="bold">Inventory</h2>
      <Inventory />
    </div>

    <!-- <br /> -->
    <hr />
    <div>
      <h2>Cabinet Details</h2>
      <!-- 
        1. see all the cabinets
        2. see who has authorization to the cabinets
        3. add authorization to cabinet
        4. see what inventory is in the cabinet
        5. Remote unlock
        6. See if door is open
        7. See history of who has opened the door
        8. 

       -->
    </div>
  </main>
</template>

<style scoped>
</style>
