<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  import { emit } from '@tauri-apps/api/event';
  // import { onDestroy } from 'svelte';

  let clap_on = $state(true);
  
  $effect(() => {
    if (clap_on) {
      invoke("call_my_sidecar");
    } else {
      invoke("kill", { name: "hi" });
    }
  });

  // const click = () => {
  //   emit("click");
  // }
</script>

this is a toggle for keeping the binary active 
<input type="checkbox" bind:checked={clap_on}>

{clap_on}

<!-- <button onclick={click}>kill child</button> -->
