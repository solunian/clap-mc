<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  // import { emit } from '@tauri-apps/api/event';

  let clap_on = $state(true);
  
  $effect(() => {
    if (clap_on) {
      invoke("call_my_sidecar");
    } else {
      invoke("kill");
    }
  });

  // const click = () => {
  //   emit("click");
  // }
</script>

<main>


<div class="lg">
Clap to control your computer's playback!
</div>

<div class="md">
Toggle: 2 claps
<div>

  ♫ - two claps - toggle play/pause
</div>
</div>

<div class="md">
Selection: 3 claps
<div>
  ♩♫ - one long clap, two short claps - go to next 
</div>
<div>
  ♪♩♩- one short clap, two long claps - go to previous
</div>
</div>

<div class="md">
Volume: 4 claps
<div>
  ♩♩♫ - two long claps, two short claps - volume up
</div>
<div>
  ♩ ♪♩♪- long, short, long, short - volume down
</div>
<div>
  ♩♫♪ - one long clap, three short claps - mute
</div>
</div>

</main>
<!-- <button onclick={click}>kill child</button> -->


<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');

  * {
    font-family: "Poppins", sans-serif;
  }

  main {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .lg {
    font-weight: 600;
    font-size: large;
  }

  .md {
    font-weight: 500;
  }
</style>