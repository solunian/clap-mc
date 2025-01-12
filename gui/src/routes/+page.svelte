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


<div>
Clap to control your computer's playback!
</div>

<div>
2 claps
♫ - two claps - play/pause
</div>

<div>
Selection: 3 claps
♩♫ - one long clap, two short claps - go to next 
♪♩♩- one short clap, two long claps - go to previous
</div>

<div>
Volume: 4 claps
♩♩♫ - two long claps, two short claps - volume up
♩ ♪♩♪- long, short, long, short - volume down
♩♫♪ - one long clap, three short claps - mute
</div>

<!-- <button onclick={click}>kill child</button> -->
