<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { isAuthenticated, token } from '../auth'

const route = useRoute()
const router = useRouter()
const BASE_URL = 'http://localhost:5000'

const userId = route.params.id
const userProfile = ref(null)
const isLoading = ref(true)
const errorMsg = ref('')

const fetchUserProfile = async () => {
  try {
    isLoading.value = true
    errorMsg.value = ''
    
    const config = token.value ? { headers: { Authorization: `Bearer ${token.value}` } } : {}
    
    //apelare ambele rute paralel
    const [booksRes, reviewsRes] = await Promise.all([
      axios.get(`${BASE_URL}/Book_Sharing/books/view-books/${userId}`, config),
      axios.get(`${BASE_URL}/Book_Sharing/reviews/view-reviews/${userId}`, config).catch(() => ({ data: { reviews: [], average_rating: 0 } }))
    ])
    
    
    userProfile.value = {
      name: booksRes.data.user?.name || "Utilizator",
      city: booksRes.data.user?.city || "Nespecificat",
      books: booksRes.data.books || [],
      reviews: reviewsRes.data.reviews || [],
      averageRating: reviewsRes.data.average_rating || 0
    }
  } catch (err) {
    console.error("Eroare la încărcarea profilului:", err)
    errorMsg.value = "Nu s-au putut încărca datele acestui utilizator."
  } finally {
    isLoading.value = false
  }
}

//trimitere cerere imprumut carte
const handleRequestBook = async (bookId, bookTitle) => {
  if (!isAuthenticated.value) {
    alert("Trebuie să fii logat pentru a cere o carte!")
    router.push('/login')
    return
  }
  
  if (confirm(`Vrei să trimiți o cerere de împrumut pentru "${bookTitle}"?`)) {
    try {
      const config = { headers: { Authorization: `Bearer ${token.value}` } }
      await axios.post(`${BASE_URL}/Book_Sharing/loans/request`, { book_id: bookId }, config)
      alert("Cererea a fost trimisă cu succes proprietarului!")
    } catch (err) {
      alert(err.response?.data?.error || "Eroare la trimiterea cererii.")
    }
  }
}

onMounted(() => {
  fetchUserProfile()
})
</script>

<template>
  <div class="profile-container">
    <button class="btn-back" @click="router.back()">⬅️ Înapoi</button>

    <div v-if="isLoading" class="loading-box">Se încarcă profilul utilizatorului...</div>
    
    <div v-else-if="errorMsg" class="error-box">⚠️ {{ errorMsg }}</div>

    <div v-else-if="userProfile">
      <header class="profile-header">
        <div class="avatar-dummy">👤</div>
        <div class="profile-main-info">
          <h1>{{ userProfile.name }}</h1>
          <p class="location">📍 Oraș: <strong>{{ userProfile.city }}</strong></p>
          <div class="rating-summary" v-if="userProfile.reviews.length > 0">
            <span class="stars">⭐ {{ userProfile.averageRating }} / 5</span> 
            <span class="total-rev">({{ userProfile.reviews.length }} recenzii)</span>
          </div>
          <div class="rating-summary no-reviews" v-else>
            <span>Nu are recenzii încă</span>
          </div>
        </div>
      </header>

      <div class="profile-grid">
        <section class="profile-section">
          <h2>⭐ Recenzii primite ({{ userProfile.reviews.length }})</h2>
          <div v-if="userProfile.reviews.length === 0" class="empty-msg">
            Nu există nicio recenzie pentru acest utilizator încă.
          </div>
          <ul v-else class="reviews-list">
            <li v-for="rev in userProfile.reviews" :key="rev.id" class="review-item">
              <div class="review-top">
                <span class="reviewer">👤 Recenzie #{{ rev.id }}</span>
                <span class="stars">{{ '⭐'.repeat(rev.rating) }}</span>
              </div>
              <p class="review-comment" v-if="rev.comment">„ {{ rev.comment }} ”</p>
              <small class="review-date" v-if="rev.created_at">{{ new Date(rev.created_at).toLocaleDateString() }}</small>
            </li>
          </ul>
        </section>

        <section class="profile-section">
          <h2>⭐ Recenzii primite ({{ userProfile.reviews?.length || 0 }})</h2>
          <div v-if="!userProfile.reviews || userProfile.reviews.length === 0" class="empty-msg">
            Nu există nicio recenzie pentru acest utilizator încă.
          </div>
          <ul v-else class="reviews-list">
            <li v-for="rev in userProfile.reviews" :key="rev.id" class="review-item">
              <div class="review-top">
                <span class="reviewer">👤 {{ rev.reviewer_name }}</span>
                <span class="stars">{{ '⭐'.repeat(rev.rating) }}</span>
              </div>
              <p class="review-comment" v-if="rev.comment">„ {{ rev.comment }} ”</p>
            </li>
          </ul>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-container { max-width: 1100px; margin: 40px auto; padding: 0 20px; font-family: sans-serif; }
