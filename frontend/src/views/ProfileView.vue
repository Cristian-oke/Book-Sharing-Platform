<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { isAuthenticated, token } from '../auth'

const router = useRouter()
const BASE_URL = 'http://localhost:5000'

const userProfile = ref(null)
const isLoading = ref(true)
const errorMsg = ref('')

const currentUserId = computed(() => {
  if (!token.value) return null
  try {
    const base64Url = token.value.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
    }).join(''))
    const decoded = JSON.parse(jsonPayload)
    return decoded.sub ? parseInt(decoded.sub) : null
  } catch (error) {
    console.error("Eroare la decodificarea token-ului:", error)
    return null
  }
})

const fetchMyProfile = async () => {
  try {
    isLoading.value = true
    errorMsg.value = ''
    
    if (!isAuthenticated.value || !currentUserId.value) {
      errorMsg.value = "Trebuie să fii conectat pentru a-ți vedea profilul."
      return
    }

    const config = { headers: { Authorization: `Bearer ${token.value}` } }
    const myId = currentUserId.value

    const [booksRes, reviewsRes] = await Promise.all([
      axios.get(`${BASE_URL}/Book_Sharing/books/my-books`, config),
      axios.get(`${BASE_URL}/Book_Sharing/reviews/view-reviews/${myId}`, config).catch(() => ({ data: { reviews: [], average_rating: 0 } }))
    ])

    userProfile.value = {
      id: Number(booksRes.data.user?.id) || myId,
      name: booksRes.data.user?.name || "Utilizator",
      city: booksRes.data.user?.city || "Nespecificat",
      books: booksRes.data.books || [],
      reviews: reviewsRes.data.reviews || [],
      averageRating: reviewsRes.data.average_rating || 0
    }
  } catch (err) {
    errorMsg.value = "Nu s-au putut încărca datele profilului tău."
  } finally {
    isLoading.value = false
  }
}
onMounted(() => {
  if (isAuthenticated.value) {
    fetchMyProfile()
  }
})
</script>

