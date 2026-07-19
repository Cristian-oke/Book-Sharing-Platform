<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { token } from '../auth'

const BASE_URL = 'http://localhost:5000'

// Stări pentru date
const stats = ref(null)
const users = ref([])
const books = ref([])
const reviews = ref([])

//UI control
const activeTab = ref('stats') // stats/ user/ books /reviews
const isLoading = ref(true)
const errorMsg = ref('')

const config = { headers: { Authorization: `Bearer ${token.value}` } }

const loadAdminData = async () => {
  try {
    isLoading.value = true
    errorMsg.value = ''
    
    const [statsRes, usersRes, booksRes, reviewsRes] = await Promise.all([
      axios.get(`${BASE_URL}/Book_Sharing/admin/stats`, config),
      axios.get(`${BASE_URL}/Book_Sharing/admin/view-users`, config),
      axios.get(`${BASE_URL}/Book_Sharing/books/view-books`),
      axios.get(`${BASE_URL}/Book_Sharing/reviews/all-reviews`, config)
    ])
    
    stats.value = statsRes.data
    users.value = usersRes.data
    books.value = booksRes.data 
    reviews.value = reviewsRes.data
  } catch (err) {
    console.error("Eroare la încărcarea panoului de admin:", err)
    errorMsg.value = "Eroare la securizarea sau preluarea datelor de administrare."
  } finally {
    isLoading.value = false
  }
}

const deleteUser = async (userId, name) => {
  if (!confirm(`Sigur vrei să ștergi utilizatorul "${name}"? Această acțiune va șterge toate cărțile și recenziile sale!`)) return
  try {
    await axios.delete(`${BASE_URL}/Book_Sharing/admin/delete-user/${userId}`, config)
    alert("Utilizator șters cu succes!")
    loadAdminData()
  } catch (err) {
    alert("Eroare la ștergerea utilizatorului: " + (err.response?.data?.error || err.message))
  }
}

const deleteBook = async (bookId, title) => {
  if (!confirm(`Sigur vrei să ștergi cartea "${title}" de pe platformă?`)) return
  try {
    await axios.delete(`${BASE_URL}/Book_Sharing/books/delete/${bookId}`, config)
    alert("Carte ștearsă cu succes!")
    loadAdminData()
  } catch (err) {
    alert("Eroare la ștergerea cărții.")
  }
}

const deleteReview = async (reviewId) => {
  if (!confirm("Sigur vrei să ștergi această recenzie?")) return
  try {
    await axios.delete(`${BASE_URL}/Book_Sharing/reviews/delete-review/${reviewId}`, config)
    alert("Recenzie ștearsă!")
    loadAdminData()
  } catch (err) {
    alert("Eroare la ștergerea recenziei.")
  }
}

onMounted(() => {
  loadAdminData()
})
</script>