.btn-back { background: #f4f6f8; border: 1px solid #ccc; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; margin-bottom: 20px; }
.btn-back:hover { background: #e2e6ea; }

.profile-header { display: flex; align-items: center; gap: 25px; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eee; margin-bottom: 30px; }
.avatar-dummy { font-size: 4rem; background: #eaedd0; padding: 10px 20px; border-radius: 50%; }
.profile-main-info h1 { margin: 0 0 5px 0; color: #2c3e50; }
.profile-main-info .location { margin: 0 0 10px 0; color: #7f8c8d; }
.role-badge { background: #e8f4fd; color: #1da1f2; padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; }

.profile-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 30px; }
@media (max-width: 800px) { .profile-grid { grid-template-columns: 1fr; } }

.profile-section { background: white; padding: 25px; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
.profile-section h2 { margin-top: 0; border-bottom: 2px solid #f4f6f8; padding-bottom: 12px; color: #34495e; font-size: 1.3rem; }

.books-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; margin-top: 15px; }
.profile-book-card { display: flex; gap: 12px; background: #fafbfc; padding: 12px; border-radius: 8px; border: 1px solid #e1e4e6; }
.book-card-img { width: 70px; height: 95px; object-fit: cover; border-radius: 4px; }
.book-card-details { display: flex; flex-direction: column; justify-content: space-between; flex: 1; }
.book-card-details h4 { margin: 0; color: #2c3e50; font-size: 0.95rem; }
.book-card-details .author { margin: 2px 0; font-size: 0.8rem; color: #7f8c8d; }

.badges-row { margin: 5px 0; display: flex; gap: 4px; flex-wrap: wrap; }
.badge { font-size: 0.7rem; padding: 2px 5px; border-radius: 4px; font-weight: bold; }
.badge.Disponibila { background-color: #e8f5e9; color: #2e7d32; }
.badge.Imprumutata { background-color: #ffebee; color: #c62828; }
.status-badge { background-color: #eaeaea; color: #555; }

.btn-request-book { background: #42b983; color: white; border: none; padding: 6px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; cursor: pointer; text-align: center; margin-top: auto; }
.btn-request-book:hover { background: #3aa876; }

.reviews-list { list-style: none; padding: 0; margin: 0; }
.review-item { padding: 15px 0; border-bottom: 1px solid #f4f6f8; }
.review-item:last-child { border-bottom: none; }
.review-top { display: flex; justify-content: space-between; margin-bottom: 5px; }
.reviewer { font-weight: bold; font-size: 0.9rem; color: #34495e; }
.stars { font-size: 0.85rem; }
.review-comment { margin: 0; font-style: italic; color: #555; font-size: 0.88rem; line-height: 1.4; }

.empty-msg { color: #95a5a6; font-style: italic; font-size: 0.9rem; margin-top: 15px; }
.loading-box, .error-box { text-align: center; padding: 40px; font-weight: bold; color: #7f8c8d; }
.error-box { color: #c62828; }

.rating-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 5px;
  font-weight: bold;
}
.total-rev {
  font-weight: normal;
  color: #7f8c8d;
  font-size: 0.85rem;
}
.no-reviews {
  color: #bdc3c7;
  font-size: 0.85rem;
  font-style: italic;
}
.review-date {
  font-size: 0.75rem;
  color: #95a5a6;
  display: block;
  margin-top: 5px;
}
</style>