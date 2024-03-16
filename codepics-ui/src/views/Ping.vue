<template>
  <div>
    <p>ping... {{ msg }}</p>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'PingView',
  data() {
    return {
      msg: ''
    }
  },
  methods: {
    ping() {
      const path = 'http://localhost:5001/ping'
      axios
        .get(path)
        .then((res) => {
          this.msg = res.data
        })
        .catch((error) => {
          console.error(error)
        })
    }
  },
  created() {
    this.ping()
  }
}
</script>