<template>
  <div class="admin-container">
    <header class="admin-header">
      <h1>⚙️ Administrare Platformă</h1>
    </header>

    <div class="admin-tabs">
      <button :class="{ active: activeTab === 'stats' }" @click="activeTab = 'stats'">📈 Statistici</button>
      <button :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">👥 Utilizatori ({{ users.length }})</button>
      <button :class="{ active: activeTab === 'books' }" @click="activeTab = 'books'">📚 Cărți ({{ books.length }})</button>
      <button :class="{ active: activeTab === 'reviews' }" @click="activeTab = 'reviews'">⭐ Recenzii ({{ reviews.length }})</button>
    </div>

    <div v-if="isLoading" class="status-box">Se procesează baza de date...</div>
    <div v-else-if="errorMsg" class="status-box error">⚠️ {{ errorMsg }}</div>
    <div v-else class="tab-content">
      
      <!--STATISTICI -->
      <div v-if="activeTab === 'stats' && stats">
        <div class="stats-grid">
          <div class="stat-card">
            <span class="stat-icon">👥</span>
            <div class="stat-info"><span class="stat-label">Utilizatori</span><span class="stat-value">{{ stats.total.users }}</span></div>
          </div>
          <div class="stat-card">
            <span class="stat-icon">📚</span>
            <div class="stat-info"><span class="stat-label">Cărți pe platformă</span><span class="stat-value">{{ stats.total.books }}</span></div>
          </div>
          <div class="stat-card">
            <span class="stat-icon">⚡</span>
            <div class="stat-info"><span class="stat-label">Împrumuturi Active</span><span class="stat-value">{{ stats.live_activity.current_active_loans }}</span></div>
          </div>
          <div class="stat-card">
           <span class="stat-icon">⭐</span>
           <div class="stat-info">
           <span class="stat-label">Recenzii Totale</span>
           <span class="stat-value">{{ reviews.length }}</span>
      </div>
    </div>
        </div>
      </div>

      <!--UTILIZATORI -->
      <div v-if="activeTab === 'users'">
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nume</th>
              <th>Oraș</th>
              <th>Acțiuni</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>#{{ u.id }}</td>
              <td><strong>{{ u.name }}</strong></td>
              <td>{{ u.city }}</td>
              <td>
                <button class="btn-delete" @click="deleteUser(u.id, u.name)">🗑️ Șterge</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!--CĂRȚI -->
      <div v-if="activeTab === 'books'">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Imagine atașată</th>
              <th>Titlu / Autor</th>
              <th>Status</th>
              <th>Acțiuni</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in books" :key="b.id">
              <td>
                <img :src="b.image_url || '/default-image.jpg'" class="table-thumb" />
              </td>
              <td>
                <strong>{{ b.title }}</strong>
                <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #64748b;">de {{ b.author }}</p>
              </td>
              <td><span class="badge">{{ b.availability || 'Disponibil' }}</span></td>
              <td>
                <button class="btn-delete" @click="deleteBook(b.id, b.title)">🗑️ Șterge</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!--RECENZII -->
      <div v-if="activeTab === 'reviews'">
        <div v-if="reviews.length === 0" class="empty-msg">Nu există recenzii pe platformă</div>
        <table v-else class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Notă</th>
              <th>Comentariu</th>
              <th>Acțiuni</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in reviews" :key="r.id">
              <td>#{{ r.id }}</td>
              <td><strong style="color: #f59e0b;">⭐ {{ r.rating }}/5</strong></td>
              <td><span class="comment-text">{{ r.comment || '----' }}</span></td>
              <td>
                <button class="btn-delete" @click="deleteReview(r.id)">🗑️ Șterge</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>

<style scoped>
.admin-container { max-width: 1100px; margin: 40px auto; padding: 0 20px; font-family: system-ui, sans-serif; }
.admin-header { display: flex; justify-content: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 20px; }
.admin-header h1 { color: #1e293b; font-size: 1.6rem; margin: 0;margin-top:30px;margin-bottom: 35px; }

.admin-tabs { display: flex;justify-content: center; gap: 10px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 75px; }
.admin-tabs button { background: #f1f5f9; border: none; padding: 14px 28px; border-radius: 8px; cursor: pointer; font-weight: 600; color: #475569; transition: all 0.2s;font-size: 0.9rem; }
.admin-tabs button:hover { background: #e2e8f0; }
.admin-tabs button.active { background: #7b8293; color: white; }

.admin-table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; 
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);border: 2px solid #cbd5e1; }

.admin-table th, .admin-table td { padding: 14px 18px; text-align: left; border-bottom: 2px solid #cbd5e1;border-right: 1px solid #e2e8f0; }

.admin-table th:last-child, .admin-table td:last-child {border-right: none;}
.admin-table th {background: #7a7d83;color: #ffffff;font-weight: 700;font-size: 0.95rem; border-bottom: 3px solid #1e293b;}
.admin-table tr:nth-child(even) {background: #f8fafc;}
.admin-table tr:hover { background: #e2e8f0 !important;}

.table-thumb { width: 45px; height: 60px; object-fit: cover; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.comment-text { font-style: italic; color: #475569; }

.btn-delete { background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85rem; font-weight: 500; transition: background 0.15s; }
.btn-delete:hover { background: #dc2626; }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
.stat-card { display: flex; align-items: center; gap: 20px; background: white; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; }
.stat-icon { font-size: 2rem; background: #f8fafc; padding: 8px; border-radius: 6px; }
.stat-info { display: flex; flex-direction: column; }
.stat-label { font-size: 1.0rem; color: #64748b; margin-bottom:5px;}
.stat-value { display: flex; justify-content:center;font-size: 1.6rem; font-weight: bold; color: #0f172a; }

.status-box { text-align: center; padding: 40px; background: #f8fafc; border-radius: 8px; font-weight: bold; }
.status-box.error { color: #ef4444; background: #fef2f2; }
.empty-msg { padding: 40px; color: #64748b; text-align: center; }
</style>