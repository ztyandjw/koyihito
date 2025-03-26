<template>
    <div class="container">
        <h1>{{ message }}</h1>
        <button @click="changeMessage">点击我</button>
    </div>
</template>

<script>
export default {
    data() {
        return {
            message: 'Hello Vue!'
        }
    },
    methods: {
        changeMessage() {
            this.message = '你好，Vue!'
        }
    }
}
</script>

<style>
.container {
    text-align: center;
    margin-top: 60px;
}
h1 {
    color: #42b983;
}
button {
    padding: 8px 16px;
    background-color: #42b983;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
</style>