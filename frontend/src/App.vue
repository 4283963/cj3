<template>
  <div id="app">
    <header class="header">
      <div class="container">
        <h1 class="logo" @click="goHome">🐾 流浪猫狗救助领养中心</h1>
        <nav class="nav">
          <router-link to="/animals/gallery" class="nav-link">待领养</router-link>
        </nav>
      </div>
    </header>
    <main class="main">
      <router-view />
    </main>
    <footer class="footer">
      <div class="container">
        <p>© 2024 小区动物保护志愿者团队 · 用爱守护每一个生命</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/animals/gallery')
}
</script>

<style lang="scss" scoped>
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);

  .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
  }

  .logo {
    font-size: 1.5rem;
    font-weight: 700;
    cursor: pointer;
    margin: 0;
  }

  .nav {
    display: flex;
    gap: 2rem;
  }

  .nav-link {
    color: white;
    text-decoration: none;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: background 0.3s;

    &:hover,
    &.router-link-active {
      background: rgba(255, 255, 255, 0.2);
    }
  }
}

.main {
  min-height: calc(100vh - 140px);
  padding: 2rem 0;
}

.footer {
  background: #2d3748;
  color: #a0aec0;
  padding: 1.5rem 0;
  text-align: center;

  p {
    margin: 0;
  }
}
</style>