<template>
  <div class="profile-container">
    
    <div v-if="!isAuthenticated" class="centered-auth-wrapper">
      <div class="simple-redirect-box">
        <h2>Nu ești autentificat</h2>
        <p>Trebuie să fii conectat pentru a avea acces la profilul tău.</p>
        <button class="btn-simple-connect" @click="router.push('/login')">
          Conectează-te
        </button>
      </div>
    </div>

    <div v-else>
      <div v-if="isLoading" class="loading-box">Se încarcă profilul tău...</div>
      <div v-else-if="errorMsg" class="error-box">⚠️ {{ errorMsg }}</div>

      <div v-else-if="userProfile">
        <header class="profile-header">
          <div class="avatar-dummy">👤</div>
          <div class="profile-main-info">
            <h1>{{ userProfile.name }}</h1>
            <p class="location">📍 Oraș: <strong>{{ userProfile.city }}</strong></p>
            <div class="rating-summary" v-if="userProfile.reviews.length > 0">
              <span class="stars">⭐ {{ userProfile.averageRating }} / 5</span> 
              <span class="total-rev">({{ userProfile.reviews.length }} recenzii primite)</span>
            </div>
            <div class="rating-summary no-reviews" v-else>
              <span>Nu ai primit recenzii încă</span>
            </div>
          </div>
        </header>

        <div class="profile-grid">
          
          <section class="profile-section">
            <h2>📚 Cărțile Mele ({{ userProfile.books?.length || 0 }})</h2>
            <div v-if="!userProfile.books || userProfile.books.length === 0" class="empty-msg">
              Nu ai nicio carte adăugată în bibliotecă.
            </div>
            <div v-else class="books-grid">
              <div v-for="book in userProfile.books" :key="book.id" class="profile-book-card">
                <div class="book-card-main-info">
                  <img :src="book.image_url || 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=150'" class="book-card-img" />
                  <div class="book-card-details">
                    <h4>{{ book.title }}</h4>
                    <p class="author">de {{ book.author }}</p>
                    <div class="badges-row">
                      <span class="badge" :class="book.availability === 'Disponibila' ? 'Disponibila' : 'Imprumutata'">
                        {{ book.availability === 'Disponibila' ? 'Disponibilă' : 'Indisponibilă' }}
                      </span>
                      <span class="badge status-badge">✨ {{ book.status }}</span>
                    </div>
                  </div>
                </div>

                <div class="book-card-actions">
                  <div class="own-book-profile-msg">
                    ℹ️ Această carte îți aparține
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section class="profile-section">
            <h2>⭐ Recenzii primite ({{ userProfile.reviews.length }})</h2>
            <div v-if="userProfile.reviews.length === 0" class="empty-msg">
              Nu ai primit nicio recenzie deocamdată.
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

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-container { max-width: 1100px; margin: 40px auto; padding: 0 20px; font-family: sans-serif; }
.centered-auth-wrapper { display: flex; justify-content: center; align-items: center; min-height: 50vh; }
.simple-redirect-box { width: 100%; max-width: 400px; background: white; padding: 35px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #eee; text-align: center; }
.simple-redirect-box h2 { margin-bottom: 10px; color: #2c3e50; }
.simple-redirect-box p { color: #7f8c8d; font-size: 0.95rem; margin-bottom: 25px; line-height: 1.5; }
.btn-simple-connect { width: 100%; padding: 12px; background-color: #42b983; color: white; border: none; font-weight: bold; border-radius: 6px; cursor: pointer; font-size: 1rem; transition: background 0.2s; }
.btn-simple-connect:hover { background-color: #35495e; }

.profile-header { display: flex; align-items: center; gap: 25px; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eee; margin-bottom: 30px; }
.avatar-dummy { font-size: 4rem; background: #e3f2fd; padding: 10px 20px; border-radius: 50%; }
.profile-main-info h1 { margin: 0 0 5px 0; color: #2c3e50; display: flex; align-items: center; gap: 10px; }
.own-profile-badge { font-size: 0.85rem; background: #e8f5e9; color: #2e7d32; padding: 3px 8px; border-radius: 12px; font-weight: bold; }
.profile-main-info .location { margin: 0 0 10px 0; color: #7f8c8d; }

.profile-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 30px; }
@media (max-width: 800px) { .profile-grid { grid-template-columns: 1fr; } }
.profile-section { background: white; padding: 25px; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
.profile-section h2 { margin-top: 0; border-bottom: 2px solid #f4f6f8; padding-bottom: 12px; color: #34495e; font-size: 1.3rem; }

.books-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; margin-top: 15px; }
.profile-book-card { display: flex; flex-direction: column; justify-content: space-between; background: #fafbfc; padding: 15px; border-radius: 8px; border: 1px solid #e1e4e6; gap: 12px; }
.book-card-main-info { display: flex; gap: 12px; }
.book-card-img { width: 65px; height: 90px; object-fit: cover; border-radius: 4px; }
.book-card-details { display: flex; flex-direction: column; justify-content: center; }
.book-card-details h4 { margin: 0; color: #2c3e50; font-size: 0.95rem; }
.book-card-details .author { margin: 2px 0; font-size: 0.8rem; color: #7f8c8d; }
.badges-row { margin: 5px 0; display: flex; gap: 4px; flex-wrap: wrap; }
.badge { font-size: 0.7rem; padding: 2px 5px; border-radius: 4px; font-weight: bold; }
.badge.Disponibila { background-color: #e8f5e9; color: #2e7d32; }
.badge.Imprumutata { background-color: #ffebee; color: #c62828; }
.status-badge { background-color: #eaeaea; color: #555; }

.own-book-profile-msg { width: 95%; text-align: center; padding: 5px; background-color: #ebf5fe; color: #1e88e5; font-size: 0.85rem; font-weight: bold; border-radius: 10px; border: 2px dashed #2196f3; }
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
.rating-summary { display: flex; align-items: center; gap: 8px; margin-top: 5px; font-weight: bold; }
.total-rev { font-weight: normal; color: #7f8c8d; font-size: 0.85rem; }
.no-reviews { color: #bdc3c7; font-size: 0.85rem; font-style: italic; }
.review-date { font-size: 0.75rem; color: #95a5a6; display: block; margin-top: 5px; }
</style>