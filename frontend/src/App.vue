<script setup>
</script>

<template>
  <div id="app-layout">
    <nav class="navbar">
      <router-link to="/">Home</router-link> |
      <router-link to="/dashboard">Dashboard</router-link> |
      <router-link to="/profile">Profilul Meu</router-link> |
      <router-link to="/history">Istoric Împrumuturi</router-link> |
    </nav>

    <main class="content">
      <router-view></router-view> 
    </main>
  </div>
</template>

<style scoped>
.navbar {
  padding: 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  margin-bottom: 20px;
}
.navbar a {
  margin: 0 10px;
  text-decoration: none;
  color: #2c3e50;
  font-weight: bold;
}
.navbar a.router-link-exact-active {
  color: #42b983;
}
.content {
  padding: 0 20px;
}
</style>